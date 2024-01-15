FROM ubuntu:20.04

RUN yum -y update && yum install -y gnupg2 curl python3-virtualenv libpq-dev
# Clean yum cache
RUN yum clean all

# Install the dependencies for the slurm-drmaa1 package
RUN wget https://github.com/natefoo/slurm-drmaa/releases/download/1.1.4/slurm-drmaa-1.1.4.tar.gz \
    && tar -xvzf slurm-drmaa-1.1.4.tar.gz \
    && cd slurm-drmaa-1.1.4 \
    && ./configure && make && make install && ldconfig

# Clean the installation files
RUN rm -rf slurm-drmaa-1.1.4.tar.gz slurm-drmaa-1.1.4

# Create a virtual environment for Python 3 and use th requirements.txt file to install the dependencies
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip

# Copy the files from the host to the container
COPY . /app
WORKDIR /app

COPY --chown=munge:munge docker/prod/munge.key /etc/munge/munge.key
RUN chmod 400 /etc/munge/munge.key

RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY docker/prod/drmaa-entrypoint.sh /usr/local/bin/drmaa-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/drmaa-entrypoint.sh"]
