# TOD test-report-processor 

This package is designed to be used specifically inside ECP machine as a cron job. The `main.py` script will process XML test reports and send a curl to TOD instance 

**Pre requisite:**
- Create and edit .env file and set the following variables:
```
# TOKENS
LINODE_CLI_TOKEN=
LINODE_CLI_OBJ_ACCESS_KEY=
LINODE_CLI_OBJ_SECRET_KEY=

# Linode Object Storage env variables
CLUSTER='us-southeast-1'
BUCKET='dx-test-results'

# TOD URL
URL="http://198.19.5.79:7272/builds/"

# Test Report Variables
TEAM_NAME='DX Team'
```


**Usage:**

Manually running the script:
`python main.py`

Running the script will download all the report files from object storage and store inside local directory (e.g. `/reports`)
Logs generated during script will be stored inside local direotory (e.g. `/logs`)


Setting it as cronjob in ECP machine:
1. SSH to ECP machine, `ssh root@198.19.5.95`
2. Edit cront job, `crontab -e`
3. Add line to the file, `0 */2 * * * cd /root/DX-Tests/test_report_uploader && python3 main.py >> logs.txt 2>&1`

Make sure to check for the latest updates and releases in the repository for any improvements or new features.

