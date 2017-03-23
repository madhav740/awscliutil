import sqlite3
import boto
import boto.rds2
import boto.rds
import subprocess
def create_connection(configuration):
    connection = sqlite3.connect(configuration['db'])
    return connection
def execute_query(connection,query,query_type="dml"):
    query_result = None
    if query_type == "ddl":
        connection.execute(query)
        connection.commit()
    else:
        cursor = connection.cursor()
        cursor.execute(query)
        query_result = list(cursor.fetchall())
    return query_result

def get_all_rds_instances_regionwise(regions_list):
    rds_to_region_map = list()
    for regions in regions_list:
        connection = boto.rds.connect_to_region(regions)
        rds_list=connection.get_all_dbinstances()
        connection.close()
        for rds in rds_list:
            rds_to_region_map.append(rds)
    return rds_to_region_map

def get_tags(rds,region,connection):
    tagset=dict()
    tagsetlist = connection.list_tags_for_resource("arn:aws:rds:"+region+":208876916689:db:"+rds.id)['ListTagsForResourceResponse']['ListTagsForResourceResult']['TagList']
    for items in tagsetlist:
        print items 
        tagset[items['Key']]= items['Value']
    return tagset   


def populate_db_with_rds_resources(configuration):
    regions_list = ['us-west-2']
    rds_to_region_map = get_all_rds_instances_regionwise(regions_list)
    connection = create_connection(configuration)
    aws_connection = boto.rds2.connect_to_region("us-west-2")
    create_table_query = 'create table rds (dbname VARCHAR(10) PRIMARY KEY NOT NULL, rdsendpoint VARCHAR(20), clientag VARCHAR(100), systemtag VARCHAR(50), envtag VARCHAR(50),owntag VARCHAR(50),dbsize INT(10))'
    try:
        connection.execute(create_table_query)
    except Exception,e:
        s=1
        #print "table already exists"+str(e)
    for items in rds_to_region_map:
        tagset = get_tags(items,"us-west-2",aws_connection) 
        instance_name_tag = ""
        instance_own_tag = ""
        instance_system_tag = ""
        instance_client_tag = ""
        instance_env_tag = ""
        if "own" in tagset.keys():
            instance_own_tag = tagset['own']
        if "system" in tagset.keys():
            instance_system_tag = tagset['system']
        if "client" in tagset.keys():
            instance_client_tag = tagset['client']
        if "env" in tagset.keys():
            instance_env_tag = tagset['env']
        #if items.instanceLifecycle == "spot":
        connection.execute("insert OR IGNORE into rds VALUES(?,?,?,?,?,?,?);",(items.id,items.endpoint[0],instance_client_tag,instance_system_tag,instance_env_tag,instance_own_tag,items.allocated_storage)) 
    connection.commit()
    connection.close()

def sync(configuration):
    print "\nWAIT WHILE SYNC IS IN PROGRESS\n"
    populate_db_with_rds_resources(configuration)
    print "SYNCING DONE"
