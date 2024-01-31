## Geodesic Module Initialization

This directory contains the configuration and scripts to build and run a Docker container based on the Geodesic module.

### Dockerfile

The `Dockerfile` is used to build a Docker image with custom configurations:

- It is based on the `cloudposse/geodesic` image.
- The `BANNER` environment variable is set to a default value, which can be overridden at build time.
- The `AWS_PROFILE` environment variable is set to "default-profile" by default, which can be overridden.
- The `AWS_DEFAULT_REGION` environment variable is set to "default-region" by default, which can be overridden.

### docker_build

The `docker_build` script is a simple command that builds the Docker image using the `Dockerfile` in the current directory and tags it as `geodesic-test-image`.

### docker_run.py

The `docker_run.py` script is a Python program that performs several tasks:

- Checks for the presence of the AWS CLI and Docker.
- Fetches AWS profiles and allows the user to select one.
- Fetches Docker images with a specific prefix and allows the user to select one to run.
- Sets environment variables based on the selected AWS profile.
- Runs a Docker container with the selected image and sets up volume mappings.
- The script also replaces placeholders in volume paths with the corresponding environment variable values.
- It prompts the user for confirmation before running the Docker command.

### Usage

To build the Docker image, run the `docker_build` script:
```bash
docker build -t geodesic-test-image .
```

To run the Docker container, execute the `docker_run.py` script:
```bash
python docker_run.py
```

You will be prompted to select an AWS profile and a Docker image, after which the Docker container will start with the specified configurations.
