FROM python:3.11-slim

WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app      ./app
COPY ./frontend ./frontend
COPY ./prompts  ./prompts
COPY config.py  .

RUN mkdir -p logs history

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
