# we start from slim python images, which already has all the requirements for python
FROM python:3.8-slim-buster

# this will be working directory inside of the image
WORKDIR /usr/src/app

# copy python library requirements.txt
COPY requirements.txt ./

# install requirements
RUN pip install --no-cache-dir -r requirements.txt

# copy source files
COPY . .

ENV node=none

# execute application
CMD ["sh", "-c", "PYTHONHASHSEED=0 python ./app.py $node"]