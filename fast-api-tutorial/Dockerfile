FROM python:3.9

# to organise the structure in container. This will become the starting point
WORKDIR /fastapi-python

# . represents current dir
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the app folder in the container
COPY ./app ./app

# Specify the entrypoint 
CMD [ "python","./app/main.py" ]