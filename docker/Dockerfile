FROM python:3.12

RUN useradd --create-home --shell /bin/bash python

USER python

WORKDIR /app

COPY requirements.txt .

RUN python -m venv /app/.venv && /app/.venv/bin/pip install --no-cache-dir -r requirements.txt

ENV PATH="/app/.venv/bin:$PATH"

COPY --chown=python:python . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]