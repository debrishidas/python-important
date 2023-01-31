# python-fast-api

A simple python application designed to run in a containerized environment of Kubernetes

- Build a docker image

```
docker build -t python-fast-api .
```

- Push docker image to docker hub

```
docker tag python-fast-api <dockerhub-username>/python-fast-api
docker login -u <dockerhub-username> -p <password>
docker push <dockerhub-username>/python-fast-api
```

- Run the application in a docker container & goto localhost:8000 to see the app in action

```
docker run -p 8000:8000 python-fast-api
```

- Run the application on kubernetes & goto localhost:2000 to see the app in action

```
kubectl apply -f kubernetes/deployment/deployment.yaml
kubectl apply -f kubernetes/deployment/service.yaml
kubectl port-forward <pod-name> 2000:8000
```
