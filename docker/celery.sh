#!/bin/bash

cd src

if [[ "${1}" == "celery" ]]; then
  celery -A celery_app.config_celery worker -l INFO
elif [[ "${1}" == "flower" ]]; then
  celery -A celery_app.config_celery flower
 fi