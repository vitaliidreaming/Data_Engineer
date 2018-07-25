#!/usr/bin/env bash

psql -U postgres -d postgres -c "COPY apps TO STDOUT WITH CSV DELIMITER','" | gzip > dat.csv.gz
