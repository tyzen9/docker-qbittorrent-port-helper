# <img src="https://github.com/tyzen9/tyzen9/blob/main/images/logos/t9_logo.png" height="25"> Tyzen9 - docker-qbittorrent-port-helper
In order to meet seeding requirements, other peers need to connect to your qBittorrent client. They use the port number specified in qBittorrent to attempt to establish this connection.  This container monitors the dynamically assigned PIA port number, and using the qBittorrent API, adds that number to the qBittorrent client automatically as it changes.

> [!INFO]
> This [docker image](https://hub.docker.com/repository/docker/tyzen9/qbittorrent-port-helper/general) is used in my in my experimental Docker stack [docker-pia-servarr](https://github.com/tyzen9/docker-pia-servarr), and keeps the qBittorrent instance available even as the PIA exposed port number changes.

## Requirements
For full functionality, the qbittorrent-port-helper requires the following docker services:
- [linuxserver/qbittorrent](https://docs.linuxserver.io/images/docker-qbittorrent/) - a qBittorrent container with accessible API
- [docker-wireguard-pia](https://github.com/thrnz/docker-wireguard-pia) - A Docker container for using WireGuard with PIA

## What does it do?
The WireGUard PIA container mentioned above writes the current port number to a file so that other containers can gain access to that number.  This container's purpose is to periodically read that file, and determine if that port number has changed.  When that port number changes, it makes an API call to a qBittorent instance to update the exposed port number. 

> [!IMPORTANT]
> The PIA connection must use a region that supports port forwarding, use this command to list compatible regions:

List all PIA regions that support port forwarding: 
`# curl https://serverlist.piaservers.net/vpninfo/servers/v4  |jq '.regions[]| select(.port_forward) | {NAME: .name, ID: .id}'| cat`


## Docker Compose
Add the qbittorrent-port-helper declaration to your docker compose file.

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

| Variable | Example | Definition |
| :---   | :--- | :--- |
| QBITORRENT_USERNAME | `<username>` | The username used to access the qBittorrent web portal|
| QBITTORRENT_PASSWORD | `<password>` | The password used to access the qBittorent web portal |
| QBITTORRENT_PORT_NUMBER | `8080` | The port number qBittorrent is running on |
| QBITTORRENT_URL |  `http://localhost` | The URL to the qBittorrent web portal, by default it will use the included instance |
| WATCH_INTERVAL | `30` | The number of seconds between each time the `port.dat` file is read for detecting port number changes |
| FILE | `/pia-shared/port.dat` | The path to the file being written by [docker-wireguard-pia](https://github.com/thrnz/docker-wireguard-pia) that contains the current port number.  This is usually best configured by using a shared volume. |
