# streamlit-app

- Build a docker image

```
docker build -t <image-name>:<image-tag> .
```

- To run the file in a docker container

```
docker run -p 8501:8501 <image-name>:<image-tag>
```

- To use docker-compose to start up the web-app alongwith a postgres instance with a persisted volume

```
docker-compose up --build
```
