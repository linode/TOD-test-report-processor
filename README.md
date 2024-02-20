# TOD test-report-processor 

This package is designed to be used specifically inside ECP machine as a cron job. The `main.py` script will process XML test reports and send a curl to TOD instance 

Pre requisite:
- Create .env file and set the following variables 


Usage:

Manually running the script:
`python main.py`

Setting it as cronjob:
1. Edit cront job: `crontab -e`
2. Add line: `0 */2 * * * cd /root/DX-Tests/test_report_uploader && python3 main.py >> logs.txt 2>&1`

Make sure to check for the latest updates and releases in the repository for any improvements or new features.


Feel free to contribute, report issues, or provide feedback to help enhance the functionality of this package for the DX team's testing processes.

## Contribution Guidelines

WiP
