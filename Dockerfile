FROM python:alpine

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY exporter.py ./
COPY objectlist.json ./

#CMD [ "python", "./app.py" ]
CMD [ "python", "./exporter.py" ]

EXPOSE 9120

