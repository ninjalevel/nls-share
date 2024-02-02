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
from typing import Optional,Dict,Any


class DockerManager:
    """Class to manage Docker operations including building images and tracking changes in Dockerfiles."""

    def __init__(
        self, 
        docker_file: str, 
        image_name: str, 
        force_rebuild: Optional[bool] = False, 
        env_vars: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize DockerManager with Dockerfile, image name, force rebuild flag, and environment variables."""
        self.docker_file = docker_file
        self.image_name = image_name
        self.force_rebuild = force_rebuild
        self.env_vars = env_vars or {}
        self.hash_file = f"{docker_file}_hash"

    def manage_docker_build(self) -> None:
        """Manages the Docker build process based on Dockerfile changes."""
        
        if self.has_dockerfile_changed() or self.force_rebuild:
            logger.info("Building or rebuilding Docker image.")
            self.build_docker_image()
            self.create_dockerfile_hash()
        else:
            logger.info("No changes detected in Dockerfile. No action needed.")

    def build_docker_image(self) -> bool:
        """Builds a Docker image from the initialized Dockerfile, including environment variables."""
        logger.info("Building Docker image...")
        try:
            build_command = ['docker', 'build', '-f', self.docker_file, '-t', self.image_name]
            # Include environment variables as build-args
            for key, value in self.env_vars.items():
                build_command.extend(['--build-arg', f'{key}={value}'])
            if self.force_rebuild:
                build_command.append('--no-cache')
            build_command.append('.')
            subprocess.run(build_command, check=True)
            logger.success("Docker image built successfully.")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to build Docker image: {e}")
            proceed = input("Enter for yes, Ctrl-c for no: ")
            if proceed == '':
                logger.info("Proceeding with the last known good image.")
                return True
            else:
                logger.info("Stopping the script.")
                return False
            
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


def execute_docker_class(
    docker_file: str, 
    image_name: str, 
    force_rebuild: bool = False, 
    env_vars: Optional[Dict[str, str]] = None
) -> None:
    """Execute Docker build management with environment variables."""
    
    docker_manager = DockerManager(docker_file, image_name, force_rebuild, env_vars)
    docker_manager.manage_docker_build()
    
def run_docker_manager(
    config: Dict[str, Any]
    ) -> None:
    """Executes Docker manager with configuration."""
    docker_file = config.get("docker_manager", {}).get("docker_file")
    image_name = config.get("docker_manager", {}).get("image_name")
    if docker_file and image_name:
        execute_docker_class(docker_file, image_name)
    else:
        logger.error("Docker file or image name not found in configuration.")

if __name__ == "__main__":
    config = toml.load("atmos.toml")
    force_rebuild = False
    docker_file = config["docker_manager"]["docker_file"]
    image_name = config["docker_manager"]["image_name"]
    execute_docker_class(docker_file, image_name,force_rebuild)

