FROM ubuntu:20.04 as build

RUN apt update && apt install -y software-properties-common
RUN add-apt-repository ppa:natefoo/slurm-drmaa
RUN apt update && apt install -y libmunge-dev slurm-client libslurm-dev slurm-drmaa-dev python3.8-dev python3.8-venv \
  python3-pip pkg-config build-essential default-libmysqlclient-dev python3-mysqldb gosu apache2 libapache2-mod-wsgi-py3 \
    locales language-pack-en

# We need to set the locale to UTF-8 to avoid issues with Python 3 and using ASCII encoding
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN mkdir /run/munge
RUN chown -R munge: /etc/munge/ /var/log/munge/ /run/munge/
RUN chmod 0700 /etc/munge/ /var/log/munge/

# ATTENTION: If you using user remapping, you need to set the same gid as the users group on the cluster
# To do so, we need to create an internal user with a uid that when remapped will have the same gid as the users group on the cluster
# This is necessary to allow the container to write to the shared volume and for the external user to read and write in the
# directories created by the container
# The user here created will be the one running the Django application with Apache2 and mod_wsgi (look at the Apache2 configuration)
RUN groupdel users
RUN groupadd -g 997001 users
RUN useradd -u 1000042 myuser
RUN usermod -a -G users myuser
# Add users to the root user, so root can write to the shared volume
RUN usermod -a -G users root

# Create a virtual environment for Python 3 and use th requirements.txt file to install the dependencies
RUN python3.8 -m venv /opt/venv
RUN /opt/venv/bin/pip3 install --upgrade pip

# Copy the files from the host to the container
COPY . /app
WORKDIR /app

# Copy the munge key to the container
COPY --chown=munge:munge docker/deploy/munge.key /etc/munge/munge.key
RUN chmod 400 /etc/munge/munge.key

# Install the dependencies for DRMAAtic
RUN /opt/venv/bin/pip3 install -r requirements.txt

# Copy the entrypoint script to the container and make it executable
COPY docker/deploy/drmaa-entrypoint.sh /usr/local/bin/drmaa-entrypoint.sh
RUN chmod +x /usr/local/bin/drmaa-entrypoint.sh

# Copy the SLURM configuration files to the container
COPY docker/deploy/slurm.conf /etc/slurm-llnl/slurm.conf
COPY docker/deploy/slurmdbd.conf /etc/slurm-llnl/slurmdbd.conf

# Create the static directory and set the permissions
RUN mkdir -p /app/static
RUN chown -R django:users /app/static
RUN chown -R django:users /app/drmaatic/migrations

# Configure Apache2 to serve the Django application using mod_wsgi
RUN a2enmod wsgi

# Add ServerName to apache2.conf
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

ENTRYPOINT ["/usr/local/bin/drmaa-entrypoint.sh"]
EXPOSE 80
