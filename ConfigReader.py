import os
from ConfigParser import SafeConfigParser
from ConfigParser import NoSectionError
import ConfigParser

def read_config():
    Config = ConfigParser.ConfigParser()
    Config.read("/Users/Achilles/.awsCliUtilResources/awsCliUtilConfig.ini")
    configuration = dict()
    configuration['db'] = Config.get('DbConfig','db_path')
    option_path = Config.get('AutoSuggestOptions','file_path')
    options_list = list()
    with open(option_path) as f:
        for line in f:
            options_list.append(line.rstrip("\n"))
    configuration['autosuggest'] = options_list
    return configuration
