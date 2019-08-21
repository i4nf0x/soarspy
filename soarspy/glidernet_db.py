from datetime import date,datetime
from typing import Sequence
import os.path
import sqlite3
import glob
from dateutil import tz


class GlidernetDb():
    def __init__(self, db):
        self.db = db

    def get_airplanes(self) -> Sequence[sqlite3.Row]:
        c = self.db.execute("select address, max(altitude) as max_qnh, "
                            "min(reference_timestamp) as 'first_seen [epoch]', "
                            "max(reference_timestamp) as 'last_seen [epoch]'"
                            "from positions group by address order by min(reference_timestamp) asc")
        return c.fetchall()


def list_flight_days() -> Sequence[str]:
    day_files = glob.glob("data/gliderdata-*.db")
    return list(map(lambda d: os.path.basename(d).replace('gliderdata-', '').replace('.db',''), day_files))


def load_flight_day(daystr: str) -> GlidernetDb:
    filename = "data/gliderdata-"+daystr+".db"
    if os.path.exists(filename):
        db = sqlite3.connect(filename, detect_types=sqlite3.PARSE_COLNAMES)
        sqlite3.register_converter('epoch', lambda a: datetime.fromtimestamp(int(a), tz.tzlocal()))
        db.row_factory = sqlite3.Row
        return GlidernetDb(db)


