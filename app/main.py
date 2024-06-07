import os
import requests
import sys
import json
import time
import datetime
import qbittorrentapi

from colorama import init as colorama_init
from colorama import Fore, Style
colorama_init()

# Set all values that are set via the environment
qbt_url = os.environ['QBITTORRENT_URL']
qbt_port = os.environ['QBITTORRENT_PORT_NUMBER']
qbt_username = os.environ['QBITTORRENT_USERNAME']
qbt_password = os.environ['QBITTORRENT_PASSWORD']
vpn_portFile = os.environ['FILE']
watch_interval =  int(os.environ['WATCH_INTERVAL'])

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def printSplash():
    """
    Print the splash screen
    """
    print(f''' _____                                                          _____ 
( ___ )                                                        ( ___ )
 |   |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|   | 
 |   |                                                          |   | 
 |   |   ████████╗██╗   ██╗███████╗███████╗███╗   ██╗ █████╗    |   | 
 |   |   ╚══██╔══╝╚██╗ ██╔╝╚══███╔╝██╔════╝████╗  ██║██╔══██╗   |   | 
 |   |      ██║    ╚████╔╝   ███╔╝ █████╗  ██╔██╗ ██║╚██████║   |   | 
 |   |      ██║     ╚██╔╝   ███╔╝  ██╔══╝  ██║╚██╗██║ ╚═══██║   |   | 
 |   |      ██║      ██║   ███████╗███████╗██║ ╚████║ █████╔╝   |   | 
 |   |      ╚═╝      ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═══╝ ╚════╝    |   | 
 |   |                {Fore.CYAN}https://github.com/tyzen9{Fore.RESET}                 |   | 
 |   |                    Made in the {Fore.RED}U{Fore.RESET}.{Fore.WHITE}S{Fore.RESET}.{Fore.BLUE}A{Fore.RESET}.                    |   | 
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
        file = open(vpn_portFile, 'r')
        first_line = file.readline()
        file.close()
        # Convert the port number into an integer
        __returnValue = int(first_line.strip())
    except Exception as e:
        print (f'{Fore.RED}Error:  Unable to read port number from {vpn_portFile}{Fore.RESET}')
        print (f'\t{e}')
    return(__returnValue)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def main(): 
    __qbtPortNumber = None
    __qbtConnectionValidated = False

    # Set the qBittorrent WEB API connection values
    conn_info = dict(
        host=qbt_url,
        port=qbt_port,
        username=qbt_username,
        password=qbt_password,
    )

    print(f'{Fore.LIGHTBLACK_EX}please wait 5 seconds...{Fore.RESET}')
    time.sleep(5)

    # Instantiate a qBittorrent WEB API Client using the appropriate WebUI configuration
    qbt_client = qbittorrentapi.Client(**conn_info)

    # Keep trying to connect to qBittorrent until we make a successful connection
    while __qbtConnectionValidated == False:
        # First lets make sure we can connect to the qBittorrent API by just logging in/out
        try:
            print(f'Validate qBittorrent WEB API connection at {qbt_url}:{qbt_port}')
            qbt_client.auth_log_in()
            qbt_client.auth_log_out()
            print(f'\t✅  Validated')
            __qbtConnectionValidated = True
        except Exception as e:
            print (f'{Fore.RED}Error:  qBittorrent Web API Login Failure{Fore.RESET}')
            print ('**********************************************************************')
            print (f'Please make sure qBittorrent is running at {qbt_url}:{qbt_port}\n')
            print ('If this is the first time the qBittorrent container is being run, then')
            print ('check its output log for the admin users\'s temporary password.  Update')
            print ('the qBittorrent admin password  using the qBittorrent web interface to')
            print ('match the password specified in this application, and restart.')
            print ('**********************************************************************')
            print ('Exception Details:')
            print (f'{e}\n')
            print ('Retrying in 10 seconds...')
            time.sleep(10)

    # Now, forever check for a change in the VPN Port number by reading the specified file
    # When a change is detected, then update the listening_port in the qBittorrent VPN Client
    while True:

        __piaPortNumber = getPortNumber()
        # If this is a new port number, and the port number returned is NOT zero (0)
        if (__qbtPortNumber != __piaPortNumber) and (__piaPortNumber != 0):
            print (f'---------------------')
            print (f'{Fore.BLUE}Assigned VPN forwarding port number is now: {__piaPortNumber}{Fore.RESET}')
            # Let's update qBittorrent
            try:
                print(f'The UTC time is: {datetime.datetime.now()}')
                print(f'Connecting to qBittorrent WEB API at {qbt_url}:{qbt_port}')
                qbt_client.auth_log_in()
                print(f'\tSuccessful connection')
                print(f"\tqBittorrent: {qbt_client.app.version}")
                print(f"\tqBittorrent Web API: v{qbt_client.app.web_api_version}")
                qbt_client.app.preferences = dict(listen_port=__piaPortNumber)
                # Validate with a call back to qBittorrent that the update to the listening port was successful
                if (qbt_client.app.preferences.listen_port == __piaPortNumber):
                    print (f'\t🎉  {Fore.GREEN}Listening port updated successfully to {__piaPortNumber}{Fore.RESET}')
                    __qbtPortNumber = __piaPortNumber
                else:
                    print (f'\t{Fore.RED}Something failed updating the port, will try again in {watch_interval} seconds{Fore.RESET}')
                qbt_client.auth_log_out()
                print('WEB API connection closed')
                print (f'---------------------')
            # If an error was encountered, then dump the details to the screen and try again
            except Exception as e:
                print (f'{Fore.RED}Error: qBittorrent Web API Connection Failure{Fore.RESET}')
                print (f'\t{e}')

        print (f'{Fore.LIGHTBLACK_EX}Watching {vpn_portFile} for an updated port number, checking again in {watch_interval} seconds {Fore.RESET}')
        time.sleep(watch_interval)


# Was this script called directly?  Then lets go....
if __name__=="__main__": 
    printSplash()
    main() 