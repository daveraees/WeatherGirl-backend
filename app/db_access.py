from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
import pandas as pd
import os


aws_rds_endpoint = os.environ['WG_DATABASE_ENDPOINT']
aws_rds_port = os.environ['WG_DATABASE_PORT']
db_pw = os.environ['WG_DATABASE_PASS']
db_user = os.environ['WG_DATABASE_USER']
db_name = os.environ['WG_DATABASE_NAME']
engine = create_engine("mysql+pymysql://{user}:{pw}@{endpoint}:{port}/{db}"
                       .format(user=db_user,
                               pw=db_pw,
                               endpoint=aws_rds_endpoint,
                               db=db_name,
                               port=aws_rds_port,
                              ))

# database model

dbmodel = {
    'timestamp': String(10),            
    'Server': String(20), 
    'Date': String(33), 
    'Content-Type': String(50), 
    'Content-Length': String(12), 
    'Connection': String(10), 
    'X-Cache-Key': String(50), 
    'Access-Control-Allow-Origin': String(10), 
    'Access-Control-Allow-Credentials': String(10), 
    'Access-Control-Allow-Methods': String(10), 
    'data_storage_link': String(64)
}


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

def table_exists (engine,coord,units='metric'):
    """
    returns boolean value whether the table exists for given coordinates
    """
    table_name = format_SQLtable_name(coord,units)
    return engine.dialect.has_table(engine.connect(), table_name)

def create_new_table(engine,record,coord,units='metric'):
    table_name = format_SQLtable_name(coord,units)
    pd.DataFrame.from_dict( record,orient='index').T.set_index('timestamp').to_sql(table_name,engine,index=True,if_exists='replace',dtype=dbmodel)
    return


def insert_into_table(engine,record,coord,units='metric'):
    table_name = format_SQLtable_name(coord,units)
    pd.DataFrame.from_dict( record,orient='index').T.set_index('timestamp').to_sql(table_name,engine,index=True,if_exists='append',dtype=dbmodel)
    return

def fetch_records_table_for_coord(engine,coord,units='metric'):
    table_name = format_SQLtable_name(coord,units)
    response = None
    if  table_exists (engine,coord,units):
        query = ("SELECT * FROM %s;" % table_name)
        response = pd.read_sql(query,engine,index_col='timestamp')
    return response
