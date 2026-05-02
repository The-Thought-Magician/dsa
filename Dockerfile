FROM ubuntu:latest
WORKDIR /app
RUN apt-get update && apt-get install -y curl
COPY . .
RUN echo "Step 01: Project setup complete"
