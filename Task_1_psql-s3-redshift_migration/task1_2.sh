#!/usr/bin/env bash

echo "script generating and inserting data into table apps";
python task1_2.py "${1:-postgres}" "${2:-postgres}" "${3:-password}" "${4:-4999000}";
echo "done";
