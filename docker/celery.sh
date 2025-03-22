#!/bin/bash

cd src

if [[ "${1}" == "celery" ]]; then
  celery --app=celery:app worker -l INFO
elif [[ "${1}" == "flower" ]]; then
  celery --app=celery:app flower
 fi