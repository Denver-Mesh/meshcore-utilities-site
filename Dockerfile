FROM ubuntu:latest
LABEL authors="nate"

ENTRYPOINT ["top", "-b"]
