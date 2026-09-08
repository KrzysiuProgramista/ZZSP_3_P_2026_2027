FROM python:3.12-slim

WORKDIR /code
RUN pip install fastapi[standard]

EXPOSE 8000

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]