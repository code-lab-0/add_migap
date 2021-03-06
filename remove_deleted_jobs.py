# -*- coding: utf-8

import sqlite3
from subprocess import Popen, PIPE
import json
import re
import daemon
import daemon.pidfile
import time

dbfile = '/tmp/remove_deteted_jobs/job_ids_record.sqlite3'
table = 'proc__job_ids__user__password'
rest_host = '172.19.24.112'
rest_port = '8182'
conn = None

def remove_deleted_job():
    try:
        conn = sqlite3.connect(dbfile, isolation_level='IMMEDIATE')
        c = conn.cursor()
        deleted_proc = []

        sql = 'select * from ' + table
        for row in c.execute(sql):
            proc = row[0]
            job_ids = row[1].split(' ')
            user = row[2]
            password = row[3]

            cmd = "ps h " + proc
            out, err = exec_cmd(cmd)
            if out.decode('utf-8') == '':
                print(proc + ' is removed.')
                job_ids.reverse()
                for job_id in job_ids:
                    print("job id:" + job_id)
                    exec_host = get_exec_host(job_id, user, password)
                    delete_uge_job(job_id, user, password)
                    if exec_host != 'no exec host':
                        print('exec host:' + exec_host)
                        # dockerコンテナの終了処理
                        container_id = get_container_id(job_id, user, password)
                        delete_container(container_id, exec_host, user, password)

                deleted_proc.append(proc)
            else:
                print('out:' + out.decode('utf-8'))

        for proc in deleted_proc:
            sql = "delete from " + table + " where proc = '" + proc + "'"
            c.execute(sql)

    except Exception as e:
        print(e)
        if conn: conn.rollback()

    finally:
        if conn: conn.commit()

    conn.close()

def exec_cmd(cmd):
    p = Popen(cmd, shell=True, executable='/bin/bash', stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return(out, err)

# UGE RESTからジョブの実行ノードを取得
def get_exec_host(job_id, user, password):
    host_r = re.compile("t\d\d\d")
    cmd = [
        "curl -X GET -H 'Content-Type: application/json' http://",
        rest_host,
        ":",
        rest_port,
        "/jobs/",
        job_id,
        " -u ",
        user,
        ":",
        password
    ]
    out, err = exec_cmd(''.join(cmd))
    json_data = json.loads(out.decode('utf-8'))
    print(json.dumps(json_data))
    if 'queue' in json_data:
        m = host_r.search(json_data["queue"])
        exec_host = m.group(0)
        return(exec_host)
    else:
         return("no exec host")

# UGE RESTにジョブ削除のコマンドを投入
def delete_uge_job(job_id, user, password):
    cmd = [
        "curl -X DELETE -H 'Content-Type: application/json' http://",
        rest_host,
        ":",
        rest_port,
        "/jobs -d {'jobid':'",
        job_id,
        "'} -u ",
        user,
        ":",
        password
    ]
    out, err = exec_cmd(''.join(cmd))
    print('out:' + out.decode('utf-8'))

# UGEジョブの標準出力からdockerコンテナIDの取得
def get_container_id(job_id, user, password):
    container_r = re.compile("^/docker/(.*?)\n")

    cmd = [
        "sh -c \"sshpass -p '",
        password,
        "' ssh -o StrictHostKeyChecking=no ",
        user,
        "@",
        rest_host,
        " 'cat /home/",
        user,
        "/*.o",
        job_id,
        "'\""
    ]
    print('cmd:' + ''.join(cmd))
    out, err = exec_cmd(''.join(cmd))
    m = container_r.search(out.decode('utf-8'))
    container_id = m.group(1)
    print("container id:" + container_id)
    return(container_id)

# 実行ノードとdockerコンテナIDからdockerコンテナを終了
def delete_container(container_id, exec_host, user, password):
    cmd = [
        "sh -c \"sshpass -p '",
        password,
        "' ssh -o StrictHostKeyChecking=no ",
        user,
        "@",
        rest_host,
        " 'docker stop ",
        container_id,
        "'\""
    ]
    print('cmd:' + ''.join(cmd))
    out, err = exec_cmd(''.join(cmd))
    print(out.decode('utf-8'))

def daemon_task():
    while True:
        remove_deleted_job()
        time.sleep(60)
        continue

if __name__ == "__main__":
    context = daemon.DaemonContext(
        working_directory = '/tmp/remove_deleted_jobs/',
        umask = 0o002,
        pidfile = daemon.pidfile.PIDLockFile('/tmp/remove_deleted_jobs/remove_deleted_jobs.pid'),
        stdout = open("/tmp/remove_deleted_jobs/stdout.log", "w+"),
        stderr = open("/tmp/remove_deleted_jobs/stderr.log", "w+")
    )
    with context:
        daemon_task()

