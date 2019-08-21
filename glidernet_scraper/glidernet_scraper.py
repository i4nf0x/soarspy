#!/usr/bin/python3.6
import calendar
import sqlite3
from ogn.client import AprsClient
from ogn.parser import parse, ParseError
import datetime
import calendar

# Fix data from old version:
#
# create table positions_old as select * from positions;
# create table positions (id integer primary key autoincrement, address text, timestamp INTEGER, reference_timestamp INTEGER, latitude REAL, longitude REAL, climbrate REAL, turnrate REAL, groundspeed REAL, altitude REAL);
# insert into positions select null, callsign, timestamp+2*60*60, reference_timestamp+2*60*60, latitude, longitude, climbrate, turnrate, groundspeed, altitude from positions_old;
# drop table positions_old;
# vacuum;


db=None 
last_db_name=None
commit_counter = 0

def process_beacon(raw_message):
    global db
    db_check_connect()
    try:
        beacon = parse(raw_message)
        if beacon['aprs_type']=='position' and beacon['beacon_type']=='aprs_aircraft':
            beacon['timestamp'] = calendar.timegm(beacon['timestamp'].timetuple())
            beacon['reference_timestamp'] = calendar.timegm(beacon['reference_timestamp'].timetuple())

            print(beacon)
            db.execute("INSERT INTO positions VALUES (null, :name, :timestamp, :reference_timestamp, :latitude, :longitude, :climb_rate, :turn_rate, :ground_speed, :altitude)", beacon)
            db_commit()

    except Exception as e:
        print('Error, {}'.format(e))

def db_check_connect():
    global db, last_db_name
    new_db_name = datetime.datetime.now().strftime("gliderdata-%Y-%m-%d.db")

    if new_db_name != last_db_name:
        if db!=None:
            print("New day, opening new database "+new_db_name)
            db.commit()
            db.close()
        db = db_init(new_db_name)
        last_db_name = new_db_name

def db_init(name):
    db = sqlite3.connect(name)
    db.execute("CREATE TABLE IF NOT EXISTS positions (id INTEGER PRIMARY KEY AUTOINCREMENT, address TEXT, timestamp INTEGER, reference_timestamp INTEGER, latitude REAL, longitude REAL, climbrate REAL, turnrate REAL, groundspeed REAL, altitude REAL)")
    db.execute("PRAGMA JOURNAL_MODE=WAL")
    return db

def db_commit():
    global commit_counter, db
    commit_counter+=1
    if commit_counter%100==0:
        print("Commiting DB...")
        db.commit()


db_check_connect()

client = AprsClient(aprs_user='N0CALL', aprs_filter='r/49.856/15.490/300.0')
client.connect()

try:
    client.run(callback=process_beacon, autoreconnect=True)

except KeyboardInterrupt:
    print('\nStop glidernet scraper')
    db.commit()
    db.close()
    client.disconnect()


