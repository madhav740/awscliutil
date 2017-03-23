import sqlite3
import QueryConstructor
import Sync

def get_first_word_after_filter(text,filter_name):
    filter_val = text.split(filter_name)
    filter_parameters = list()
    i=1
    length = len(filter_val)
    if length >1:
        while(i<length):
            filter_parameters.append(filter_val[i].split()[0])
            i = i+1
    return filter_parameters

def run_query(query_text,configuration):
    query,query_type = QueryConstructor.construct_query(query_text,"ec2")
    connection = sqlite3.connect(configuration['db'])
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    if len(result) == 0 and query_type == "describe":
        Sync.populate_db_with_ec2_resources(query_text.split()[2])
        cursor.execute(query)
        result = cursor.fetchall()
    for items in result:
        res = "InstanceId : " +str(items[0]) + "\nInstanceName : " +str(items[3]) + "\nSystemtag : "+ str(items[5]) + "\nClienttag : " +str(items[4]) + "\nEnvtag : "+str(items[6]) + "\nPublicIp : " + str(items[1])+ "\nPrivateIp : " + str(items[2])+"\n"
        print res

