from peewee import *
from os import getenv


db = MySQLDatabase(database=getenv('DATABASE', ''),
                            host=getenv('HOST', ''),
                            port=int(getenv('PORTS', '')),
                            user=getenv('USER', ''),
                            password=getenv('PASSWORD', ''),
                   ssl={'ca': 'ca.pem'})


