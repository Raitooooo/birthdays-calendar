FROM python:3.12-slim
RUN pip install --upgrade pip
WORKDIR /app
COPY requirements.txt .
COPY main.py .
COPY config.py .
COPY database.py .
COPY alembic.ini .
COPY app/ ./app/
COPY alembic/ ./alembic/
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD [ "python", "main.py" ]

