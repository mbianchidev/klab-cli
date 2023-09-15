from datetime import datetime
import constants as const
import subprocess
import click
import os

script_dir = os.path.dirname(os.path.realpath(__file__))
logs_dir = os.makedirs(os.path.join(script_dir, const.LOGS_DIR), exist_ok=True)
aws_logs_file = os.path.join(logs_dir, const.AWS_LOG_FILE)
azure_logs_file = os.path.join(logs_dir, const.AZURE_LOG_FILE)
gcp_logs_file = os.path.join(logs_dir, const.GCP_LOG_FILE)
generic_logs_file = os.path.join(logs_dir, const.GENERIC_LOG_FILE)

def log(message: str, provider=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    if provider == const.AWS_PROVIDER:
        log_file = aws_logs_file
    elif provider == const.AZURE_PROVIDER:
        log_file = azure_logs_file
    elif provider == const.GCP_PROVIDER:
        log_file = gcp_logs_file
    else:
        log_file = generic_logs_file
    click.echo(log_entry)
    with open(log_file, 'a') as log_file:
        log_file.write(log_entry)


def check_parameters(**kwargs):
    for param_name, param_value in kwargs.items():
        if param_value is None or param_value == "":
            raise ValueError(f"Parameter '{param_name}' is None or blank. Please check the required parameters and try again.")


def execute_command(command: str, log_file_path: str, wait=False):
    with open(log_file_path, 'a') as log_file:
        # Utility function to run a command and wait for its completion
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                text=True,
                stdout=log_file,
                stderr=subprocess.STDOUT
            )

            # if process is in error state, wait for it to finish and raise an exception
            if process.poll() is not None and process.returncode != 0:
                process.wait()
                log(f"Error running the {command}.")

            if wait:
                log(f"Running the {command} in foreground.")
                process.wait()
                # return output
                return process.stdout.read()
            else:
                log(f"Running the {command} in background.")
        # Catching exceptions and raising them
        except subprocess.CalledProcessError as e:
            log(f"Error occurred during {command}. Please check the command and try again. {e}")
            raise e(process.returncode, command)
