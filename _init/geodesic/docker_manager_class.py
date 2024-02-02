"""
This script is designed to manage Docker operations. 
It includes functionality to build Docker images, track changes in Dockerfiles, and rebuild images if changes are detected. 
It does this by creating a hash of the Dockerfile and storing it. 
When the script is run, it checks if the Dockerfile has changed by comparing its current hash to the stored hash. 
If changes are detected, it rebuilds the Docker image and updates the stored hash.
"""
import hashlib
import subprocess
from loguru import logger
import os
import toml
import json


import docker_manager_class

class DockerManager:
    """Class to manage Docker operations including building images and tracking changes in Dockerfiles."""

    def __init__(self, docker_file, force_rebuild=False):
        """Initialize with the Dockerfile and its corresponding hash file path."""
        self.docker_file = docker_file
        self.hash_file = f"{docker_file}_hash"
        self.force_rebuild = force_rebuild


    def manage_docker_build(self, image_name):
        """Manages the Docker build process based on the existence and comparison of Dockerfile hashes."""
        if self.has_dockerfile_changed() or self.force_rebuild:
            logger.info("Building or rebuilding Docker image.")
            self.build_docker_image(image_name)
            self.create_dockerfile_hash()
        else:
            logger.info("No changes detected in Dockerfile. No action needed.")


            
    def build_docker_image(self, image_name):
        """Builds a Docker image from the initialized Dockerfile."""
        logger.info("Building Docker image...")
        try:
            build_command = ['docker', 'build', '-f', self.docker_file, '-t', image_name, '.']
            if self.force_rebuild:
                build_command.insert(2, '--no-cache')
            subprocess.run(build_command, check=True)
            logger.success("Docker image built successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to build Docker image: {e}")
            
    def create_dockerfile_hash(self):
        """Creates a hash of the Dockerfile and stores it in a separate hash file."""
        logger.info("Creating hash of the Dockerfile...")
        try:
            with open(self.docker_file, 'rb') as file:
                file_hash = hashlib.sha256(file.read()).hexdigest()
            with open(self.hash_file, 'w') as hash_file:
                hash_file.write(file_hash)
            logger.success("Hash of Dockerfile created and stored successfully.")
        except IOError as e:
            logger.error(f"Error in creating Dockerfile hash: {e}")

    def has_dockerfile_changed(self):
        """Checks if the Dockerfile has changed by comparing its current hash to the stored hash."""
        logger.info("Checking if Dockerfile has changed...")
        if not os.path.exists(self.hash_file):
            return True  # If hash file doesn't exist, assume Dockerfile has changed
        try:
            with open(self.docker_file, 'rb') as file:
                current_hash = hashlib.sha256(file.read()).hexdigest()
            with open(self.hash_file, 'r') as hash_file:
                stored_hash = hash_file.read()
            return current_hash != stored_hash
        except IOError as e:
            logger.error(f"Error in checking Dockerfile change: {e}")
            return True  # Assume change if there's an error reading the files


def execute_docker_class(docker_file, image_name, force_rebuild=False):
    """Executes Docker build management. REPLACED!!!!"""
    docker_manager = DockerManager(docker_file, force_rebuild)
    docker_manager.manage_docker_build(image_name)
    
def run_docker_manager(config):
    """Runs the Docker manager with configuration."""
    docker_file = config["docker_manager"]["docker_file"]
    image_name = config["docker_manager"]["image_name"]
    execute_docker_class(docker_file, image_name)


if __name__ == "__main__":
    config = toml.load("atmos.toml")
    force_rebuild = False
    docker_file = config["docker_manager"]["docker_file"]
    image_name = config["docker_manager"]["image_name"]
    execute_docker_class(docker_file, image_name,force_rebuild)

