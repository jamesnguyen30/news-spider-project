from mongoengine import connect, disconnect
import pathlib
import os

#Params for parsing db config
CWD = pathlib.Path(__file__).parent.absolute()
CONFIG_FILE =  os.path.join(CWD, 'db.config')


def init_db(alias, name):
    connect(alias = alias, name = name)

def disconnect_db():
    disconnect()
