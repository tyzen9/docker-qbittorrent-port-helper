# <img src="doc/images/t9_logo.png" height="25"> Tyzen9 - docker-qbittorrent-port-helper
In order to meet seeding requirements, other peers need to connect to your qBittorrent client. They use the port number specified in qBittorrent to establish this connection.  This container monitors a dynamically assigned VPN forwarding port number, and using the qBittorrent API, adds that port number to the qBittorrent client automatically as it changes.

> [!NOTE]
> This [docker image](https://hub.docker.com/repository/docker/tyzen9/qbittorrent-port-helper/general) is used in my in my experimental Docker stack [docker-servarr-seedbox](https://github.com/tyzen9/docker-servarr-seedbox), and keeps the qBittorrent instance available even as the VPN forwarded port number changes.

I created this image for use with my [docker-servarr-seedbox](https://github.com/tyzen9/docker-servarr-seedbox) stack that uses a [Private Internet Access](https://www.privateinternetaccess.com/) (PIA) VPN service but it can be adjusted for use with any VPN. When used with different VPN provider that support Port Forwarding, that VPN's container must write a port.dat file that only contains the forwarding port number in a volume shared with this docker container.

## Requirements
For full functionality, the qbittorrent-port-helper requires the following docker services:
- [linuxserver/qbittorrent](https://docs.linuxserver.io/images/docker-qbittorrent/) - a qBittorrent container with 
accessible API

## Recomendations
A PIA docker container that writes the forwarded port number to a file. The [docker-wireguard-pia](https://github.com/thrnz/docker-wireguard-pia) is built to do just this.  However, any container capable of writing its forwarded port number to a file will work.

- [docker-wireguard-pia](https://github.com/thrnz/docker-wireguard-pia) - A Docker container for using WireGuard with PIA

## What does it do?
The suggested WireGuard PIA container mentioned above writes the current port number to a file. Configured properly, the WireGuard PIA container will write this file to a volume shared with this container. This container's purpose is to periodically read that file, and determine if the VPN's forwarding port number has changed.  When this happens, this container it makes an API call to a qBittorrent instance to update the exposed listening port number. 

> [!IMPORTANT]
> If using PIA for the VPN, a region must be used that supports port forwarding, use this command to list compatible regions:

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
            - pia-portnumber:/vpn-data 
        environment:
            - TZ_ID=${TZ_ID}
            - QBITTORRENT_USERNAME=${QBITTORRENT_USERNAME}
            - QBITTORRENT_PASSWORD=${QBITTORRENT_PASSWORD}
            - QBITTORRENT_PORT_NUMBER=${QBITTORRENT_PORT_NUMBER}
            - QBITTORRENT_URL=${QBITTORRENT_URL}
            # Optional Settings
            # - VPN_DATA_FILEPATH=${VPN_DATA_FILEPATH}
            # - WATCH_INTERVAL=${WATCH_INTERVAL}
            # - STARTUP_DELAY=${STARTUP_DELAY}
            # - LOG_LEVEL=${LOG_LEVEL}
```
> [!IMPORTANT]
> The `pia-portnumber` volume listed in this config is created and the `port.dat` file is placed here by the [docker-wireguard-pia](https://github.com/thrnz/docker-wireguard-pia) container - see my [docker-servarr-seedbox](https://github.com/tyzen9/docker-servarr-seedbox) stack.

## Required Configuration Options
| Variable | Example | Definition |
| :---   | :--- | :--- |
| QBITORRENT_USERNAME | `<username>` | The username used to access the qBittorrent web portal|
| QBITTORRENT_PASSWORD | `<password>` | The password used to access the qBittorent web portal |
| QBITTORRENT_PORT_NUMBER | `8080` | The port number qBittorrent is running on |
| QBITTORRENT_URL |  `http://localhost` | The URL to the qBittorrent web portal, by default it will use the included instance |

## Optional Configuration Options
These environment variables are optional, and could be used to adjust functionality:
| Variable | Example | Definition |
| :---   | :--- | :--- |
| TZ_ID | `America/New_York` | Timezone to be running this container as [TZ IDs](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List) |
| VPN_DATA_FILEPATH | `/pia-shared/port.dat` | The path to the file being written by the VPN client containing the current forwarded port number.  This is usually best configured by using a shared volume. |
| WATCH_INTERVAL | `30` | The number of seconds between each time the `port.dat` file is read for detecting port number changes (default: 300)|
| STARTUP_DELAY | `5` | The number of seconds to delay the startup of the container (default:0)
| LOG_LEVEL | `INFO` | Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL  |


## Development Environment Requirements
- Docker Engine 
- Docker Desktop (optional)
- Make - used to build and publish images

## VS Code
The following extensions are recommended to be installed in VS Code:

- [Dev Containers](https://marketplace.visualstudio.com/items/?itemName=ms-vscode-remote.remote-containers)
- [Docker](https://marketplace.visualstudio.com/items/?itemName=ms-azuretools.vscode-docker)
- [Python](https://marketplace.visualstudio.com/items/?itemName=ms-python.python)

### Open the project in a Docker Dev Container for development using VS Code
1. Install the Recommended extensions (above):
2. Ensure Docker Desktop (or another Docker service) is running on your system.
3. In VS Code, Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P), and Select Dev Containers: `Reopen in Container`
    - VS Code will build the container based on the `.devcontainer/devcontainer.json` configuration 
      The first build might take some time, but subsequent openings will be faster.
7. Develop Inside the Container. 
    - Once connected, you can use all of VS Code's features (e.g., IntelliSense, debugging) as if working locally.

> [!TIP]
> All of the development specific configuration is done in the `.devcontainer` directory. The production builds are performed from the root using `make`.

## Build & Publish
Update the `Makefile` to contain the appropriate Docker Hub username, application name and version number

```
DOCKER_USERNAME ?= username
APPLICATION_NAME ?= application-name
VERSION ?= 1.0.0
```

To build images of this container, use this command in the root directory of the project:

```
make build
```

To publish th built images to to Docker Hub use this command in the root directory of the project:

To build use this command:
```
make push
```

# References
[Setting up a dockerized Python environment the elegant way](https://towardsdatascience.com/setting-a-dockerized-python-environment-the-elegant-way-f716ef85571d/)

