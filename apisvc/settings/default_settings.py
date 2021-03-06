import hashlib
import os
import socket

ENV = os.getenv("SERVICE_ENV", "default")

#Service Settings
SERVICE = "apisvc"
SERVICE_PID_FILE = "%s.%s.pid" % (SERVICE, ENV)
SERVICE_HOSTNAME = socket.gethostname()
SERVICE_FQDN = socket.gethostname()

#Thrift Server settings
THRIFT_SERVER_ADDRESS = socket.gethostname()
THRIFT_SERVER_INTERFACE = "0.0.0.0"
THRIFT_SERVER_PORT = 9099

#Database settings
DATABASE_HOST = "localdev"
DATABASE_NAME = "localdev_techresidents"
DATABASE_USERNAME = "techresidents"
DATABASE_PASSWORD = "techresidents"
DATABASE_CONNECTION = "postgresql+psycopg2://%s:%s@/%s?host=%s" % (DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_NAME, DATABASE_HOST)
DATABASE_POOL_SIZE = 20

#Zookeeper settings
ZOOKEEPER_HOSTS = ["localdev:2181"]

#Mongrel settings
MONGREL_SENDER_ID = "apisvc_" + hashlib.md5(THRIFT_SERVER_ADDRESS+str(THRIFT_SERVER_PORT)).hexdigest()
MONGREL_PUB_ADDR = "tcp://localdev:9990"
MONGREL_PULL_ADDR = "tcp://localdev:9991"

#Riak settings
RIAK_HOST = "localdev"
RIAK_PORT = 8087
RIAK_SESSION_BUCKET = "tr_sessions"
RIAK_SESSION_POOL_SIZE = 4

#Rackspace CDN settings
CDN_URL = 'http://c41747272913390b5be0-2f317612417b37502ddedebdeb21ff41.r21.cf1.rackcdn.com'
CDN_SSL_URL = 'https://cea2664df6532c394770-2f317612417b37502ddedebdeb21ff41.ssl.cf1.rackcdn.com'
CDN_STREAMING_URL = 'http://fb45a9b6d35ebef42d2b-2f317612417b37502ddedebdeb21ff41.r21.stream.cf1.rackcdn.com'

#Elastic Search settings
ES_ENDPOINT = 'http://localdev:9200'
ES_POOL_SIZE = 4

#Twilio settings
TWILIO_ACCOUNT_SID = "AC339bd35c385747713117ec475787c1f7"
TWILIO_AUTH_TOKEN = "38ecd9a4310677ac69b575cd8f724d31"
TWILIO_APPLICATION_SID = "AP1672ddc9ec844ae9b0274a63262ccb4d"

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
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "brief_formatter",
            "stream": "ext://sys.stdout"
        },

        "file_handler": {
            "level": "DEBUG",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "long_formatter",
            "filename": "%s.%s.log" % (SERVICE, ENV),
            "when": "midnight",
            "interval": 1,
            "backupCount": 7
        }
    },
    
    "root": {
        "level": "DEBUG",
        "handlers": ["console_handler", "file_handler"]
    }
}
