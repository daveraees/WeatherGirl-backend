# WeatherGirl-backend

Sample backend app that periodically downloads current weather information (including forecast) available form OpenWeatherMap.com. It is written in Python and uses Amazon Web Services (one S3 bucket and MySQL database hosted on RDS) cloud infrastructure.

## Function:
The app downloads the config file that contains list of locations of interest (cities) in JSON format. It then scans this list and determines which locations should the weather information be downloaded for, based on the boolean value of the "retrieve" field.  
The app then downloads the weather info for the locations of interest, and stores the metadata (query timestamp, current weather info filename) in MySQL database, and saves downloaded files to the S3 bucket. The weather information contains current weather information related to a specified geolocation (city, country). The application source code is ready for deployment in form of docker container.

## Pre-requisites:
* The app must have access to the respective services in AWS, namely the file storage service (S3 bucket) and the mysql database server.
    * access to the database is controled by MySQL username and password, via the database endpoint.
    * access to the S3 bucket via boto3 api
* The app needs an active API key for retrieving the weather infromation data from the [OpenWeatherMap.com](https://OpenWeatherMap.com). 
 
Another app [WeatherGirl-backend](https://github.com/daveraees/WeatherGirl-backend)  can be used to retrieve the weather info files from OpenWeatherMap and store the data files in the S3 bucket.
 
 
## Dependency requirements for running the server:

### libraries
- The app was tested and runs with python 3.7
- Libraries are specified in the file requirements.txt

### environment variables:
Before running the app locally from source code, or in a container, please make sure the following environmental variables are configured:

- WG_S3BUCKET_NAME=appbucket # name of the file storage  server S3 buckeet
- WG_CONFIG_PATH=path/to/config/wg_config.json.gz # this file must be accessible also to the backend app, that uses it to execute the weather info downloads
- WG_LOCAL_DATA_STORE=app/data # where small temporary file can be stored. No requirements for accessibility from other services
- WG_DATABASE_ENDPOINT=mysqlDB.example.com
- WG_DATABASE_USER=<mysql_read_write_access_username>
- WG_DATABASE_PASS=<mysql_password>
- WG_DATABASE_PORT: 3306
- WG_DATABASE_NAME: 'cities'
- WG_CITY_COUNT_LIMIT=60 # maximum number of cities that can be marked for download by the backend app.

## Usage:

running the web server locally from the source code in the root directory of the local git repository:

        $ python3 ./app/wg.py

The files docker-compose.yml and Dockerfile contain instructions needed to build a docker image.

## License:
The source code is released under the MIT license.


Author Information
------------------

The code was written by David Rais, see my other projects at [github.com/daveraees](https://github.com/daveraees)
