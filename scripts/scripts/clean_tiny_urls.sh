#!/bin/bash
export PGPASSWORD=whitehouse

psql -U rocketsr_dba rocketsr_sfdiva   < clean_sfdiva_db.sql 
#sqlite3 ~/sqlite3dbs/dj_sfblur.db < ~/private/clean_sfblur_db.sql 2>&1 >~/logs/sfblur.clean.log

