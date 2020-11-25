REPO=ihammes
IMAGE=worker
TAG=v1

build:
	docker build -t $(IMAGE):$(TAG) -f Dockerfile-worker .
	docker tag $(IMAGE):$(TAG) $(REPO)/$(IMAGE):$(TAG)
	docker push $(REPO)/$(IMAGE):$(TAG)
