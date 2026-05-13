FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y software-properties-common gnupg2 curl
RUN add-apt-repository ppa:natefoo/slurm-drmaa
RUN apt-get update && apt-get install -y \
    munge \
    libmunge-dev \
    slurm-client \
    libslurm-dev \
    slurm-drmaa-dev \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    mysql-client \
    gosu \
    && rm -rf /var/lib/apt/lists/*

RUN groupmod -g 998 munge && usermod -u 998 -g 998 munge

RUN mkdir -p /run/munge /var/log/munge /var/lib/munge \
    && chown -R munge: /etc/munge/ /var/log/munge/ /run/munge/ /var/lib/munge/ \
    && chmod 0700 /etc/munge/ /var/log/munge/ /var/lib/munge/

RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip

COPY . /app
WORKDIR /app

RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

RUN drmaa_lib="$(find /usr/lib -name 'libdrmaa.so*' | head -n 1)" \
    && test -n "$drmaa_lib" \
    && ln -sf "$drmaa_lib" /usr/local/lib/libdrmaa.so \
    && ldconfig

COPY docker/testing/drmaa-entrypoint.sh /usr/local/bin/drmaa-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/drmaa-entrypoint.sh"]
