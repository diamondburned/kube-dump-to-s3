GIT_TAG    := $(shell git describe --tags --dirty --always)
GIT_TAGGED := $(shell git describe --tags --exact-match &> /dev/null && echo 1 || echo 0)

IMAGE_REPOSITORY ?=
IMAGE_NAME       ?= $(if $(IMAGE_REPOSITORY),$(IMAGE_REPOSITORY)/)kube-dump-to-s3
IMAGE_TAG        ?= $(GIT_TAG) 

HAS_NIX             := $(shell command -v nix-build 2> /dev/null)
DOCKER_BUILD_TARGET := $(if $(HAS_NIX),docker-build-with-nix,docker-build-with-docker)

.PHONY: list
list:
	@echo "Available targets:"
	@echo "  make docker-build"
	@echo "  make docker-build-with-nix"
	@echo "  make docker-build-with-docker"
	@echo "  make docker-push"

.PHONY: docker-build
docker-build: $(DOCKER_BUILD_TARGET)

.PHONY: docker-build-with-nix
docker-build-with-nix:
	docker load -i \
		$$(nix build --no-link --print-out-paths -f ./docker-image.nix \
			--argstr imageName $(IMAGE_NAME) \
			--argstr imageTag $(IMAGE_TAG) \
			--argstr created now)

.PHONY: docker-build-with-docker
docker-build-with-docker:
	docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

.PHONY: docker-push
docker-push: docker-push-tagged $(if $(GIT_TAGGED),docker-push-latest)

.PHONY: docker-push-tagged
docker-push-tagged: docker-build
	docker push $(IMAGE_NAME):$(IMAGE_TAG)

.PHONY: docker-push-latest
docker-push-latest: docker-build
	docker tag $(IMAGE_NAME):$(IMAGE_TAG) $(IMAGE_NAME):latest
	docker push $(IMAGE_NAME):latest
