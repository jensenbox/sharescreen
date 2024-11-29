FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependencies
COPY pyproject.toml .

# Install dependencies
RUN pip install --no-cache-dir .

# Copy application files
COPY . .

# Command to run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8088", "--reload"]
