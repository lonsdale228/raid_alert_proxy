# Use an official lightweight Python image.
FROM python:3.12.6-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port that Flask will run on
EXPOSE 5000

# Set the default command to run the application
CMD ["python", "app.py"]
