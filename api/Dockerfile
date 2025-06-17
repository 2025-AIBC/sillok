#------------------------------------------------------------------------------
# Description
#| 1. Build fastapi image.
#|   > `docker build --tag fastapi -f Dockerfile.fastapi .`
#| 2. Create a container and attach to it.
#|   > `docker run -d --name fastapi -p 80:80 fastapi`
# ------------------------------------------------------------------------------
FROM python:3.12.3-slim-bookworm

ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local'\
    POETRY_VERSION=1.8.2 \
    # OpenAI API Key:
    API_KEY='INSERT YOUR OPEN AI API KEY HERE. OR FOLLOWING `docker run ...` COMMAND IN THE `Usage.md` FILE.'
    
RUN apt-get update && apt-get upgrade -y \
    && apt-get install --no-install-recommends -y \
    bash \
    build-essential \
    curl \
    git \
    libpq-dev \
    # Installing `poetry` package manager:
    # https://github.com/python-poetry/poetry
    && curl -sSL 'https://install.python-poetry.org' | python - \
    && poetry --version \
    # && poetry add uvicorn \
    # Cleaning cache:
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*


WORKDIR /sillok_api

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --no-interaction --no-ansi

COPY . .

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]