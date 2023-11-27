FROM python:3
WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY daemon ./daemon

CMD ["gunicorn", "daemon:create_app()", "-b", "0.0.0.0"]