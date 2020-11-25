REPO=ihammes
IMAGE=rest-server
TAG=v1

build:
		docker build -t $(IMAGE):$(TAG) -f Dockerfile-rest .
		docker tag $(IMAGE):$(TAG) $(REPO)/$(IMAGE):$(TAG)
		docker push $(REPO)/$(IMAGE):$(TAG)
