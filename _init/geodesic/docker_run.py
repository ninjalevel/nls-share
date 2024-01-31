import os
import subprocess
import shutil
from loguru import logger
import re
import toml
from docker_manager_class import execute_docker_class
import argparse

# Logger configuration
logger.add("debug.log", format="{time} {level} {message}", level="DEBUG")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run Docker Manager.')
    parser.add_argument('--force-rebuild', action='store_true', help='Force a full rebuild of the Docker image.')
    return parser.parse_args()

def check_tool_availability(tool_name: str) -> bool:
    """Check the availability of a given tool. Currently checks for 'aws cli' and 'docker cli'."""
    logger.info(f"Checking for {tool_name}...")
    result = shutil.which(tool_name) is not None
    logger.info(f"{tool_name} found.") if result else logger.error(f"{tool_name} not found.")
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
    if not check_tool_availability("aws"):
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
    """Fetch Docker images that start with a given prefix."""
    if not check_tool_availability("docker"):
        raise Exception("Docker not found. Please install it.")
    logger.info("Fetching Docker images...")
    images = execute_subprocess(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"]).split('\n')
    return [image for image in images if image.startswith(prefix)]

def replace_env_variables(volume: str) -> str:
    """Replace environment variable placeholders in a volume string."""
    return re.sub(r'\$env:([A-Za-z0-9_]+)', lambda match: os.environ.get(match.group(1), ''), volume)

def validate_local_paths(volumes: list) -> None:
    """
    Validates if the local paths specified in the volumes exist.
    If a path does not exist, it raises a FileNotFoundError with a clear message.
    """
    missing_paths = [volume.split(":")[0] for volume in volumes if not os.path.exists(volume.split(":")[0])]
    if missing_paths:
        missing_paths_str = "\n".join(missing_paths)
        raise FileNotFoundError(f"The following local path(s) do not exist:\n{missing_paths_str}")

def run_docker(volumes: list, container_name=None, image_prefix="geodesic"):
    """Run a Docker container with specified volumes."""
    logger.info("Running Docker...")
    selected_image = select_from_list(get_docker_images_with_prefix(image_prefix), "Select a Docker image by number: ")
    if container_name is None:
        container_name = selected_image.split(':')[0].replace('/', '_')

    volumes = [replace_env_variables(volume) for volume in volumes]
    validate_local_paths(volumes)
    
    volume_commands = [item for volume in volumes for item in ["--volume", volume]]
    
    docker_command = [
        "docker", "run", "-it", "--rm", "--name", container_name,
        "-e", "BANNER=NLS-Geodesic",  #TODO: MOVE THIS TO CONFIG
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


if __name__ == "__main__":
    args = parse_arguments()
    config = toml.load("atmos.toml")
    
    docker_file = config["docker_manager"]["docker_file"]
    image_name = config["docker_manager"]["image_name"]
    # force_rebuild = True
    
    execute_docker_class(docker_file, image_name,args.force_rebuild)
    
    set_aws_environment_variables()
    
    run_docker(volumes=config["run_docker"]["volumes"])


