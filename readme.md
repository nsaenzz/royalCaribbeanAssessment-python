
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

2. Create a new MySql schema for your database

3. Create tables:
    * In your database schema, open a new query
    * Open database/database.sql
    * copy the file and paste it in the new query
    * Run the query 

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
* Run Script: 'python rc_timezoneDB_API.py' and wait until it finish.
* Go to the databae and verify the table if the data is there.
* Check the errors in the tzdb_error_log table.

