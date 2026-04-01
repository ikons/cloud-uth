.PHONY: deploy clean

deploy:
	# Create configuration, storage, and database resources first.
	kubectl apply -f 01-secret.yaml
	kubectl apply -f 02-configmap.yaml
	kubectl apply -f 03-pvc.yaml
	kubectl apply -f 04-init-sql.yaml
	kubectl apply -f 05-postgres.yaml
	kubectl apply -f 06-postgres-svc.yaml
	@echo "Waiting for PostgreSQL to start..."
	kubectl wait --for=condition=Ready pod/postgres --timeout=120s
	# Deploy the application tier only after the database is ready.
	kubectl apply -f 07-web-content.yaml
	kubectl apply -f 08-webserver.yaml
	kubectl apply -f 09-webserver-svc.yaml
	kubectl wait --for=condition=Ready pod/webserver --timeout=60s
	@echo "Application deployed! Use: kubectl port-forward svc/webserver-service 8080:80"

clean:
	kubectl delete -f 09-webserver-svc.yaml --ignore-not-found
	kubectl delete -f 08-webserver.yaml --ignore-not-found
	kubectl delete -f 07-web-content.yaml --ignore-not-found
	kubectl delete -f 06-postgres-svc.yaml --ignore-not-found
	kubectl delete -f 05-postgres.yaml --ignore-not-found
	kubectl delete -f 04-init-sql.yaml --ignore-not-found
	kubectl delete -f 03-pvc.yaml --ignore-not-found
	kubectl delete -f 02-configmap.yaml --ignore-not-found
	kubectl delete -f 01-secret.yaml --ignore-not-found
