#!/usr/bin/env bash

docker run -it --network=host -v "$PWD:/app" -v "/tmp/.X11-unix:/tmp/.X11-unix" -e "DISPLAY=$DISPLAY" -v "$HOME/.Xauthority:/root/.Xauthority" --privileged python:buster /bin/bash
