import base64
import os
import json
import xml.etree.ElementTree as ET
import datetime
import logging


from linode_commands import get_list_command, get_download_command, get_remove_command
from command_execution import execute_command
from api_interaction import upload_encoded_xml_file, get_release_version
from setup_configuration import check_and_install_linode_cli


# Configure logging
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M")
log_file_path = f"logs/{timestamp}log.log"
logging.basicConfig(filename=log_file_path, level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')


def log_and_print(message, level=logging.INFO):
    logging.log(level, message)
    print(message)


def get_software_name(file_name: str):
    if 'cli' in file_name:
        return "linode-cli"
    elif 'sdk' in file_name:
        return "linode_api4"
    elif 'linodego' in file_name:
        return "linodego"
    elif 'terraform' in file_name:
        return "linode-terraform"
    elif 'packer' in file_name:
        return "packer"
    elif 'ansible' in file_name:
        return "ansible_linode"
    elif 'py-metadata' in file_name:
        return "py-metadata"
    elif 'go-metadata' in file_name:
        return "go-metadata"
    else:
        "unknown software type"

# TOD rejects any xml report with multiple testsuite variable, this function translate xml to acceptable version by TOD
def change_xml_report_to_tod_acceptable_version(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    if len(root.findall("testsuite")) > 1:
        testsuites_element = root

        # total
        total_tests = int(testsuites_element.get('tests')) if testsuites_element.get('tests') is not None else 0
        total_failures = int(testsuites_element.get('failures')) if testsuites_element.get('failures') is not None else 0
        total_errors = int(testsuites_element.get('errors')) if testsuites_element.get('errors') is not None else 0
        total_skipped = int(testsuites_element.get('skipped')) if testsuites_element.get('skipped') is not None else 0

        # Create a new <testsuites> element with aggregated values
        new_testsuites = ET.Element("testsuites")
        new_testsuites.set("tests", str(total_tests))
        new_testsuites.set("failures", str(total_failures))
        new_testsuites.set("errors", str(total_errors))
        new_testsuites.set("skipped", str(total_skipped))


        # Create a new <testsuite> element under <testsuites>
        new_testsuite = ET.SubElement(new_testsuites, "testsuite", attrib=testsuites_element.attrib)

        for testcase in root.findall('.//testcase'):
            new_testcase = ET.SubElement(new_testsuite, "testcase", attrib=testcase.attrib)
            for child in testcase:
                new_testcase.append(child)

        branch_name = ET.SubElement(new_testsuites, 'branch_name')
        branch_name.text = root.find('branch_name').text
        branch_name = ET.SubElement(new_testsuites, 'gha_run_id')
        branch_name.text = root.find('gha_run_id').text
        branch_name = ET.SubElement(new_testsuites, 'gha_run_number')
        branch_name.text = root.find('gha_run_number').text
        branch_name = ET.SubElement(new_testsuites, 'release_tag')
        branch_name.text = root.find('release_tag').text

        # Save the new XML to a file
        try:
            new_tree = ET.ElementTree(new_testsuites)
            new_tree.write(file_path, encoding="UTF-8", xml_declaration=True)

            log_and_print(f"{timestamp}:XML content successfully over-written to " + file_path)
        except Exception as e:
            log_and_print(f"{timestamp}:Error writing XML content:", str(e))


# Download all xml test reports
def download_and_upload_xml_files(cluster, bucket, url):
    list_process = execute_command(get_list_command(cluster))

    lines_of_all_files = list_process.stdout.decode().split('\n')

    xml_files = []

    team_name = os.environ.get('TEAM_NAME')

    current_dir = os.getcwd()
    # Define the report directory
    report_dir = os.path.join(current_dir, "reports")

    for line in lines_of_all_files:
        if bucket in line and line.endswith(".xml"):
            xml_file = line.split("/")[-1]
            xml_files.append(xml_file)

    # Upload each xml file to TOD
    for file in xml_files:
        file_path = os.path.join(report_dir, file)
        # Construct the full path to the XML file
        result = execute_command(get_download_command(cluster, bucket, file, file_path))

        change_xml_report_to_tod_acceptable_version(file_path)
        print(file_path)
        # Parse the XML file
        tree = ET.parse(file_path)
        root = tree.getroot()
        branch_name_element = root.find('branch_name')
        gha_run_id_element = root.find('gha_run_id')
        gha_run_number_element = root.find('gha_run_number')
        release_tag_element = root.find('release_tag')

        branch_name_value = branch_name_element.text if branch_name_element is not None else "N/A"
        gha_id_value = gha_run_id_element.text if gha_run_id_element is not None else "N/A"
        gha_number_value = gha_run_number_element.text if gha_run_number_element is not None else "N/A"
        release_version_value = release_tag_element.text if release_tag_element is not None else get_release_version(file)

        f = open(file_path, "r")
        lines = f.read()
        encoded_file = str(base64.b64encode(lines.encode('utf-8')).decode('utf-8'))

        # get softwarename
        software_name = get_software_name(file_name=file)

        build_name = software_name

        testsuite_failures = root.find('testsuite').get('failures') if root.find('testsuite') is not None else 0
        failures = root.find('failures').text if root.find('failures') is not None else 0
        value = testsuite_failures or failures

        pass_value = int(value) == 0

        tag_value = "GHA ID: " + gha_id_value + "   Run ID: " + gha_number_value if gha_id_value and gha_number_value else " "

        # Define the data as a dictionary
        data = {
            "team": team_name,
            "softwareName": software_name,
            "semanticVersion": release_version_value,
            "buildName": build_name,
            "pass": pass_value,
            "xunitResults": [encoded_file],
            "tag": tag_value,
            "branchName": branch_name_value,
        }

        headers = {"Content-Type": "application/json"}

        data_json = json.dumps(data)

        response = upload_encoded_xml_file(url, data_json, headers)

        # Check the response
        if response.status_code == 201:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_and_print(f"{timestamp}: {file} uploaded to TOD successfully...")

            # delete the xml files from the object storage because it will create a duplicate entry in TOD
            result = execute_command(get_remove_command(cluster, bucket, file))

            if result.returncode == 0:
                log_and_print(f"{timestamp}: {file} deleted from object storage...")
            else:
                log_and_print(f"{timestamp}: Error deleting {file} from object storage. Command returned non-zero exit code: {result.returncode}", level=logging.ERROR)

        else:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_and_print(f"{timestamp}: POST request for file {file} failed with status code: {response.status_code}", level=logging.ERROR)


def main():
    try:
        cluster = os.environ.get("CLUSTER")
        bucket = os.environ.get("BUCKET")
        url = os.environ.get("URL")

        check_and_install_linode_cli()
        download_and_upload_xml_files(cluster, bucket, url)

    except Exception as e:
        log_and_print(f"An error occurred in the main function: {str(e)}", level=logging.ERROR)


if __name__ == "__main__":
    main()
