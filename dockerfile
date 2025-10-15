FROM python:3.11-slim

# Set the working directory inside container
WORKDIR /app

# Copy project files into the container
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app from inside app/ folder
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
