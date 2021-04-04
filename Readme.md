# Directory structure
- `FRONT_END`: dir containing all the front end files
- `DATA_DUMP`: dir
- `setup_front_end.sh`: bash script file which will install all dependencies related to your front-end.  
**Note:** Installation file should not consist of any commands containing sudo.
- `run.sh`: bash script to run your flask server.  
Port number for flask is 5022 (5000 + 22 (our group number))

# Running instructions
When you first run the app, you need to create and fill the database
```
createdb group_22
psql -d group_22 -f db_build.sql
```

If you want to delete all the tables and then the whole database do
```
psql -d group_22 -f db_drop.sql
dropdb group_22
```

To create DATA_DUMP, do the following
```
pg_dump group_22 > DATA_DUMP/data_dump.sql
```
Also replace all occurences of user (e.g. 'vishal') with 'group_22' in the data_dump.sql file.

# Design Plan
![healTrip-project-design-plan](https://user-images.githubusercontent.com/31121102/112135495-db731c00-8bf3-11eb-8907-db669f22ccdc.jpg)
