FROM python:3.8-slim-buster

# Create a working directory.
RUN mkdir wd
WORKDIR /wd/

# Copy requirements
COPY requirements.txt /wd/

# Install requirements
RUN pip3 install -r requirements.txt

# Copy code
COPY app.py /wd/

# Command to run this program
CMD [ "gunicorn", "--workers=5", "--threads=1", "-b 0.0.0.0:8000", "app:server"]
