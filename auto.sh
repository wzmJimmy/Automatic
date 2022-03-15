#!/bin/bash
set -e # exit on first error

BASE_FOLDER=$(dirname "$0")
echo $BASE_FOLDER

select_pod(){
    pod_name=$(kubectl get pods | grep -v NAME | fzf -1 -0 -q "$1" | tr -s ' ' | cut -d' ' -f1 );
    echo $pod_name
}

read_aws_sso_token(){
  for i in $HOME/.aws/sso/cache/*; do
    if [[ ! $i =~ "botocore-client-id-us-east-1.json" ]]; then
      echo $(jq -r .accessToken $i)
    fi
  done
}

request_aws_sso_temp_token() {
  sso_token=$(read_aws_sso_token)
  aws --profile di-team sso get-role-credentials --role-name Administrator --account-id 819385756561 --access-token $sso_token
}

airflow_sso_init() {
  connection_id=di_aws_account

  echo -e "\033[0;32m Get SSO tokens ..."
  aws_raw_token=$(request_aws_sso_temp_token)
  # Parse temporary tokens from the respond
  access_key=$(echo $aws_raw_token | jq -r .roleCredentials.accessKeyId)
  secret_key=$(echo $aws_raw_token | jq -r .roleCredentials.secretAccessKey)
  session_key=$(echo $aws_raw_token | jq -r .roleCredentials.sessionToken)

  echo "Update Development values ..."
  values_file="kube-di-airflow/env-values/values-development.yaml"
  # replace the whole line matched specific key with the new key-value pair (In the yaml file.)
  sed -i '' '/awsAccessKeyId/c\
  awsAccessKeyId: '$access_key'
' $values_file
  sed -i '' '/awsSecretAccessKeyId/c\
  awsSecretAccessKeyId: '$secret_key'
' $values_file
  sed -i '' '/awsSessionToken/c\
  awsSessionToken: '$session_key'
' $values_file
}

make minikube
colima start

aws sso login --profile di-team
make docker-login-new  
airflow_sso_init

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

if [ "$1" != "" ]; then
    python3 $BASE_FOLDER/run.py update_conn --dag "$1"
fi
make webserver