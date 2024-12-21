FROM python:3.12.7-alpine3.20 AS pip-install

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt


FROM pip-install

EXPOSE 8000

COPY . .
CMD [ "fastapi", "run", "main.py" ]
