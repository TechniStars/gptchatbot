# Use the official Python 3.8 image from Docker Hub
FROM python:3.8

# Set the working directory to /
WORKDIR /qa-chatbot-synerise

# Add a new user and group with specified UID and GID
RUN groupadd -g 1000 mygroup && useradd -u 1000 -g mygroup -m myuser

# Set the ownership of the directory to the newly created user
RUN chown -R myuser:mygroup /qa-chatbot-synerise

# Switch to the newly created user
USER myuser

# Copy the entire current directory into the container
COPY . /qa-chatbot-synerise/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run main.py when the container launches
CMD ["python", "main.py"]
