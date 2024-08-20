IMAGE_REPOSITORY ?=
IMAGE_NAME       ?= $(if $(IMAGE_REPOSITORY),$(IMAGE_REPOSITORY)/)kube-dump-to-s3
IMAGE_TAG        ?= $(shell git describe --tags --dirty --always) 

.PHONY: list
list:
	@echo "Available targets:"
	@echo "  make docker-build"
	@echo "  make docker-build-with-nix"
	@echo "  make docker-build-with-docker"
	@echo "  make docker-push"

HAS_NIX := $(shell command -v nix-build 2> /dev/null)
DOCKER_BUILD_TARGET := $(if $(HAS_NIX),docker-build-with-nix,docker-build-with-docker)

.PHONY: docker-build
docker-build: $(DOCKER_BUILD_TARGET)

.PHONY: docker-build-with-nix
docker-build-with-nix:
	nix build \
		-f ./docker-image.nix \
		--argstr imageName $(IMAGE_NAME) \
		--argstr imageTag $(IMAGE_TAG)
	docker load -i result
	rm result

.PHONY: docker-build-with-docker
docker-build-with-docker:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: docker-push
docker-push:
	docker push $(IMAGE_NAME):$(IMAGE_TAG)
