FROM giovtorres/slurm-docker-cluster:25.11.4-2.3.0
#FROM giovtorres/slurm-docker-cluster:latest

RUN yum -y update
RUN yum -y groupinstall development
RUN yum install -y --allowerasing gnupg2 curl python3-devel libpq-devel wget slurm-libs mysql-devel
# Clean yum cache
RUN yum clean all

## Install the dependencies for the slurm-drmaa1 package
#RUN wget https://github.com/natefoo/slurm-drmaa/releases/download/1.1.5/slurm-drmaa-1.1.5.tar.gz \
#    && tar -xvzf slurm-drmaa-1.1.5.tar.gz \
#    && cd slurm-drmaa-1.1.5 \
#    && ./configure && make && make install && ldconfig

## Clean the installation files
#RUN rm -rf slurm-drmaa-1.1.4.tar.gz slurm-drmaa-1.1.4

# Trying to install the rpm package instead of building from source
RUN wget https://github.com/natefoo/slurm-drmaa/releases/download/1.1.5/slurm-drmaa-1.1.5-22.05.el9.x86_64.rpm
RUN rpm -i slurm-drmaa-1.1.5-22.05.el9.x86_64.rpm

# Create a virtual environment for Python 3 and use th requirements.txt file to install the dependencies
RUN python3 -m venv /opt/venv
RUN /opt/venv/bin/pip install --upgrade pip

# Copy the files from the host to the container
COPY . /app
WORKDIR /app
RUN ls -la

RUN /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY docker/testing/drmaa-entrypoint.sh /usr/local/bin/dramaa-entrypoint.sh
ENTRYPOINT ["/usr/local/bin/dramaa-entrypoint.sh"]
