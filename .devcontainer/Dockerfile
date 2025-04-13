FROM python:3.11-slim

# Install prerequisites for docker-in-docker
RUN apt-get update && apt-get install -y --no-install-recommends \
    apt \
    dpkg \
    ca-certificates \
    curl \
    libc-bin \
    passwd \
&& rm -rf /var/lib/apt/lists/*


# Set the working directory inside of the image's fileystem
WORKDIR /workspace 

# Installed the required Python libraries
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Make a directory on the image's filesystem
# and copy the application into that directory
RUN mkdir -p tyzen9
COPY app/. ./tyzen9/.

# Production entry point
# --- NOTE: This is NOT executed when starting a dev container
# ENTRYPOINT ["python3", "tyzen9/main.py"]