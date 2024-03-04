FROM public.ecr.aws/lambda/python:3.11 as osml_tile_server_test

# Only override if you're using a mirror with a cert pulled in using cert-base as a build parameter
ARG BUILD_CERT=/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem
ARG PIP_INSTALL_LOCATION=https://pypi.org/simple/

ARG CONDA_ENV_NAME="tile-server-test"

# Define required packages to install
ARG PACKAGES="wget"

# Give sudo permissions
USER root

# Configure, update, and refresh yum enviornment
RUN yum update -y && yum clean all && yum makecache

# Install all our dependancies
RUN yum install -y $PACKAGES

# Install miniconda
ARG MINICONDA_VERSION=Miniconda3-latest-Linux-x86_64
ARG MINICONDA_URL=https://repo.anaconda.com/miniconda/${MINICONDA_VERSION}.sh
RUN wget -c ${MINICONDA_URL} \
    && chmod +x ${MINICONDA_VERSION}.sh \
    && ./${MINICONDA_VERSION}.sh -b -f -p /usr/local

# Clean up installer file
RUN rm ${MINICONDA_VERSION}.sh

# Copy tests into container
COPY . /home/
RUN chmod +x --recursive /home/
RUN chmod 777 --recursive /home/

# CD to the home directory
WORKDIR /home

# Install python with conda
RUN conda env create -n ${CONDA_ENV_NAME} --file environment.yml

# Clean up any dangling conda resources
RUN conda clean -afy

ENV PATH /usr/local/envs/${CONDA_ENV_NAME}/bin:$PATH

# Import the source directory to the generalized path
ENV PYTHONPATH="/usr/local/envs/${CONDA_ENV_NAME}/bin"

ENTRYPOINT ["python", "src/aws/osml/run_test.py"]
