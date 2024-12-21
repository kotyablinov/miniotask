FROM python:3.12-slim-bookworm
COPY ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY templates /app/templates
COPY app.py /app
EXPOSE 5000
CMD ["python", "app.py" ]
