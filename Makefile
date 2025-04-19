# Usage: make build push
DOCKER_USERNAME ?= tyzen9
APPLICATION_NAME ?= qbittorrent-port-helper
VERSION ?= 2.0.0
 
build:
	docker buildx build --platform linux/amd64,linux/arm64 \
		--tag ${DOCKER_USERNAME}/${APPLICATION_NAME}:${VERSION} \
		--tag ${DOCKER_USERNAME}/${APPLICATION_NAME}:latest \
		--file Dockerfile \
		.

push:
	docker push ${DOCKER_USERNAME}/${APPLICATION_NAME}:${VERSION}
	docker push ${DOCKER_USERNAME}/${APPLICATION_NAME}:latest