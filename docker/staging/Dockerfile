FROM ubuntu:20.04 as build

RUN apt update && apt install -y software-properties-common
RUN add-apt-repository ppa:natefoo/slurm-drmaa
RUN apt update && apt install -y libmunge-dev slurm-client libslurm-dev slurm-drmaa-dev python3.8-dev python3.8-venv \
  python3-pip pkg-config build-essential default-libmysqlclient-dev python3-mysqldb gosu apache2 libapache2-mod-wsgi-py3

RUN mkdir /run/munge
RUN chown -R munge: /etc/munge/ /var/log/munge/ /run/munge/
RUN chmod 0700 /etc/munge/ /var/log/munge/

# Create a virtual environment for Python 3 and use th requirements.txt file to install the dependencies
RUN python3.8 -m venv /opt/venv
RUN /opt/venv/bin/pip3 install --upgrade pip

# Copy the files from the host to the container
COPY . /app
WORKDIR /app

COPY --chown=munge:munge docker/staging/munge.key /etc/munge/munge.key
RUN chmod 400 /etc/munge/munge.key

RUN /opt/venv/bin/pip3 install -r requirements.txt

COPY docker/staging/drmaa-entrypoint.sh /usr/local/bin/drmaa-entrypoint.sh
RUN chmod +x /usr/local/bin/drmaa-entrypoint.sh

# Configure Apache2 to serve the Django application using mod_wsgi
COPY docker/staging/apache-config.conf /etc/apache2/sites-available/000-default.conf
RUN a2enmod wsgi

# Create the static file directory and assign permissions to the www-data user, if it doesn't exist
RUN mkdir -p /app/static
RUN chown -R www-data:www-data /app/static

# Add ServerName to apache2.conf
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

ENTRYPOINT ["/usr/local/bin/drmaa-entrypoint.sh"]
EXPOSE 80
