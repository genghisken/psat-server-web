FROM python:3.9

RUN useradd \
--create-home \  
--shell /bin/bash \
--uid 1001 \
--user-group \
psat 

# Set the working directory in the container
WORKDIR /app

# Install system dependencies and then remove cache to reduce image size
RUN apt-get update && apt-get install -y \
    build-essential \
    pkg-config \
    apache2-dev \
    libhdf5-dev \
    default-mysql-client \
    default-libmysqlclient-dev \
    swig \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the parent directory (the repo) contents into the container at /app
COPY . .

# Install python dependencies and the package itself
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir mod_wsgi-standalone

WORKDIR /app/psat_server_web/atlas

# Link to the images dir and change ownership of everything in the app directory 
# to the psat user
RUN ln -s /images /app/psat_server_web/atlas/media/images/data && \
    chown -R psat:psat /app
      

USER 1001

# Set the command to run on container start
CMD ["bash"]