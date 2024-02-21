import requests

latest_release_urls = ["https://api.github.com/repos/linode/linode-cli/releases/latest", "https://api.github.com/repos/linode/linode_api4-python/releases/latest", "https://api.github.com/repos/linode/linodego/releases/latest", "https://api.github.com/repos/linode/terraform-provider-linode/releases/latest", "https://api.github.com/repos/linode/packer-plugin-linode/releases/latest", "https://api.github.com/repos/linode/ansible_linode/releases/latest"]

def get_release_version(file_name):
    url = ""
    if 'cli' in file_name:
        url = latest_release_urls[0]
    elif 'sdk' in file_name:
        url = latest_release_urls[1]
    elif 'linodego' in file_name:
        url = latest_release_urls[2]
    elif 'terraform' in file_name:
        url = latest_release_urls[3]
    elif 'packer' in file_name:
        url = latest_release_urls[4]
    elif 'ansible' in file_name:
        url = latest_release_urls[5]
    else:
        "unknown log type"
        
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors

        release_info = response.json()
        version = release_info["tag_name"]

        # Remove 'v' prefix if it exists
        if version.startswith("v"):
            version = version[1:]

        return str(version)

    except requests.exceptions.RequestException as e:
        print("Error:", e)
    except KeyError:
        print("Error: Unable to fetch release information from GitHub API.")


def upload_encoded_xml_file(url, payload, headers):
    response = requests.post(url, data=payload, headers=headers)
    return response
