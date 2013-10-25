import xadmin
from xadmin import views
from models import *
from xadmin.layout import *

from xadmin.plugins.inline import Inline
from xadmin.plugins.batch import BatchChangeAction

from project.models import City, Island, Project

xadmin.site.register(City)
xadmin.site.register(Island)
xadmin.site.register(Project)


