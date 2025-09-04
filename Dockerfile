# 1. Use a more recent and secure Python base image
FROM python:3.11-slim-bullseye

# 2. Set the working directory for your application
WORKDIR /app

# 3. Update packages, install git, and clean up in a single layer
# This reduces the final image size.
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# 4. Copy the requirements file first to leverage Docker's layer caching
# This step is only re-run if requirements.txt changes.
COPY requirements.txt .

# 5. Upgrade pip and install Python dependencies
# --no-cache-dir also helps keep the image size small.
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy your entire project's code into the working directory
# This assumes you run the 'docker build' command from your project's root.
COPY . .

# 7. Make your start script executable
RUN chmod +x ./start.sh

# 8. Define the command to run when the container starts
CMD ["/bin/bash", "./start.sh"]
