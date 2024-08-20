REGISTRY     ?= registry.fke.fptcloud.com
IMAGE_PREFIX ?= kube-dump-to-s3
IMAGE_NAME 	 ?= kube-dump-to-s3
VERSION      ?= $(shell git describe --tags --dirty --always)

# Image URL to use all building/pushing image targets
IMAGE ?= $(REGISTRY)/$(IMAGE_PREFIX)/$(IMAGE_NAME):$(VERSION) 


.PHONY: build
build:
	nix build

.PHONY: docker-build
docker-build:
	docker build -t ${IMAGE} .

.PHONY: docker-push
docker-push:
	docker push ${IMAGE}
