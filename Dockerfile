FROM python:3.9-alpine
ENV TELEGRAM_TOKEN $TELEGRAM_TOKEN 
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt && chmod 755 .
COPY . .
ENV TZ Europe/Moscow
CMD ["python3", "-u", "main.py"]