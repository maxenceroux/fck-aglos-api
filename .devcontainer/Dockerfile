FROM python:3.8.9

# Install system dependencies and Docker CLI
RUN apt-get update && apt-get install -y curl build-essential ffmpeg libsm6 libxext6 docker.io make docker-compose && rm -rf /var/lib/apt/lists/*


# Install Poetry
RUN pip install "poetry==1.1.12"

# Set workdir
WORKDIR /workspace

# Copy only dependency files first for caching
COPY pyproject.toml poetry.lock ./

# Install all dependencies, including dev dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy the rest of the code
COPY . .

# Set default command
CMD ["bash"] 