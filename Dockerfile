FROM python:3.13-slim AS build

WORKDIR /home/aequitas-backend

COPY requirements.txt ./requirements.txt
COPY pyproject.toml ./pyproject.toml
COPY poetry.lock ./poetry.lock
COPY poetry.toml ./poetry.toml

ENV POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root


FROM python:3.13-slim AS production

# removes the configurations to delete cached files after a successful install
RUN rm -f /etc/apt/apt.conf.d/docker-clean; echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN apt-get update && \
    apt-get install -y curl && \
    apt-get install -y librsvg2-bin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


ENV VIRTUAL_ENV="/home/aequitas-backend/.venv"

WORKDIR /home/aequitas-backend

COPY . .
COPY --from=build /home/aequitas-backend/requirements.txt ./requirements.txt
COPY --from=build /home/aequitas-backend/pyproject.toml ./pyproject.toml

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=build ${VIRTUAL_ENV} ${VIRTUAL_ENV}

ENV ENV=production

CMD ["sh", "-c", "poe serve --port $AEQUITAS_BACKEND_PORT"]