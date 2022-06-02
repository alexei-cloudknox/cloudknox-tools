# User Discovery and Clean up

The python script goes throught the data storages, finds and cleans up user data. 

## Set up

The caller of the script has to have write/delete permission to the data storage to clean up the data. 

The config file has clearly described parameters for connections.

Except for blob data storage, a connection must be tunneled through a jump host. Blob storage, as it is S3 today, the communication is direct to the public host.

Example of SSH tunneling through a jump host:
| Storage Type |DB connection description                         | Connection setup                                             |
|---------------|-----------------------------------------|------------------------------------------------------------------------|
| data-db |  Postgres hi intensity DB(make a not of ingres port)| ssh -L 5433:postgres-hi.qa4.mciem.cloudknox.io:5432 jhmq4|
| data-db | Postgres low intensity DB|    ssh -L 5432:postgres-lo.qa4.mciem.cloudknox.io:5432 jhmq4|
| control-db | MySQL DB| ssh -L 3306:sql.qa4.mciem.cloudknox.io:3306 jhmq4|
| analytics-db |Trino DB| ssh -L 8080:datalake-sql-coordinator.qa4.mciem.cloudknox.io:8080 jhmq4|
  
  Note, jhmq4 is a jump host for the cluster described in ~/.ssh/config file
  
For S3 connection set, the required parameters can be found in ~/.aws/credentials. Access should be setup through STS.


## Python requirements

To run the script you must have python3 installed with the following libraries: json, trino, mysql, psycopg2, pyjq, minio

## Running the scrip

The script can be run in two modes: user information discovery and deletion.

To obtain current script option set, run it with --help option
````bash
alexei@samara:> python3 ./discover_user.py  --help
usage: discover_user.py [-h] [--config-file CONFIG_FILE]
                        [--search-area SEARCH_AREA] [--delete]

Process some integers.

optional arguments:
  -h, --help            show this help message and exit
  --config-file CONFIG_FILE
                        Config file
  --search-area SEARCH_AREA
                        Search areas. Any combinations of blob-storage,data-
                        db,control-db,analytics-db. Default are all.
  --delete              Delete found info
````

Make sure the script is run without delete option to verify that user info search criteria is entered correctly.

Search parameters example:
````json
  "org_id": "cukvKLU0Yqw939WofWWvy0zaMkBkojnJ",
  "auth_system_id": "377596131774",
  "auth_system_type": "AWS",

  "user_principal_name": "arn:aws:iam::377596131774:user/alexei",
  "user_name": "alexei",
  "user_email": "arn:aws:iam::377596131774:user/alexei",
````

## Examples Running the Script

### A Run for data-db:
Discovery mode: looking for user "arn:aws:iam::377596131774:user/alexei" in our data set

````bash
alexei@samara:> python3 ./discover_user.py  --config-file ./discover_user_config_s3.json --search-area data-db
User Entitlements Data:
	From Entitlements DB:
		Identity records
			461651 12404 arn:aws:iam::377596131774:user/alexei alexei 1 1 377596131774 None None 1 {'principalId': 'AIDAVP2T3XG7IEXLA5YZY', 'dateCreatedOn': 1651527040000} 1654193421968 2022-06-02 18:10:54.814369
		Grants Summary:
			num_tasks_granted: 10793,  num_high_risk_tasks_granted: 5743,  num_delete_tasks_granted: 1291,  num_resources_granted: 2476,  num_memberships: 1,  num_permissions: 62, 
			Total number of granted permissions: 192
	From Activities DB:
		Total number of events performed by identity: 0
		Total number of accesses with identity id: 0
		Total number of logins by identity id: 1
		Total number of tasks by identity id: 15
		Total number of session tokens by identity id: 0
	From Consumable Data DB:
		Total number of autopilot recommendations with identity id: 0
		Total number of services with advisor tasks with identity id: 2
		Total number of risk scores categories with identity id: 0
		Total number of task usages for identity id: 0
		Total number of privilege escalations for identity id: 0
````
Delete Mode: 
The same line but with added --delete argument will clean up the data from the data-db
````bash
````

### A Run for contol-db
Looking for user "geetaalapati@mciemgeetaalapatippe009.ccsctp.net" in control-db data set

````bash
alexei@samara:> python3 ./discover_user.py  --config-file ./discover_user_config_s3.json --search-area control-db
Data Access Control DB:
SELECT * FROM users WHERE  user_principal_name = 'geetaalapati@mciemgeetaalapatippe009.ccsctp.net'
	Found user record: 
		('daa7156e8845b571a0921df43d721f6c', '', '', 'geetaalapati@mciemgeetaalapatippe009.ccsctp.net', 'Geeta Alapati', 'Geeta Alapati', '', None, None, 'geetaalapati@mciemgeetaalapatippe009.ccsctp.net', 'ACTIVE', 'AAD', datetime.datetime(2022, 1, 27, 18, 56, 33), datetime.datetime(2022, 1, 27, 18, 56, 40))
	User created following orgs:
		('NSM0SX1Gvv8yNPAIUgg96NvnRAxX0afb', 'mciem-geetaalapati-ppe-009', 1, 'ACTIVE', 'daa7156e8845b571a0921df43d721f6c', 'AAD', datetime.datetime(2022, 3, 28, 18, 18, 1), datetime.datetime(2022, 1, 27, 18, 56, 33))
	User is not notified by sqs.
	User is not registered for email notifications.
	Organization is not listed in controller_requests table
	Organization is not listed in report_schedule table.
````
Same user, Deletion Mode:
````bash
alexei@samara:> python3 ./discover_user.py  --config-file ./discover_user_config_s3.json --search-area control-db --delete
Data Access Control DB:
SELECT * FROM users WHERE  user_principal_name = 'geetaalapati@mciemgeetaalapatippe009.ccsctp.net'
	Found user record: 
		('daa7156e8845b571a0921df43d721f6c', '', '', 'geetaalapati@mciemgeetaalapatippe009.ccsctp.net', 'Geeta Alapati', 'Geeta Alapati', '', None, None, 'geetaalapati@mciemgeetaalapatippe009.ccsctp.net', 'ACTIVE', 'AAD', datetime.datetime(2022, 1, 27, 18, 56, 33), datetime.datetime(2022, 1, 27, 18, 56, 40))
	User created following orgs:
		('NSM0SX1Gvv8yNPAIUgg96NvnRAxX0afb', 'mciem-geetaalapati-ppe-009', 1, 'ACTIVE', 'daa7156e8845b571a0921df43d721f6c', 'AAD', datetime.datetime(2022, 3, 28, 18, 18, 1), datetime.datetime(2022, 1, 27, 18, 56, 33))
	User is not notified by sqs.
	User is not registered for email notifications.
	Organization is not listed in controller_requests table
	Organization is not listed in report_schedule table.
DELETING from Data Access Control DB:
	No sqs notifications to delete
	No email notifications to delete
	No controller requests to update
	No reports schedule to update
	User is obfuscated in users table
````

### A Run for blob-storage and back up

Discovery mode: looking for user "arn:aws:iam::377596131774:user/alexei" in our raw data set
````bash
alexei@samara:> python3 ./discover_user.py  --config-file ./discover_user_config_s3.json --search-area blob-storage
User Raw Data and Backups:
	The first presents of alexei in entitlements/cbdMov64KyH7OHH4dYp0aRtR1m6IT2GV/377596131774/2022/4/12/22/1649801133742.json.gz
	The last presents of alexei in entitlements/cbdMov64KyH7OHH4dYp0aRtR1m6IT2GV/377596131774/2022/5/19/7/1652944328975.json.gz
	BackUp should be adjusted to keep only after last occurrence
````
Same user, Deletion Mode:
````bash
python3 ./discover_user.py  --config-file ./discover_user_config_s3.json --search-area blob-storage --delete 
User Raw Data and Backups:
        The first presents of alexei in entitlements/cbdMov64KyH7OHH4dYp0aRtR1m6IT2GV/377596131774/2022/4/12/22/1649801133742.json.gz
        The last presents of alexei in entitlements/cbdMov64KyH7OHH4dYp0aRtR1m6IT2GV/377596131774/2022/5/19/7/1652944328975.json.gz
        BackUp should be adjusted to keep only after last occurrence
DELETING from User Raw Data and Backups:
        Deleting all collection objects before cbdMov64KyH7OHH4dYp0aRtR1m6IT2GV/377596131774/2022/5/19
                Removing entitlements/cbdMov64KyH7OHH4dYp0aRtR1m6IT2GV/377596131774/2022/4/12/22/1649801133742.json.gz
                Removing entitlements/cbdMov64KyH7OHH4dYp0aRtR1m6IT2GV/377596131774/2022/4/12/23/1649804853907.json.gz
                ...
                Removing tasks/cbdMov64KyH7OHH4dYp0aRtR1m6IT2GV/377596131774/2022/4/12/20/1649796194614.json.gz
                Removing tasks/cbdMov64KyH7OHH4dYp0aRtR1m6IT2GV/377596131774/2022/4/12/20/1649796194722.json.gz
                Removing tasks/cbdMov64KyH7OHH4dYp0aRtR1m6IT2GV/377596131774/2022/4/12/20/1649796194835.json.gz
                Removing tasks/cbdMov64KyH7OHH4dYp0aRtR1m6IT2GV/377596131774/2022/4/12/20/1649796194858.json.gz
                ...
````
