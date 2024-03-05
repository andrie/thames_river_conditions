__version__ = '0.1.0'
from .core import find_local
from .core import plot_thames_level, lookup_thames_station_name, get_thames_metric
from .scrape import scrape_conditions, scrape_river_closures
from .sunrise import sunrise_times
# from .earivers import get_stations, get_measures, get_readings_for_measure, get_ea_measures

from . import ea_rivers