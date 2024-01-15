# Use a lightweight base image for the Python app
FROM python:3.12-slim AS app_base

# Set the working directory for the Python app
WORKDIR /app

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install dependencies for the Python app
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Build the Python app
FROM app_base AS app

# Copy the entire application for the Python app
COPY . .

# Expose the port on which the Python app will run
EXPOSE 5000

# Command to run the Python app
CMD ["python", "api.py"]
