from utils import (
    run_shell,
    constant_leap_waiter,
    dumps_json,
    read_json_file
)
from detect_conn_id import get_connection_need


def get_pod(prefix: str, id_only: bool = True) -> str:
    command = "kubectl get pods"
    li_pods = run_shell(command, True)
    for line in li_pods:
        if line.startswith(prefix):
            li = line.split()
            return li[0] if id_only else li
    return None


def kube_exec_bash(script: str, pod: str, hint: str = "processing..."):
    template = 'kubectl exec -it {} -- /bin/bash -c "{}"'
    print(hint)
    run_shell(template.format(pod, script))


def change_conn(pod: str, conn_id: str, dic: dict, add_only: str = False):
    cmd_delete = f"airflow connections -d --conn_id {conn_id}"
    li_cmd_add = [f"airflow connections -a --conn_id {conn_id}"]
    hint = "{} connection {} ..."

    if not add_only:
        kube_exec_bash(cmd_delete, pod, hint.format("Delete", conn_id))

    for key, v in dic.items():
        value = dumps_json(v, key == "conn_extra")
        li_cmd_add.append(f"--{key} {value}")

    kube_exec_bash(' '.join(li_cmd_add), pod, hint.format("Add", conn_id))


def _update_all_conn(pod: str, dname: str, li_conn: list[str]):
    dic = read_json_file(dname)

    for conn_id in li_conn:
        if conn_id in dic:
            change_conn(pod, conn_id, dic[conn_id])
        else:
            print(f"{conn_id} not exist in config file.")


def update_all_conn(pod: str, fconfig: str, fdag: str):
    pod_name = get_pod(pod)
    print(f"Pod name is {pod_name}.")

    li_conn = get_connection_need(fdag)
    print(f"Conn_ids are needed: {li_conn}")

    _update_all_conn(pod_name, fconfig, li_conn)
    print("update conn finished.")


def wait_pod_to_active(pod: str, start_sec: int = 150,
                       end_sec: int = 300, leap_sec: int = 20):
    def cond(time):
        status = get_pod(pod, False)[1]
        return status.startswith('1')

    constant_leap_waiter(
        start_sec=start_sec,
        end_sec=end_sec,
        leap_sec=leap_sec,
        cond=cond,
        verbose=True
    )
    print(f"Pod {pod} initiatied successfully.")


if __name__ == "__main__":
    from utils import get_base_dirc
    base = get_base_dirc()
    pod = get_pod("webserver-deployment")
    li_conn = ["databricks_di_infra", "di_aws_account",
            "main_aws_account", "main_aws_account_s3", "di_redshift_staging"]
    _update_all_conn(pod, base+"/config/stage_extra.json", li_conn)

    print(get_pod("webserver-deployment", False)[1].startswith('1'))
