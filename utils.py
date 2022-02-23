import os
import json
import time
import subprocess

BASE = os.path.dirname(__file__)


def get_base_dirc():
    return BASE


def run_shell(script: str, cap_result: bool = False) -> list:
    res = subprocess.run(script, shell=True, capture_output=cap_result)
    if cap_result:
        return res.stdout.decode("utf-8").split('\n')
    else:
        return []


def read_json_file(fname: str) -> dict:
    with open(fname) as f:
        dic = json.load(f)
    return dic


def dumps_json(dic, for_bash: bool = False) -> str:
    res = json.dumps(dic)
    if for_bash:
        return "'{}'".format(res.replace('"', '\\"'))
    return res


def scan_files(dirc: str, cond: callable, except_first: bool = False) -> dict:
    res = {}
    for root, _, files in os.walk(dirc):
        if except_first and root == dirc:
            continue
        for f in files:
            if cond(f):
                res[f] = os.path.join(root, f)
    return res


def constant_leap_waiter(start_sec: int, end_sec: int, leap_sec: int,
                         cond: callable, verbose: bool = False):
    time.sleep(start_sec)
    for t in range(start_sec, end_sec, leap_sec):
        time.sleep(leap_sec)
        if cond(t):
            return None
        elif verbose:
            print("{} sec: still waiting.".format(t))

    raise TimeoutError("Condtion not fulfilled after {} sec.".format(end_sec))


if __name__ == "__main__":
    res = run_shell("ls -al {}".format(BASE), True)
    for line in res:
        print(line)

    def cond_always_true(x): return True
    print(scan_files(BASE, cond_always_true))

    def cond(x): return x > 9
    constant_leap_waiter(4, 12, 2, cond, True)
    constant_leap_waiter(2, 5, 2, cond, True)
