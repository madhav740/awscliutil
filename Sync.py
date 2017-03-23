import sqlite3
import boto
import boto.ec2
import Ec2Sync
import DbSync
def sync_data(configuration):
    Ec2Sync.sync(configuration)
    DbSync.sync(configuration)
