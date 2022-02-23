import os
import argparse
from detect_conn_id import (get_connection_need,
                            generate_conn_id_csv)
from kube_operations import (wait_pod_to_active,
                             update_all_conn)
from utils import get_base_dirc

BASE = get_base_dirc()

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(required=True)

parser_conns = subparsers.add_parser('conns')
parser_conns.add_argument('--fname', dest='fname', type=str, required=True)
parser_conns.set_defaults(func=lambda **kvargs: print(get_connection_need(**kvargs)))

parser_conn_csv = subparsers.add_parser('conn_csv')
parser_conn_csv.add_argument('--dirc', dest='dirc', type=str, required=True)
parser_conn_csv.add_argument('--csv', dest='csv_path', type=str, default="file_to_conn_ids.csv")
parser_conn_csv.set_defaults(func=generate_conn_id_csv)

parser_update_conn = subparsers.add_parser('update_conn')
parser_update_conn.add_argument('--pod', dest='pod', type=str, default="webserver-deployment")
parser_update_conn.add_argument('--config', dest='fconfig', type=str, default=os.path.join(BASE,"config/stage_extra.json"))
parser_update_conn.add_argument('--dag', dest='fdag', type=str, required=True)
parser_update_conn.set_defaults(func=update_all_conn)


parser_wait_pod = subparsers.add_parser('wait_pod')
parser_wait_pod.add_argument('--pod', dest='pod', type=str, default="webserver-deployment")
parser_wait_pod.add_argument('--start', dest='start_sec', type=int, default=60)
parser_wait_pod.add_argument('--end', dest='end_sec', type=int, default=360)
parser_wait_pod.add_argument('--leap', dest='leap_sec', type=int, default=20)
parser_wait_pod.set_defaults(func=wait_pod_to_active)

if __name__ == '__main__':
    args = parser.parse_args()
    kvargs = {k:v for k,v in args.__dict__.items() if k!="func"}
    args.func(**kvargs)
