#!/bin/bash

psql -h localhost -U postgres -d postgres -c "CREATE USER admin WITH PASSWORD 'postgres';
                                              CREATE DATABASE db_app OWNER admin;
                                              GRANT ALL PRIVILEGES ON DATABASE db_abb TO admin;"