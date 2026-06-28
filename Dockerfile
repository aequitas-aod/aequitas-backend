FROM python:3.14-slim

WORKDIR /home/aequitas-backend

COPY requirements.txt ./requirements.txt
COPY pyproject.toml ./pyproject.toml
COPY poetry.lock ./poetry.lock
COPY poetry.toml ./poetry.toml

# removes the configurations to delete cached files after a successful install
RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
    echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

RUN apt-get update && \
    apt-get install -y curl librsvg2-bin && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV ENV=production

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    poetry install --without dev --no-root

COPY . .

CMD ["sh", "-c", "poe serve --port $AEQUITAS_BACKEND_PORT"]