import cProfile
import pstats
import StringIO
from functools import wraps


def setProfile(f):
    @wraps(f)
    def new_f(*args, **kwargs):
        pr = cProfile.Profile(subcalls=False, builtins=False)
        pr.enable()
        return_value = f(*args, **kwargs)
        pr.disable()
        s = StringIO.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        return return_value
    return new_f
