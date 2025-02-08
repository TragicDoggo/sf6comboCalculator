# Use a stable Python version
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /sf6comboCalculator

# Copy everything into the container
COPY . .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the NiceGUI default port
EXPOSE 8080

# Run the app
CMD ["python", "main.py"]
