import os
import sys
import time
import datetime
import qbittorrentapi

import logging
from colorlog import ColoredFormatter

###########################################
# Process environment variables
###########################################
# Set all values that are set via the environment
QBITTORRENT_URL = os.environ['QBITTORRENT_URL']
QBITTORRENT_PORT_NUMBER = os.environ['QBITTORRENT_PORT_NUMBER']
QBITTORRENT_USERNAME = os.environ['QBITTORRENT_USERNAME']
QBITTORRENT_PASSWORD = os.environ['QBITTORRENT_PASSWORD']
WATCH_INTERVAL =  int(os.environ.get('UPDATE_INTERVAL', '300')) # Default 5 mins
VPN_DATA_FILEPATH = os.environ.get('VPN_DATA_FILEPATH', '/vpn-data/port.dat')
STARTUP_DELAY =  int(os.environ.get('STARTUP_DELAY', '0')) # Default 0 secs

# Validate that all required environment variables are set
required_vars = {
    "QBITTORRENT_URL": QBITTORRENT_URL,
    "QBITTORRENT_PORT_NUMBER": QBITTORRENT_PORT_NUMBER,
    "QBITTORRENT_USERNAME": QBITTORRENT_USERNAME,
    "QBITTORRENT_PASSWORD": QBITTORRENT_PASSWORD
}
missing_vars = [key for key, value in required_vars.items() if not value]
if missing_vars:
    print(f"Error: Missing required environment variables: {missing_vars}")
    sys.exit(1)

# Determine the log level to be used, the default will be INFO
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
if LOG_LEVEL not in ['DEBUG','INFO','WARNING','ERROR','CRITICAL']:
    LOG_LEVEL = 'INFO'

###########################################
# Setup Logging
###########################################
# Create a logger
#logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger()
loglevel = logging.getLevelName(LOG_LEVEL)
logger.setLevel(loglevel)

# Create formatter and add it to the handler
formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s [%(levelname)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S',
    reset=True,
    log_colors={
        'DEBUG':    'light_black',
        'INFO':     'white',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)

# Create a stream handler for formatting, and initiate the format
handler = logging.StreamHandler()
handler.setFormatter(formatter)
# Add the handler to the logger
logger.addHandler(handler)

# Configure the logging level for qbittorrent-api
logging.getLogger('qbittorrentapi').setLevel(logging.ERROR)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def splashLogo():
    """
    Print the splash screen to the logs
    """
    logging.info(f'''
 _____                                                          _____ 
( ___ )                                                        ( ___ )
 |   |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|   | 
 |   |                                                          |   | 
 |   |   ████████╗██╗   ██╗███████╗███████╗███╗   ██╗ █████╗    |   | 
 |   |   ╚══██╔══╝╚██╗ ██╔╝╚══███╔╝██╔════╝████╗  ██║██╔══██╗   |   | 
 |   |      ██║    ╚████╔╝   ███╔╝ █████╗  ██╔██╗ ██║╚██████║   |   | 
 |   |      ██║     ╚██╔╝   ███╔╝  ██╔══╝  ██║╚██╗██║ ╚═══██║   |   | 
 |   |      ██║      ██║   ███████╗███████╗██║ ╚████║ █████╔╝   |   | 
 |   |      ╚═╝      ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═══╝ ╚════╝    |   | 
 |   |                https://github.com/tyzen9                 |   | 
 |   |                    Made in the U.S.A.                    |   | 
 |___|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|___| 
(_____)                                                        (_____)

''')

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getPortNumber():
    """
    Read the first line of the specified VPN port number file.  Convert this value
    to an integer and return it.  On failure, return zero (0)

    Returns
    -------
    int
        The new port number, or zero (0) if there was an error parsing the file
    """
    __returnValue = 0
    # On any exception, zero will be returned
    try:
        # Open the file, read the first line, and close the file
        file = open(VPN_DATA_FILEPATH, 'r')
        first_line = file.readline()
        file.close()
        # Convert the port number into an integer
        __returnValue = int(first_line.strip())
    except Exception as e:
        print (f'{Fore.RED}Error:  Unable to read port number from {VPN_DATA_FILEPATH}{Fore.RESET}')
        print (f'\t{e}')
    return(__returnValue)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main(): 
    __qbtPortNumber = None
    __qbtConnectionValidated = False

    # Set the qBittorrent WEB API connection values
    conn_info = dict(
        host=QBITTORRENT_URL,
        port=QBITTORRENT_PORT_NUMBER,
        username=QBITTORRENT_USERNAME,
        password=QBITTORRENT_PASSWORD,
    )

    if (STARTUP_DELAY > 0):
        logging.info(f'please wait {STARTUP_DELAY} seconds...')
        time.sleep(STARTUP_DELAY)

    # Instantiate a qBittorrent WEB API Client using the appropriate WebUI configuration
    qbt_client = qbittorrentapi.Client(**conn_info)

    # Keep trying to connect to qBittorrent until we make a successful connection
    while __qbtConnectionValidated == False:
        # First lets make sure we can connect to the qBittorrent API by just logging in/out
        try:
            logging.info(f'Validate qBittorrent WEB API connection at {QBITTORRENT_URL}:{QBITTORRENT_PORT_NUMBER}')
            qbt_client.auth_log_in()
            qbt_client.auth_log_out()
            logging.info(f'\t✅  Validated')
            __qbtConnectionValidated = True
        except Exception as e:
            logging.error (f'Error:  qBittorrent Web API Login Failure')
            logging.error ('**********************************************************************')
            logging.error (f'Please make sure qBittorrent is running at {QBITTORRENT_URL}:{QBITTORRENT_PORT_NUMBER}\n')
            logging.error ('If this is the first time the qBittorrent container is being run, then')
            logging.error ('check its output log for the admin users\'s temporary password.  Update')
            logging.error ('the qBittorrent admin password using the qBittorrent web interface to')
            logging.error ('match the password specified in this application, and restart.')
            logging.error ('**********************************************************************')
            logging.error ('Exception Details:')
            logging.error (f'{e}\n')
            logging.error ('Retrying in 10 seconds...')
            time.sleep(10)

    # Now, forever check for a change in the VPN Port number by reading the specified file
    # When a change is detected, then update the listening_port in the qBittorrent VPN Client
    while True:

        __piaPortNumber = getPortNumber()
        # If this is a new port number, and the port number returned is NOT zero (0)
        if (__qbtPortNumber != __piaPortNumber) and (__piaPortNumber != 0):
            logging.debug (f'---------------------')
            logging.info (f'Assigned VPN forwarding port number is now: {__piaPortNumber}')
            # Let's update qBittorrent
            try:
                logging.info(f'The time is: {datetime.datetime.now()}')
                logging.info(f'Connecting to qBittorrent WEB API at {QBITTORRENT_URL}:{QBITTORRENT_PORT_NUMBER}')
                qbt_client.auth_log_in()
                logging.info(f'\tSuccessful connection')
                logging.info(f"\tqBittorrent: {qbt_client.app.version}")
                logging.info(f"\tqBittorrent Web API: v{qbt_client.app.web_api_version}")
                qbt_client.app.preferences = dict(listen_port=__piaPortNumber)
                # Validate with a call back to qBittorrent that the update to the listening port was successful
                if (qbt_client.app.preferences.listen_port == __piaPortNumber):
                    logging.info (f'\t🎉 Listening port updated successfully to {__piaPortNumber}')
                    __qbtPortNumber = __piaPortNumber
                else:
                    logging.error (f'\tSomething failed updating the port, will try again in {WATCH_INTERVAL} seconds')
                qbt_client.auth_log_out()
                logging.info('WEB API connection closed')
                logging.debug (f'---------------------')
            # If an error was encountered, then dump the details to the screen and try again
            except Exception as e:
                logging.error (f'Error: qBittorrent Web API Connection Failure')
                print (f'\t{e}')

        logging.debug (f'Watching {VPN_DATA_FILEPATH} for an updated port number, checking again in {WATCH_INTERVAL} seconds')
        time.sleep(WATCH_INTERVAL)


# Was this script called directly?  Then lets go....
if __name__=="__main__": 
    splashLogo()
    main() 