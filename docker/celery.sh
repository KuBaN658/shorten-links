#!/bin/bash

cd src

celery -A celery_app.config_celery:app worker -l INFO
