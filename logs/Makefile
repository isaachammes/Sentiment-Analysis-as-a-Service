REPO=ihammes
IMAGE=logs
TAG=v1

build:
		docker build -t $(IMAGE):$(TAG) -f Dockerfile-logs .
		docker tag $(IMAGE):$(TAG) $(REPO)/$(IMAGE):$(TAG)
		docker push $(REPO)/$(IMAGE):$(TAG)
