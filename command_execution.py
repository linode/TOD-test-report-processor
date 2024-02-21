import subprocess


def execute_command(args):
    try:
        process = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return process
    except subprocess.CalledProcessError as e:
        print(f"Error executing command with args: {args}, with error: {e}")
