FROM python:3.12.7-alpine3.20 AS pip-install

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install -r requirements.txt


FROM pip-install

COPY . .
ENV PYTHONUNBUFFERED=1
ENV DB_PASSWORD=
ENV OPENAI_KEY=
ENV AI_MODEL=gpt-4o-mini

EXPOSE 8000

CMD [ "fastapi", "run", "main.py" ]
