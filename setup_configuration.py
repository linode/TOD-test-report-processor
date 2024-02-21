import subprocess

import os
from dotenv import load_dotenv

load_dotenv()


def check_and_install_linode_cli():
    # Load environment variables from .env file

    required_env_vars = ["LINODE_CLI_TOKEN", "LINODE_CLI_OBJ_ACCESS_KEY", "LINODE_CLI_OBJ_SECRET_KEY"]

    missing_vars = [var for var in required_env_vars if var not in os.environ]
    if missing_vars:
        print("Error: The following environment variables are not set:")
        for var in missing_vars:
            print(f"- {var}")
        exit(1)

    try:
        subprocess.run(["/usr/local/bin/linode-cli", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        print("linode-cli is not installed. Please make sure Linode CLI is installed...")
