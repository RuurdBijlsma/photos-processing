FROM ubuntu:22.04 AS python-base
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y python3.12 python3-distutils python3-pip python3-apt \
    && apt-get clean autoclean \
    && apt-get autoremove --yes

# Set environment variables (if needed)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    PYSETUP_PATH="/opt/pysetup" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    VENV_PATH="/opt/pysetup/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base AS builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
    && apt-get clean autoclean \
    && apt-get autoremove --yes \
    && curl -sSL https://install.python-poetry.org | python3

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./
RUN poetry install

FROM python-base AS development

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY poetry.lock pyproject.toml ./

# copy in our built poetry + venv
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN poetry install

WORKDIR /app
COPY photos ./photos
COPY alembic ./alembic
COPY poetry.lock pyproject.toml alembic.ini ./

ENV PYTHONPATH="/app"

EXPOSE 9475
CMD ["fastapi", "run", "photos/server.py", "--port", "9475"]