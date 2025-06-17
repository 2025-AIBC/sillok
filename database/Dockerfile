# Dockerfile
FROM postgres:16.2-bookworm

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    postgresql-server-dev-16

RUN git clone https://github.com/pgvector/pgvector.git \
&& cd pgvector \
&& make \
&& make install

RUN apt-get remove -y build-essential git postgresql-server-dev-16 \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /pgvector

RUN echo "CREATE EXTENSION vector;" >> /docker-entrypoint-initdb.d/init.sql