FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY ./app ./app

# Expose the default port for streamlit
EXPOSE 8501

ENTRYPOINT ["streamlit", "run"]
CMD [ "./app/main.py" ]