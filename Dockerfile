# force amd64 platform: ensures the image is built for Cloud Run's architecture, regardless of your Mac's CPU.
FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server file
COPY server.py .

# Create a volume for persistent todo storage
VOLUME ["/app/data"]

# Expose the SSE port
EXPOSE 8050

# Set environment variable for data directory
ENV TODOS_FILE=/app/data/todos.json

# Run the server
CMD ["python", "server.py"]