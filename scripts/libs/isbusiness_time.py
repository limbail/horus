from datetime import datetime as dt
from pytz import timezone

def _isbusiness_time(start,end):

    start=dt.strptime(start, '%H:%M:%S')
    end=dt.strptime(end, '%H:%M:%S')

    try:
        tz = timezone('Europe/Madrid')
        timeNow = dt.now(tz)
        if start.time() < timeNow.time() < end.time():
            if timeNow.isoweekday() in range(1,8):
                print("business hours, continue...")
                return True
        else:
            print("Not business hours, stop here...")
            return False
    except:
        raise
        print("Something was wrong...")