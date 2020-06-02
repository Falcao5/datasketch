set ATCS_BML_DIR="../../../"
set HOSTNAME="my_awesome_hostname"
set PORT=0000
set DEPLOY_DESTINATION="/home/datasketch/"
set USER="datasketch"

scp -P %PORT% %ATCS_BML_DIR%dataset_provision.py %USER%@%HOSTNAME%:%DEPLOY_DESTINATION%
scp -P %PORT% %ATCS_BML_DIR%hyperloglog_execution.py %USER%@%HOSTNAME%:%DEPLOY_DESTINATION%
scp -P %PORT% %ATCS_BML_DIR%minhash_execution.py %USER%@%HOSTNAME%:%DEPLOY_DESTINATION%