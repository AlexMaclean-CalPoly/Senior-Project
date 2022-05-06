FROM python:3.7-buster
#FROM node

RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -
RUN apt-get install -y nodejs

RUN apt-get update
RUN apt-get install --yes libsndfile1 ffmpeg
RUN pip install Cython nemo_toolkit[all]

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

#ENTRYPOINT ["node", "--version"]
#ENTRYPOINT ["python3", "--version"]
ENTRYPOINT ["npm", "run", "main"]