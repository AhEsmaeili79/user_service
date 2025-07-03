# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /user-service

# Copy the requirements.txt file into the container at /user-service
COPY requirements.txt /user-service/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Upgrade pip
RUN pip install --upgrade pip

# Copy the rest of application code into the container at /user-service
COPY . .

# Expose the port FastAPI application will run on
EXPOSE 8001

# Command to run FastAPI application using Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]