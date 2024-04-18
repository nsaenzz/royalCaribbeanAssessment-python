
# Royal Caribbean Assessment

## About the project

Python Script to get timezone from timezonedb API

* Use List Time Zone to get the the timezones and populate table tzdb_timezones
* USe Get Time Zone to get the timezone details and populate tzdb_zone_details



<!-- GETTING STARTED -->
## Getting Started

### Prerequisites

1. Install the following packages:
    * python -m pip install requests
    * python -m pip install mysql-connector-python
    * python -m pip install urllib3
    * python -m pip install tqdm

2. Create the folling database according to instructions
    * tzdb_timezone
    * tzdb_zone_details
    * tzdb_error_log
    * staging_tzdb_zone_details (This is a stagging table same as tzdb_zone_details)

3. Rename config/config_demo.ini to config/config.ini

4. Enter your API in `config/config.ini`
   ```config
   apikey = 'ENTER_YOUR_API_KEY'
   ``` 

5. Enter your Database credential in `config/config.ini`
   ```config
    host = host
    user = user
    password = password
    database = database_name 
   ``` 



<!-- USAGE EXAMPLES -->
## Usage
Run Script: 'python rc_timezoneDB_API.py' and wait until it finish.
Go to the databae and verify the table if the data is there.
Check the error_log to see if were any error.

