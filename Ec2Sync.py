import sqlite3
import boto
import boto.ec2
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

def get_all_ec2_instances_regionwise(regions_list):
    ec2_to_region_map=list()
    for regions in regions_list:
        connection= boto.ec2.connect_to_region(regions)
        reservations = connection.get_all_instances()
        for reservation in reservations:
            for instance in reservation.instances:
                if instance.state == "running":
                    ec2_to_region_map.append(instance)
        connection.close()
    return ec2_to_region_map

#this function has hard coded region 
def get_ec2_instance_from_id(instance_id):
    connection= boto.ec2.connect_to_region("us-west-2")
    reservations = connection.get_all_instances(instance_ids=[instance_id])
    instance = reservations[0].instances[0]
    if instance:
        return [instance]
    else:
        return []



def populate_db_with_ec2_resources(configuration,resource=None):
    regions_list = ['us-west-2']
    ec2_to_region_map = list()
    if resource != None :
        ec2_to_region_map = get_ec2_instance_from_id(resource)
    else:
        ec2_to_region_map = get_all_ec2_instances_regionwise(regions_list)
    connection = create_connection(configuration)
    create_table_query = 'create table ec2 (instanceid VARCHAR(10) PRIMARY KEY NOT NULL, publicip VARCHAR(20), privateip VARCHAR(100), nametag VARCHAR(100), clientag VARCHAR(100), systemtag VARCHAR(50), envtag VARCHAR(50),owntag VARCHAR(50))'
    try:
        connection.execute(create_table_query)
        #execute_query(connection,create_table_query,"ddl")
    except Exception,e:
        s=1
        #print "table already exists"+str(e)
    for items in ec2_to_region_map:
        tagset=items.tags
        instance_name_tag = ""
        instance_own_tag = ""
        instance_system_tag = ""
        instance_client_tag = ""
        instance_env_tag = ""
        is_spot = False
        if "Name" in tagset.keys():
            instance_name_tag = tagset['Name']
        if "own" in tagset.keys():
            instance_own_tag = tagset['own']
        if "system" in tagset.keys():
            instance_system_tag = tagset['system']
        if "client" in tagset.keys():
            instance_client_tag = tagset['client']
        if "env" in tagset.keys():
            instance_env_tag = tagset['env']
        #if items.instanceLifecycle == "spot":
        is_spot = True
        connection.execute("insert OR IGNORE into ec2 VALUES (?,?,?,?,?,?,?,?);",(items.id,items.ip_address,items.private_ip_address,instance_name_tag,instance_client_tag,instance_system_tag,instance_env_tag,instance_own_tag)) 
    connection.commit()
    connection.close()

def sync(configuration):
    print "\nWAIT WHILE SYNC IS IN PROGRESS\n"
    populate_db_with_ec2_resources(configuration)
    print "SYNCING DONE"
