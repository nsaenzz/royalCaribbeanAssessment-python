from datetime import datetime
from requests.adapters import HTTPAdapter
import requests
import mysql.connector
import time
from urllib3.util import Retry
from tqdm import tqdm
from configparser import ConfigParser

config = ConfigParser()
config.read('config/config.ini')

#mysql connector
tzdb = mysql.connector.connect(
  host = config.get('database', 'host'),
  user = config.get('database', 'user'),
  password = config.get('database', 'password'),
  database = config.get('database', 'database')
)

#mysql cursor
cursonDb = tzdb.cursor()

# Retry strategy in case api call fails
retry_strategy = Retry(
    total=4,  # Maximum number of retries
    backoff_factor=2,  # Exponential backoff factor (e.g., 2 means 1, 2, 4, 8 seconds, ...)
    status_forcelist=[429, 500, 502, 503, 504],  # HTTP status codes to retry on
)

#adapter to add in the api session
adapter = HTTPAdapter(max_retries=retry_strategy)

url = '	http://api.timezonedb.com/v2.1/'
format = 'json'
apikey = config.get('auth', 'apikey')


def main():
    if populate_timezones():
        if populate_zone_details():
            print('Tables tzdb_timezones and tzdb_zone_details were successfully populated')
            if tzdb.is_connected():
                cursonDb.close()
                tzdb.close()
                print("MySQL connection is closed")
            return None
    print('There was an error when running the script. Please see the log table for more details')        
   
def populate_timezones():
    """
    Function to populate tzdb_timezones table
    :return: Boolean 
    """
    print('*** Start populating table tzdb_timezones ***')
    print('Please wait while the script is getting timezones from timezonedb.com')
    #http://api.timezonedb.com/v2.1/list-time-zone?key=YOUR_API_KEY&format=xml
    endpoint = url + 'list-time-zone?key=' + apikey + '&format=' + format
    # get timezones from the timezonedb api
    req = requests.get(endpoint)
    if req.status_code == 200:
        req = req.json()
        if req['status'] == 'OK':
            try:
                # Delete tzdb_timezones data
                cursonDb.execute("TRUNCATE TABLE tzdb_timezones")
            except mysql.connector.Error as e:
                print('There was an error when trying to truncate timeszones table: ' + e)
                save_error_log(e)
                return None    

            values = []
            #Prepare timezone api data to import it into the tzdb_timezones table
            for data in tqdm(req['zones'], desc='Preparing timezones'):
                now = datetime.now()
                formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
                values.append((
                    data['countryCode'],
                    data['countryName'],
                    data['zoneName'],
                    data['gmtOffset'],
                    formatted_date
                ))
            print('Saving timezone into the tzdb_timezones table')
            #insert data in tzdb_timezones table
            sql = 'INSERT INTO tzdb_timezones (country_code, country_name, zone_name, gmt_offset, import_date) '\
                        'VALUES (%s, %s, %s, %s, %s)' 
            try:    
                cursonDb.executemany(sql, values)
                tzdb.commit()
            except mysql.connector.Error as e:
                print('There was an error when trying to populate timeszones: {}'.format(e))
                save_error_log(e)
                return False
        else:
            print('There was an error: ' + req['message'])
            save_error_log(req['message'])
            return False
        print('Timezones were saved successfully')
        print('*** End populating table tzdb_timezones ***')
        return True
    else:
        print('Request Error Status on list-time-zone: ' + str(req.status_code))
        save_error_log('Request return status code on list-time-zone ' + str(req.status_code))
        return False
        
    
def populate_zone_details():
    """
    Function to populate tzdb_zone_details table
    :return: Boolean 
    """
    
    print('*** Start populating table tzdb_zone_details ***')
    print('Please wait while the script is getting timezone details from timezonedb.com')
    
    #Get all timezones from tzdb_timezones table
    cursonDb.execute("SELECT zone_name FROM tzdb_timezones")
    zoneNames = cursonDb.fetchall()
    #error counter
    errors = 0
    #if there any zoneName available
    if len(zoneNames):
        #for loop the zoneNames to get the details from timezonedb API
        for zoneName in tqdm(zoneNames, desc='Preparing timezone details'):
            #http://api.timezonedb.com/v2.1/get-time-zone?key=YOUR_API_KEY&format=xml&by=zone&zone=America/Chicago
            #Free timezonedb API has a limit of 1 request per second after timezonedd send a request 
            time.sleep(1.25)
            endpoint = url + 'get-time-zone?key=' + apikey + '&format=' + format + '&by=zone&zone=' + zoneName[0]
            """
                Create an Session in case the API call fails the apater retry to get the information 
                again accordingly to the retry stragegy 
            """
            s = requests.Session()
            s.mount('http://', adapter)
            req = s.get(endpoint)
            if req.status_code == 200:
                data = req.json()
                sql = "SELECT * FROM tzdb_zone_details WHERE zone_name = '{}'"\
                        "and zone_start = '{}' and zone_end = '{}'".format(data['zoneName'], data['zoneStart'], data['zoneEnd'])
                cursonDb.execute(sql)
                zone_detail = cursonDb.fetchall()
                #if this timezone doesn't exit in tzdb_zone_details table, the application get the detail from the API
                if not len(zone_detail):
                    now = datetime.now()
                    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
                    val = (
                        data['countryCode'],
                        data['countryName'],
                        data['zoneName'],
                        data['gmtOffset'],
                        data['dst'],
                        data['zoneStart'],
                        data['zoneEnd'],
                        formatted_date
                    )
                    #insert data api into the staging table staging_tzdb_zone_details to verify if the data is correct
                    sql = 'INSERT INTO staging_tzdb_zone_details '\
                        '(country_code, country_name, zone_name, gmt_offset, dst, zone_start, zone_end, import_date) '\
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)' 
                    try:    
                        cursonDb.execute(sql, val)
                        tzdb.commit()
                    except mysql.connector.Error as e:
                        save_error_log("Error with timezone {}: {}".format(zoneName[0], e))
                        errors += 1
                        continue
                else:
                    save_error_log('Request Error Status on get-time-zone {}: {}'.format(zoneName[0], req.status_code))
                    errors += 1
                    continue
                
        print('Saving timezone detail into tzdb_zone_details table')
        #Get all the data from staging and import it into tzdb_zone_details table
        cursonDb.execute("SELECT * FROM staging_tzdb_zone_details")
        zoneDetails = cursonDb.fetchall()
        sql = 'INSERT INTO tzdb_zone_details '\
            '(country_code, country_name, zone_name, gmt_offset, dst, zone_start, zone_end, import_date) '\
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)' 
        try:    
            cursonDb.executemany(sql, zoneDetails)
            tzdb.commit()
        except mysql.connector.Error as e:
            print('There was an error when trying to populate tzdb_zone_details table: {}'.format(e))
            save_error_log('There was an error when trying to populate tzdb_zone_details table: {}'.format(e))
            return False
        finally:
            print('Deleting data from stagging table')
            cursonDb.execute("TRUNCATE TABLE staging_tzdb_zone_details")
            tzdb.commit()
        print('*** End populating table tzdb_zone_details ***')
    else:
        print('No data found in table tzdb_timezones')
        save_error_log('No data found in table tzdb_timezones')
        return False
    
    if errors:
        print('Timezone details were saved with {} error(s). Please check log for more detail'.format(errors))
    else:
        print('Timezones details were save successfully')
    return True
    
def save_error_log(error_message):
    """
    Function to log the error into tzdb_error_log table
    """
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    cursonDb = tzdb.cursor()
    sql = 'INSERT INTO tzdb_error_log (error_date, error_message) '\
                'VALUES (%s, %s)'
    val = (formatted_date, str(error_message))
    cursonDb.execute(sql, val)
    tzdb.commit()
    cursonDb.close()

if __name__ == '__main__':
    main()

