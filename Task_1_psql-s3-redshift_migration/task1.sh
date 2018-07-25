#!/usr/bin/env bash

python task1_sql.py "${1:-postgres}" "${2:-postgres}" "${3:-password}";
echo "table apps has been created";
