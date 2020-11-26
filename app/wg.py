import os
import boto3
#sys.path.insert(0, str(pathlib.Path(__file__).parent))
from weather_girl import dnl_weather_records, save_appconfig, load_appconfig, init_config_file


if __name__ == '__main__':
    # run the downloader script
    # Let's use Amazon S3
    s3engine = boto3.client('s3')
    config = load_appconfig(s3engine,os.environ['WG_CONFIG_PATH'])
    if config == None:
        # initialize the config file
        local_data_folder=os.environ['WG_LOCAL_DATA_STORE']
        config_path=os.environ['WG_CONFIG_PATH']
        init_config_file(s3engine,local_data_folder, config_path, count_limit=int(os.environ['WG_CITY_COUNT_LIMIT']))
        config = load_appconfig(s3engine,os.environ['WG_CONFIG_PATH'])
    dnl_weather_records(s3engine,appconfig=config)
    #save_appconfig(os.environ['WG_CONFIG_PATH'],config)
    
    