FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD streamlit run --server.port $PORT --server.headless true --server.enableCORS false app.py
