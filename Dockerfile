FROM python:3.11

WORKDIR /app

COPY /code /app/code
COPY /images/logo.jpg /app/images/logo.jpg

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r /app/code/backend/requirements.txt
RUN pip install -r /app/code/frontend/requirements.txt

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# start service
CMD ["/app/start.sh"]
