# <img src="https://github.com/tyzen9/tyzen9/blob/main/images/logos/t9_logo.png" height="25"> Tyzen9 - docker-qbittorrent-port-helper
In order to meet seeding requirements, other peers need to connect to your qBittorrent client. They use the port number specified in qBittorrent to attempt to establish this connection.  This container monitors the dynamically assigned PIA port number, and using the qBittorrent API, adds that number to the qBittorrent client automatically as it changes.

> [!NOTE]
> This [docker image](https://hub.docker.com/repository/docker/tyzen9/qbittorrent-port-helper/general) is used in my in my experimental Docker stack [docker-servarr-seedbox](https://github.com/tyzen9/docker-servarr-seedbox), and keeps the qBittorrent instance available even as the PIA exposed port number changes.

I created this image for use with my [docker-servarr-seedbox](https://github.com/tyzen9/docker-servarr-seedbox) stack that uses a [Private Internet Access](https://www.privateinternetaccess.com/) (PIA) VPN service but it can be adjusted for use with any VPN. When used with different VPN provider that supports Port Forwarding, that VPN's container must write a port.dat file that only contains the forwarding port number in a shared volume with this docker container.

## Requirements
For full functionality, the qbittorrent-port-helper requires the following docker services:
- [linuxserver/qbittorrent](https://docs.linuxserver.io/images/docker-qbittorrent/) - a qBittorrent container with accessible API
- [docker-wireguard-pia](https://github.com/thrnz/docker-wireguard-pia) - A Docker container for using WireGuard with PIA

## What does it do?
The WireGUard PIA container mentioned above writes the current port number to a file so that other containers can gain access to that number.  This container's purpose is to periodically read that file, and determine if that port number has changed.  When that port number changes, it makes an API call to a qBittorrent instance to update the exposed port number. 

> [!IMPORTANT]
> The PIA connection must use a region that supports port forwarding, use this command to list compatible regions:

List all PIA regions that support port forwarding: 
`# curl https://serverlist.piaservers.net/vpninfo/servers/v4  |jq '.regions[]| select(.port_forward) | {NAME: .name, ID: .id}'| cat`

## Supported Architectures
Simply pulling `tyzen9/qbittorrent-port-helper:latest` should retrieve the correct image for your arch. The architectures supported by this image are:

| Architecture | Available | Tag |
| :---   | :--- | :--- |
| x86-64 | ✅ | latest |
| arm64	 | ✅ | latest |

Specific version tags are available on [Docker Hub](https://hub.docker.com/repository/docker/tyzen9/qbittorrent-port-helper/tags).

## Deployment
This is best deployed using docker compose, and typically in the same stack as the VPN client - see my [docker-servarr-seedbox](https://github.com/tyzen9/docker-servarr-seedbox) stack. Here is an example:

```yaml
services:
  qbittorrent-port-helper:
        image: tyzen9/qbittorrent-port-helper:latest
        container_name: qbittorrent-port-helper
        restart: always
        volumes:
            - pia-portnumber:/pia-shared
        environment:
            - QBITTORRENT_USERNAME=<username>
            - QBITTORRENT_PASSWORD=<password>
            - QBITTORRENT_PORT_NUMBER=8080
            - QBITTORRENT_URL=http://localhost
            - WATCH_INTERVAL=30
            - FILE=/pia-shared/port.dat
```
> [!IMPORTANT]
> The `pia-portnumber` volume listed in this config is created and the `port.dat` file is placed here by the [docker-wireguard-pia](https://github.com/thrnz/docker-wireguard-pia) container - see my [docker-servarr-seedbox](https://github.com/tyzen9/docker-servarr-seedbox) stack.

## Configuration Options
| Variable | Example | Definition |
| :---   | :--- | :--- |
| QBITORRENT_USERNAME | `<username>` | The username used to access the qBittorrent web portal|
| QBITTORRENT_PASSWORD | `<password>` | The password used to access the qBittorent web portal |
| QBITTORRENT_PORT_NUMBER | `8080` | The port number qBittorrent is running on |
| QBITTORRENT_URL |  `http://localhost` | The URL to the qBittorrent web portal, by default it will use the included instance |
| WATCH_INTERVAL | `30` | The number of seconds between each time the `port.dat` file is read for detecting port number changes |
| FILE | `/pia-shared/port.dat` | The path to the file being written by [docker-wireguard-pia](https://github.com/thrnz/docker-wireguard-pia) that contains the current port number.  This is usually best configured by using a shared volume. |

# Development
The development guidelines assume you are running on a system with docker and `make` installed. When developing, we need an instance of qBittorrent to test with.  For this we use Docker Compose to build our image, and include an instance of qBittorrent. 

## Start the Development Environment
The development environment is fired up using the command:
```
docker compose up
```

## Configure qBittorrent
The first time qBittorrent runs, it assigns a random password that you will need to retrieve by looking at the logs generated by the qBittorrent container. In those logs, you will see a message similar to this one below:
```
2025-01-21 16:47:56 To control qBittorrent, access the WebUI at: http://localhost:8080
2025-01-21 16:47:56 The WebUI administrator username is: admin
2025-01-21 16:47:56 The WebUI administrator password was not set. A temporary password is provided for this session: c2AgI7IF6
2025-01-21 16:47:56 You should set your own password in program preferences.
```

Note the temporary password listed in the container logs (`c2AgI7IF6` in this example).

### Set the qBittorrent username and password
1. Open the qBittorrent UI at http://<hostname>:8080
1. Login with the username `admin` and the temporary password from the container log file.
1. Open the Options panel under `Tools` -> `Options`
1. Click the WebUI tab
1. Set the desired username and password to use for authentication, and click `Save`

### Update the `qbittorrent-port-helper` credentials
1. Stop the development environment using `docker down`
1. In the `compose.yml` file, set the `QBT_USERNAME` and `QBT_PASSWORD` environment variables for the `qbittorrent-port-helper` container to the credentials you used in the WebUI tab of qBittorrent.
1. Start the development environment using `docker up`


Next, check the `qbittorrent-port-helper` container logs. You should see a success message like the one below with ✅ and 🎉 emojis.  

```
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
please wait 5 seconds...
Validate qBittorrent WEB API connection at http://localhost:8080
	✅  Validated
---------------------
Assigned VPN forwarding port number is now: 53727
The UTC time is: 2025-01-21 22:06:48.529196
Connecting to qBittorrent WEB API at http://localhost:8080
	Successful connection
	qBittorrent: v5.0.3
	qBittorrent Web API: v2.11.2
	🎉  Listening port updated successfully to 53727
WEB API connection closed
---------------------
Watching /pia-shared/port.dat for an updated port number, checking again in 30 seconds 
```

If you do not see the expected success message as described above, try to stop/start the stack again.

## Image Build
To make this docker image, run this command 
```
make build
```
