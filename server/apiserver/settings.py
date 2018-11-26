from eve_sqlalchemy.config import DomainConfig, ResourceConfig
from mmdps.dms.tables import Person, MRIScan, MotionScore, StrokeScore, Group, MRIMachine
from mmdps import rootconfig


DEBUG = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///F:/geyunxiang/mmdps_git/server/apiserver/mmdpdb.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
RESOURCE_METHODS = ['GET', 'POST']

# pagination
PAGINATION = False

# datetime
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

#SQLALCHEMY_ECHO = True
#SQLALCHEMY_RECORD_QUERIES = True

DOMAIN = DomainConfig({
    'people': ResourceConfig(Person),
    'mriscans': ResourceConfig(MRIScan),
    'motionscores': ResourceConfig(MotionScore),
    'strokescores': ResourceConfig(StrokeScore),
    'groups': ResourceConfig(Group),
    'mrinachines': ResourceConfig(MRIMachine)
}).render()

# custom settings
MY_STORAGE_URLBASE = rootconfig.server.storage
MY_STORAGE_AUTH = ('mmdpdata', '123')

MY_FEATURE_STORAGE_URLBASE = rootconfig.server.featurestorage
MY_FEATURE_STORAGE_AUTH = ('mmdpdata', '123')
MY_FEATURE_ROOT = 'ChangGungFeatures'
