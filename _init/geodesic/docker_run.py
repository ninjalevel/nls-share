
# Core library imports
import argparse
import os
import re
import shutil
import subprocess
import json

# Third-party library imports
from icecream import ic  # type: ignore
from loguru import logger
import toml

# Local imports
from docker_manager_class import execute_docker_class


# Logger configuration
logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")

def parse_cli_arguments():
    parser = argparse.ArgumentParser(description='Run Docker Manager.')
    parser.add_argument('--force-rebuild', action='store_true', help='Force a full rebuild of the Docker image.')
    return parser.parse_args()

def check_system_path_for_tool(tool_name: str) -> bool:
    """Verifies if a specified tool is installed and accessible in the system's PATH."""
    logger.info(f"Verifying accessibility of {tool_name} in system PATH...")
    result = shutil.which(tool_name) is not None
    logger.info(f"{tool_name} is accessible.") if result else logger.error(f"{tool_name} is not accessible in system PATH.")
    return result

def execute_subprocess(command: list) -> str:
    """
    Runs a command in the shell and gives back the result.

    The function takes a list that forms a shell command. For instance, ["aws", "configure", "list-profiles"]
    would list all AWS profiles.

    It runs the command and waits for it to finish. The output is then cleaned up (extra spaces removed) and
    returned as a string.
    """
    return subprocess.check_output(command).decode().strip()

def get_aws_profiles() -> list:
    """Get a list of AWS profiles."""
    if not check_system_path_for_tool("aws"):
        raise Exception("AWS CLI not found. Please install it.")
    logger.info("Fetching AWS profiles...")
    profiles = execute_subprocess(["aws", "configure", "list-profiles"]).replace('\r\n', '\n').split('\n')
    logger.info(f"Found {len(profiles)} AWS profiles.")
    return profiles

def select_from_list(items: list, prompt: str) -> str:
    """
    Asks the user to choose an item from a list, typically a list of AWS profiles or Docker images.

    The function displays each item in the list with a number next to it. For example, if the list contains
    AWS profiles, it might display something like:
    1. default
    2. test-profile
    3. prod-profile

    Then it shows the prompt message (e.g., "Select an AWS profile by number: ") and waits for the user to enter a number.

    The user's choice is converted to an index (by subtracting 1 from it) and used to get the corresponding
    item from the list. This item is then returned by the function.
    """
    for i, item in enumerate(items):
        print(f"{i+1}. {item}")
    selected = int(input(prompt)) - 1
    return items[selected]

def set_aws_environment_variables():
    """Set AWS related environment variables."""
    aws_profile = select_from_list(get_aws_profiles(), "Select an AWS profile by number: ")
    aws_default_region = execute_subprocess(["aws", "configure", "get", "region", "--profile", aws_profile])
    os.environ["AWS_PROFILE"] = aws_profile
    os.environ["AWS_DEFAULT_REGION"] = aws_default_region

    # Check if the selected AWS profile is active
    try:
        execute_subprocess(["aws", "sts", "get-caller-identity", "--profile", aws_profile])
        logger.info(f"AWS profile {aws_profile} is active.")
    except subprocess.CalledProcessError:
        logger.error(f"AWS profile {aws_profile} is not active. Please check its configuration.")
        raise

def get_docker_images_with_prefix(prefix: str) -> list:
    """Fetch Docker images that start with a given prefix and allow user to select an image with retries for wrong choices."""
    if not check_system_path_for_tool("docker"):
        raise Exception("Docker not found. Please install it.")
    logger.info("Fetching Docker images...")
    images = execute_subprocess(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"]).split('\n')
    filtered_images = [image for image in images if image.startswith(prefix)]
    if not filtered_images:
        raise Exception(f"No Docker images found with prefix '{prefix}'.")

    while True:
        for i, item in enumerate(filtered_images):
            print(f"{i+1}. {item}")
        try:
            selected = int(input("Select a Docker image by number: ")) - 1
            return [filtered_images[selected]]  # Change made here to return a list instead of a string
        except (ValueError, IndexError):
            print("Invalid selection, please try again.")

def replace_local_env_variables_win(volume: str) -> str:
    """
    Replaces `$env:VAR_NAME` placeholders in the input string with the actual values of the corresponding
    environment variables for windows machines.
    """
    return re.sub(r'\$env:([A-Za-z0-9_]+)', lambda match: os.environ.get(match.group(1), ''), volume)

def run_docker(volumes: list, container_name=None, image_prefix="geodesic", banner="NLS-Geodesic"):
    """Run a Docker container with specified volumes."""
    logger.info("Running Docker...")
    selected_image = select_from_list(get_docker_images_with_prefix(image_prefix), "Select a Docker image by number: ")
    if container_name is None:
        container_name = selected_image.split(':')[0].replace('/', '_')

    # Ensuring environment variables in volume paths are replaced before validation
    volumes = [replace_local_env_variables_win(volume) for volume in volumes]
    volume_commands = [item for volume in volumes for item in ["--volume", volume]]

    docker_command = [
        "docker", "run", "-it", "--rm", "--name", container_name,
        "--env-file", "atmos.env.list",  # Add env file set to atmos.env.list
        "-e", f"BANNER={banner}",  # Use banner variable
        "-e", "AWS_PROFILE=" + os.environ["AWS_PROFILE"],
        "-e", "AWS_DEFAULT_REGION=" + os.environ["AWS_DEFAULT_REGION"]
    ] + volume_commands + [selected_image, "--login"]
    logger.info("Executing Docker command: " + ' '.join(docker_command))
    confirmation = input("Press Enter to run the Docker command or type 'no' to cancel: ").lower()
    if not confirmation or confirmation == "yes":
        subprocess.run(docker_command)
        logger.info("Docker run completed.")
    else:
        logger.info("Docker command execution cancelled by user.")

def check_local_volume_bindings(volume_bindings: list):
    """
    Checks if the local paths in volume bindings exist after replacing environment variables.
    Raises FileNotFoundError if a path does not exist.
    """
    for binding in volume_bindings:
        local_path = replace_local_env_variables_win(binding["local_path"])
        if not os.path.exists(local_path):
            logger.error(f"Local path does not exist: {local_path}")
            raise FileNotFoundError(f"Local path does not exist: {local_path}")
        else:
            logger.info(f"Local path verified: {local_path}")

if __name__ == "__main__":
    args = parse_cli_arguments()

    # Import Config
    config = toml.load("atmos.toml")

    # Set Variables from Config
    docker_file = config["docker_manager"]["docker_file"]
    image_name = config["docker_manager"]["image_name"]
    image_prefix = config["docker_manager"]["image_prefix"]  # Set image_prefix variable
    banner = config["environment"]["banner"]  # Set banner variable
    env_vars = config.get("environment_variables", {})  # Extract environment variables from config

    execute_docker_class(docker_file, image_name)
    # execute_docker_class(docker_file, image_name, env_vars)

    set_aws_environment_variables()

    volume_bindings = config["run_docker"]["volume_bindings"]
    check_local_volume_bindings(volume_bindings)

    volumes = [f'{binding["local_path"]}:{binding["container_path"]}' for binding in volume_bindings]

    # Pass image_prefix and banner to run_docker
    run_docker(volumes=volumes, image_prefix=image_prefix, banner=banner)
