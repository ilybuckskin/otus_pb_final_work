FROM python:3.12-bullseye
ENV POETRY_VERSION=1.8.2
ENV POETRY_VENV=/opt/poetry-venv
ENV PATH="${PATH}:${POETRY_VENV}/bin"
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="/root/.local/bin:${PATH}"

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

COPY ./bot ./

RUN poetry install

EXPOSE 8000

CMD ["python", "bot.py"]