#!/bin/bash
docker build -t apt-alarm .
docker run -p 8000:8000 apt-alarm
