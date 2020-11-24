#sys.path.insert(0, str(pathlib.Path(__file__).parent))
from weather_girl import dnl_weather_records, save_appconfig, load_appconfig, init_config_file
import os

if __name__ == '__main__':
    # run the downloader script
    config = load_appconfig(os.environ['WG_CONFIG_PATH'])
    if config == None:
        # initialize the config file
        local_data_folder=os.environ['WG_LOCAL_DATA_STORE']
        config_path=os.environ['WG_CONFIG_PATH']
        init_config_file(local_data_folder, config_path, count_limit=60)
        config = load_appconfig(os.environ['WG_CONFIG_PATH'])
    dnl_weather_records(appconfig=config)
    #save_appconfig(os.environ['WG_CONFIG_PATH'],config)
    
    