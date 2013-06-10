import hashlib
import socket

from default_settings import *

ENV = "prod"

#Service Settings
SERVICE = "apisvc"
SERVICE_PID_FILE = "/opt/tr/data/%s/pid/%s.%s.pid" % (SERVICE, SERVICE, ENV)
SERVICE_HOSTNAME = socket.gethostname()
SERVICE_FQDN = socket.gethostname()

#Thrift Server settings
THRIFT_SERVER_ADDRESS = socket.gethostname()
THRIFT_SERVER_INTERFACE = "0.0.0.0"
THRIFT_SERVER_PORT = 9099

#Database settings
DATABASE_HOST = "localhost"
DATABASE_NAME = "techresidents"
DATABASE_USERNAME = "techresidents"
DATABASE_PASSWORD = "t3chResident$"
DATABASE_CONNECTION = "postgresql+psycopg2://%s:%s@/%s?host=%s" % (DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME, DATABASE_HOST)
DATABASE_POOL_SIZE = 20

#Zookeeper settings
ZOOKEEPER_HOSTS = ["localhost:2181"]

#Mongrel settings
MONGREL_SENDER_ID = "apisvc_" + hashlib.md5(THRIFT_SERVER_ADDRESS+str(THRIFT_SERVER_PORT)).hexdigest()
MONGREL_PUB_ADDR = "tcp://localhost:9990"
MONGREL_PULL_ADDR = "tcp://localhost:9991"

#Riak settings
RIAK_HOST = "localhost"
RIAK_PORT = 8087
RIAK_SESSION_BUCKET = "tr_sessions"
RIAK_SESSION_POOL_SIZE = 4

#Twilio settings
TWILIO_ACCOUNT_SID = "AC4b7ade305aa88344e60c0289b60df1ce"
TWILIO_AUTH_TOKEN = "6cf8febae940693197025e6a8c041bfa"
TWILIO_APPLICATION_SID = "AP825c812d201347d68cbeeadec974543c"

#Rackspace CDN settings
CDN_URL = 'http://e76e4391c97b2f87b5c0-092292abadceda5fbd10b6de4be44b7f.r11.cf1.rackcdn.com'
CDN_SSL_URL = 'https://ca6ad98c8e86bf5d358c-092292abadceda5fbd10b6de4be44b7f.ssl.cf1.rackcdn.com'
CDN_STREAMING_URL = 'http://6dd2d3a4982fca439ed9-092292abadceda5fbd10b6de4be44b7f.r11.stream.cf1.rackcdn.com'

#Elastic Search settings
ES_ENDPOINT = 'http://localhost:9200'
ES_POOL_SIZE = 4

#Logging settings
LOGGING = {
    "version": 1,

    "formatters": {
        "brief_formatter": {
            "format": "%(levelname)s: %(message)s"
        },

        "long_formatter": {
            "format": "%(asctime)s %(levelname)s: %(name)s %(message)s"
        }
    },

    "handlers": {

        "console_handler": {
            "level": "ERROR",
            "class": "logging.StreamHandler",
            "formatter": "brief_formatter",
            "stream": "ext://sys.stdout"
        },

        "file_handler": {
            "level": "INFO",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "long_formatter",
            "filename": "/opt/tr/data/%s/logs/%s.%s.log" % (SERVICE, SERVICE, ENV),
            "when": "midnight",
            "interval": 1,
            "backupCount": 7
        }
    },
    
    "root": {
        "level": "INFO",
        "handlers": ["console_handler", "file_handler"]
    }
}

