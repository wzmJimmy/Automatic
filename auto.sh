#!/bin/bash
set -e # exit on first error

if [ "$1" == "" ]; then
    echo "Error: need one parameter for path of DAG."
    exit 1;
fi


BASE_FOLDER=$(dirname "$0")
echo $BASE_FOLDER
source $BASE_FOLDER/reference/sso_script

aws sso login --profile di-team
make docker-login-new  
airflow_sso init

# Leave a break for manual config.
read -p "Have you finish manual changing? [yes]/no: " resp
# "make build-dev" usually only need to run one time.
read -p "Make build-dev? yes/[no]: " build
build=${build:-no}
if [[ $build != "no" && $build != "n" ]]; then
    make build-dev
fi

make upgrade-dev
python3 $BASE_FOLDER/run.py wait_pod
kubectl get pods
python3 $BASE_FOLDER/run.py update_conn --dag "$1"
make webserver