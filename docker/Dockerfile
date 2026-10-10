FROM python:3.12

RUN useradd --create-home --shell /bin/bash python

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=python:python . .

USER python

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]