import sqlite3
import re

#parses query_text to get client system and env and name keywords
#
def get_filters_from_text(query_text):
    filter_to_parameter_map = dict()    
    position_list = list()
    filter_list =['client','system','env','name']
    for filters in filter_list:
        reg_ex = re.compile('\\b'+filters+'\\b')
        for a in list(reg_ex.finditer(query_text)):
            filter_to_parameter_map[filters] = query_text[a.end()+1:len(query_text)].split()[0].lstrip().split(',')
    return filter_to_parameter_map

#find whether user query is of type describe or list
def find_query_type(query_text):
    if query_text.split()[0] == "describe":
        return "describe"
    else:
        return "list"

#parses query text and converts into equivalent sqlite query
def construct_query(query_text,table):
    query_type = "list"
    if find_query_type(query_text) == "describe":
        query_type = "describe"
        query = "select * from "+table+" where instanceid like '%"+query_text.split()[2]+"%' ;"
        return query,query_type
    else:
        filter_to_parameter_map = get_filters_from_text(query_text)
        query_filter = ""
        filter_to_column_map = {'client':'clientag','system':'systemtag','env':'envtag','name':'nametag'}   
        for items in filter_to_parameter_map:
            if items == "name":
                query_filter = "nametag like '%"+filter_to_parameter_map[items][0]+"%'"
                query_filter += " AND"
            else:
                query_filter += filter_to_column_map[items] + " in ("
                for param in filter_to_parameter_map[items]:
                    query_filter += "'" +param + "',"
                query_filter = query_filter.rstrip(",")
                query_filter += ") AND "
        query_filter = query_filter.rstrip().rstrip('AND')  
        query = "select * from "+table+" where "+ query_filter + " ;"
        return query,query_type

        


        
"""
def get_filter_parameters(query_text,position_list):
    return query_text[pos+1,len(query_text)].split()[0].lstrip()
    
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
"""
#b= get_filters_from_text("list ec3 for system cm,sftp")
#print construct_query("list ec2 for system cm,sftp & for client staples,sears","ec2")  
