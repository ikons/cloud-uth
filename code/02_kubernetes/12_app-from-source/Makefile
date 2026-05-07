DOCKER_USER ?= your-dockerhub-username
APP_NAME    := cloud-uth-pyapp
VERSION     ?= 0.1.0
IMAGE       := $(DOCKER_USER)/$(APP_NAME):$(VERSION)

.PHONY: help test build push deploy status logs rollback clean

help:
	@echo "Targets:"
	@echo "  test      Run pytest locally before any build."
	@echo "  build     Build the Docker image as $(IMAGE)."
	@echo "  push      Push the image to Docker Hub."
	@echo "  deploy    Apply manifests with the IMAGE substituted in."
	@echo "  status    Show Deployment, Pods, and Service for this app."
	@echo "  logs      Tail logs from all replicas."
	@echo "  rollback  Roll back to the previous Deployment revision."
	@echo "  clean     Delete the Deployment and Service."
	@echo ""
	@echo "Variables: DOCKER_USER=<dockerhub-user> VERSION=<tag>"

test:
	python -m pytest -q

build:
	docker build -t $(IMAGE) .

push:
	docker push $(IMAGE)

deploy:
	# Substitute the image placeholder, then apply the rendered manifest.
	sed "s|REPLACE_ME_USER/cloud-uth-pyapp:0.1.0|$(IMAGE)|g" 01-deployment.yaml | kubectl apply -f -
	kubectl apply -f 02-service.yaml
	kubectl rollout status deployment/pyapp --timeout=180s
	@echo "Application deployed. Use: kubectl port-forward svc/pyapp 8080:80"

status:
	kubectl get deployment pyapp
	kubectl get pods -l app=pyapp -o wide
	kubectl get svc pyapp

logs:
	kubectl logs -l app=pyapp --tail=100 --prefix

rollback:
	kubectl rollout undo deployment/pyapp
	kubectl rollout status deployment/pyapp --timeout=180s

clean:
	kubectl delete -f 02-service.yaml --ignore-not-found
	kubectl delete deployment/pyapp --ignore-not-found
