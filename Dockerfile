FROM python:3.12
WORKDIR /app
COPY . .
RUN pip install flask flask-socketio requests python-dotenv
EXPOSE 5000
CMD ["python", "main.py"]
