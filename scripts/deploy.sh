#!/bin/bash

set -e
ROOT_DIR=$(pwd)
if [ ! -d .env ]; then
    virtualenv .env
fi

if [ ! -f conf/app.conf ]; then
  echo "you need a conf/app.conf to configure application"
  exit 1
fi
if [ ! -f conf/supervisord.conf ]; then
  echo "have not found supervisord.conf,copy from sample"
  cp conf/supervisord.conf.sample conf/supervisord.conf
fi

source .env/bin/activate
which pip
pip -V
which python
pip install -r scripts/requirements.txt # -i  http://mirrors.sankuai.com/pypi/simple/
SUPERVISORD_PID_FILE=$ROOT_DIR/run/supervisord.pid
# supervisord 负责拉起tornado
# 如果supervisord没有起来，那么运行
# 如果运行起来了,那么检查tornado状态，并重启
if [ -f "$SUPERVISORD_PID_FILE" ]; then
    supervisorctl -c $ROOT_DIR/conf/supervisord.conf restart dataweb
    if [ -f "$ROOT_DIR/run/celery-beat.pid" ]; then #beat reload
        kill -1 `cat $ROOT_DIR/run/celery-beat.pid`
    fi
    if [ -f "$ROOT_DIR/run/celery-worker.pid" ]; then #worker reload
        kill -1 `cat $ROOT_DIR/run/celery-worker.pid`
    fi
    if [[ `supervisorctl -c $ROOT_DIR/conf/supervisord.conf avail|grep "admin"` ]]; then
      supervisorctl -c $ROOT_DIR/conf/supervisord.conf restart admin
    fi
    
else
    supervisord -c $ROOT_DIR/conf/supervisord.conf -l logs/supervisord.log
fi
# service moscrm restart
supervisorctl -c $ROOT_DIR/conf/supervisord.conf avail |awk '{print $1}'|xargs supervisorctl -c $ROOT_DIR/conf/supervisord.conf status
