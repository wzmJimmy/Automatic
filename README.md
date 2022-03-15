# Automatic tool to setup gamma di-airflow environment locally

## Story
To test dags to run in gamma locally, there are two pain points:
- Find the conection_ids used by the dag.
- Update the corresponding conection_ids according to gamma environment.

Moreover, frequently checking minikube pod status and running the same commands are tedious.

Hence, I built this small tool to automate this process.

## Usage
This tool base on the Makefile in di-airflow reporsitory, hence it needs to run under that directory. (Where the module is cloned does not matter)

1. Put the gamma config json file into the ./config directory with following structure:
 
    `{ "conn_id1": {
        "conn_type": "databricks",
        "conn_extra": {...}
    }, ...}`

2. Run the following shell command to start:

    `bash ./path_to_tool/auto.sh [path of the dag]`
- if path of dag is not provided, It runs all commands for a local airflow environment, monitor the minikube pod finish starting, and satrt the webserver.
- If it's provided, It will additonally check the conn_ids used by the dag and update it according to the gamma configuration.

## Extra
1. Run `make delete-dev` before rerun this tool.
2. The conn_ids detection is based on current naming convention.
3. The gamma config file reading is one naive solution. Once the mapping between env-values yaml file and existing conn_id is clear, it can be further automized.



