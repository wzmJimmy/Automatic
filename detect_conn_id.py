import re
from webbrowser import get
import pandas as pd

from utils import scan_files

pat = re.compile("('|\")([\w{}]*)('|\")")


def get_connection_need(fname: str) -> list[str]:
    li_conn_id = []
    with open(fname) as f:
        for line in f:
            if line.startswith(' '):
                continue
            if "from airflow.operators.databricks_plugin import DatabricksRunJobOperator" in line:
                li_conn_id.append("databricks_di_infra")
            elif "_conn_id =" in line:
                conn_id = pat.search(line).group(2)
                li_conn_id.append(conn_id)
    return li_conn_id


def generate_conn_id_csv(dirc: str, csv_path: str = "file_to_conn_ids.csv") -> None:
    def cond(fname): return fname.endswith(".py")
    dags = scan_files(dirc, cond, True)
    dic_conn_ids = {k: get_connection_need(v) for k, v in dags.items()}
    df = pd.DataFrame.from_dict(dic_conn_ids, orient="index")
    df.to_csv(csv_path)


if __name__ == "__main__":
    from utils import get_base_dirc
    from os.path import join
    base = join(get_base_dirc(),"../di-airflow/")
    dag = join(base, "dags/listings/listings_pipeline_v3.py")
    li_conn_id = get_connection_need(dag)
    print(li_conn_id)
    generate_conn_id_csv(join(base, "dags"))
