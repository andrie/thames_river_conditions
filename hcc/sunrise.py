
import pytz
import astral
from astral.sun import sun
from time import strftime
import pandas as pd


def sunrise_times():
    here = astral.Observer()

    s = sun(here, tzinfo = pytz.timezone("Europe/London"))

    events = pd.DataFrame({
        'event' : ['dawn', 'sunrise', 'sunset', 'dusk'],
        'time': [s['dawn'], s['sunrise'], s['sunset'], s['dusk']],
    })

    events['time'] = [strftime("%H:%M", t.timetuple()) for t in events['time']]
    return events