#!/bin/bash
# apt-alarm 이미지가 빌드, apt-alarm-container라는 이름의 Docker 컨테이너가 백그라운드에서 실행
docker build -t apt-alarm:latest -f docker/Dockerfile .
docker run -d -p 8000:8000 --name apt-alarm-container apt-alarm:latest
