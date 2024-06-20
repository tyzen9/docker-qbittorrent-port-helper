# Usage: make build push
DOCKER_USERNAME ?= tyzen9
APPLICATION_NAME ?= qbittorrent-port-helper
 
build:
	docker build --tag ${DOCKER_USERNAME}/${APPLICATION_NAME} .

push:
	docker push ${DOCKER_USERNAME}/${APPLICATION_NAME}