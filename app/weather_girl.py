import os
import sys
import pathlib
import datetime as dt
import urllib.request, urllib.error
import json, gzip

from db_access import engine, dbmodel, format_SQLtable_name, table_exists, create_new_table, insert_into_table

def extract_json_data(jsonfilename):
    with gzip.GzipFile(jsonfilename, 'r') as fin:
        #print('enc', json.detect_encoding(fin.read()))
        data = [json.loads(line,encoding='utf-8') for line in fin.readlines()]
        #data = json.loads(fin.read().decode('utf-8'),encoding='utf-8')
    return data
def get_dict_from_json_gzip_http(record_fname):
    """
    retrieves stored gzipped file from S3  
    """
    try:
        with urllib.request.urlopen(record_fname) as jf_gz:
            with gzip.open(jf_gz, 'r') as jf:
                data = json.loads(jf.read(),encoding='utf-8') 
    #except urllib.error.HTTPError as err:
    except:
        data = None
    return data
def save_appconfig(filename, config):
    """
    helper for saving the app config
    inputs : 
    file: filename for saving the configuration
    config: configuration object
    
    returns:
    None
    """
    
    remote_link  = os.environ['WG_CONFIG_PATH']
    print('saving config to file:', remote_link)
    data_json = gzip.compress (json.dumps(config).encode('utf-8'))
    req = urllib.request.Request(url=remote_link, data=data_json,method='PUT')
    with urllib.request.urlopen(req) as f:
        pass
    return

    #data_json = json.dumps(config)
    #with gzip.GzipFile(jsonfilename, 'r') as fin
    #with open(filename,'w') as cfile:
    #    cfile.write(data_json)
    return

def load_appconfig(filename, config=None):
    """
    helper for loading the app config
    loads the dictionary from the file and updates a config, or creates new config
    inputs : 
    file: filename for saving the configuration
    config: configuration object
    
    returns:
    None
    """
    new_config = get_dict_from_json_gzip_http(filename)
    
    if type(config) == type(None):
            response = new_config
    else:
        config.update(new_config)
        response = None
    return response

def init_config_file(local_data_folder, config_path, count_limit=3):
    # setup the application configuration
    config = dict()
    
    DATA_STORE = local_data_folder # this will point to the folder in the compute server in the cloud
    cities_Fname = os.path.join(DATA_STORE, 'weather_14.json.gz') # where the list of cities for initialization is stored
    country_retireve = 'CZ' # download data for cities in this country

    config['DATA_STORE'] = DATA_STORE
    config['WG_REMOTE_DATA_STORE'] = os.environ['WG_REMOTE_DATA_STORE'] # this will point to the AWS S3 

    config['OPENWEATHER_ONECALL_URL'] = 'https://api.openweathermap.org/data/2.5/onecall?'
    config['OPENWEATHER_QUERY'] = {'lat':None,
                                      'lon':None,
                                      'units':'metric'}
    config['CITY_LIST'] = [item['city'] for item in extract_json_data(cities_Fname)] # list of cities, links to their records and retrieval status

    # configure retrieval of weather information (staticaly, for all CZ cities from the list)
    limit = count_limit # for testing purposes, download only 3 cities

    for city in config['CITY_LIST']:
        if (city['country'] == country_retireve) and (limit>=0):
            city['retrieve'] = True
            #city['retrieval_interval(s)'] = 3600
            limit -=1
            print(city['name'])
        else:
            city['retrieve'] = False

    # save the config in a json file
    save_appconfig(config_path,config)
    return

def get_city_latlon (city,country,city_list):
    lat=0
    lon=0
    for item in city_list:
            if item['country'] == country:
                if item['name'] == city:
                    city_found = True
                    lat=item['coord']['lat']
                    lon=item['coord']['lon']
                    break
    return (lat,lon)

def query_for_city(city,country,url,query_template,city_list):
    (lat, lon) = get_city_latlon(city,country,city_list)
    query_dict = {}
    query_dict['appid'] = os.environ['WG_QUERY_SECRET']
    for key in query_template:
        query_dict[key] = query_template[key]
        if key == 'lat':
            query_dict[key] = lat
        if key == 'lon':
            query_dict[key] = lon
    queryS = url+"&".join([('%s=%s'% (qid,val)) for (qid, val) in query_dict.items()])     
    return queryS


def retrieve_weather_info(queryS,local_data_folder='data'):
    local_filename, headers = urllib.request.urlretrieve(queryS,filename=(local_data_folder+'/temp.json'))
    return local_filename, headers

def store_new_record(data, headers,  appconfig):
    """
    write the data to new JSON file locally
    """
    remote_data_folder = appconfig['WG_REMOTE_DATA_STORE']
    remote_filename = headers['data_storage_link']
    storage_location = os.path.join(remote_data_folder,remote_filename)
                
    data_json = json.dumps(data) 
    with open(storage_location,'a') as wfile:
        wfile.writelines(data_json)
        wfile.write('\n')
    return
def store_new_record_http(data, headers,  appconfig):
    """
    PUT all the records to a server
    """
    http_server = appconfig['WG_REMOTE_DATA_STORE']
    remote_filename = headers['data_storage_link']
    remote_link  = urllib.parse.urljoin(http_server,remote_filename)
    print(remote_link)
    data_json = bytes (json.dumps(data),encoding='utf-8')
    req = urllib.request.Request(url=remote_link, data=data_json,method='PUT')
    with urllib.request.urlopen(req) as f:
        pass
    return
def retrieve_weather_info(queryS,local_data_folder='data'):
    local_filename, headers = urllib.request.urlretrieve(queryS,filename=(local_data_folder+'/temp.json'))
    return local_filename, headers
def retrieve_new_info(queryS,appconfig):
    # query the weather server
    local_data_folder = appconfig['DATA_STORE']
    temp_filename, headers = retrieve_weather_info(queryS,local_data_folder)
    # test the received info
    headers = dict(headers) #  metadata for the weather record for storage
    storageName=None
    if os.path.getsize(temp_filename) == int(headers['Content-Length']) : # check the file size, whether it was received fully
        timestampS = str(int(dt.datetime.timestamp(dt.datetime.now())))
        headers['timestamp'] = timestampS
    else:
        print('error occured : %s' %headers) # TODO some logging api
        temp_filename = None
    return headers, temp_filename
def retrieve_new_info_by_coord(coord_dict,appconfig):
    local_data_folder = appconfig['DATA_STORE'] # temporary file location
    # construct the API query
    new_query = appconfig['OPENWEATHER_QUERY'] # copy the API query template
    new_query['appid'] = os.environ['WG_QUERY_SECRET'] # insert the secret API key
    url = appconfig['OPENWEATHER_ONECALL_URL']
    new_query.update(coord_dict)
    queryS = url+"&".join([('%s=%s'% (qid,val)) for (qid, val) in new_query.items()]) 
    # query the weather server
    temp_filename, headers = retrieve_weather_info(queryS,local_data_folder)
    # test the received info
    headers = dict(headers) #  metadata for the weather record for storage
    storageName=None
    if os.path.getsize(temp_filename) == int(headers['Content-Length']) : # check the file size, whether it was received fully
        timestampS = str(int(dt.datetime.timestamp(dt.datetime.now())))
        headers['timestamp'] = timestampS
    else:
        print('error occured : %s' %headers) # TODO some logging api
        temp_filename = None
    return headers, temp_filename
def read_record_data (json_filename):
    # read the temp JSON file:
    with open(json_filename,'r') as fin:
        data = json.loads(fin.read(),encoding='utf-8') 
    return data

def storage_file_name (headers):
    timestampS = headers['timestamp']
    X_Cache_Key = headers['X-Cache-Key']
    remote_filename = 'weather-' + '_'.join(headers['X-Cache-Key'].split('?')[1].split('&')) + '_TS=' + timestampS + '.json'        
    return remote_filename


def format_SQLtable_name(coord,units='metric'):
    """
    format string from the input coordinates dictionary, that will be suitable as MySQL table name 
    """
    if coord['lat']<0:
        lat_str = ('S%.2f' % abs(coord['lat']))
    else: 
        lat_str = ('N%.2f' % abs(coord['lat']))
    if coord['lon']<0:
        lon_str = ('E%.2f' % abs(coord['lon']))
    else: 
        lon_str = ('W%.2f' % abs(coord['lon']))

    table_name = "_".join(('lat_%s_lon_%s_%s' % (lat_str,lon_str,units)).split('.'))
    return table_name

def dnl_weather_records (appconfig):
    for item in appconfig['CITY_LIST']:
        if item['retrieve']:
            headers, temp_filename = retrieve_new_info_by_coord (coord_dict=item['coord'],appconfig=appconfig)
            # read the temp JSON file:
            data = read_record_data(temp_filename)
            print(item['name'],item['coord'])
            timestampS = str(int(dt.datetime.timestamp(dt.datetime.now()))) # record query timestamp   
            headers['timestamp'] = timestampS          
            headers['data_storage_link'] = storage_file_name(headers) 
            
            # write the record to the database
            #table_name = format_SQLtable_name(item['coord'])
            if table_exists(engine,item['coord']):
                insert_into_table(engine,record=headers,coord=item['coord'])
            else:
                create_new_table(engine,record=headers,coord=item['coord'])
            store_new_record_http(data, headers, appconfig)
    return



