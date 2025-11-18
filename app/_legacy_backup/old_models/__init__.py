"""
Aggregate all SQLAlchemy models so `from app import models` exposes them.

We import everything from each module to keep backward compatibility.
"""

from .academic import *     # noqa
from .audit import *        # noqa
from .school import *       # noqa
from .school_admin import * # noqa
from .timetable import *    # noqa
from .user import *         # noqa
from .parent import *       # noqa
