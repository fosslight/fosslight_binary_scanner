# How to set up FOSSLight Binary's Database

```note
To extract OSS information (OSS Name, OSS version, License) from Database, you need to set up Database.
```

## Prerequisite
1. Install [PostgreSQL][PostgreSQL]
2. How to edit configuration file for remote access : [reference link][ref_link]

[PostgreSQL]: https://github.com/fosslight/fosslight_binary/blob/main/LICENSE
[ref_link]: https://www.cyberciti.biz/tips/postgres-allow-remote-access-tcp-connection.html


## How to create database and table
1. Create user and database
````
$ sudo -i -u postgres 
$ psql
postgres=# CREATE USER bin_analysis_script_user PASSWORD 'script_123' ;
postgres=# CREATE DATABASE bat OWNER bin_analysis_script_user  ENCODING 'utf-8';
````
2. Create table
````
$ psql -U bin_analysis_script_user -d bat -f fosslight_create.sql
````

### Table schema
<img alt="table" src="table_schema.png">


## Example. Sql query to input data
````
INSERT INTO public.lgematching (filename, pathname, checksum, tlshchecksum, ossname, ossversion, license, parentname, platformname, platformversion, updatedate, sourcepath) VALUES
('askalono.exe', 'third_party/askalono/askalono.exe', '3f5c6bbf06ddf53a46634bb21691ab0757f3b80c', 'T138267C12BB86A9EDC06AC470878646225B31B4CA0B25BFFF41C455743E6AAF45F3D39C', 'askalono', '', 'Apache-2.0', '[123]windows app project', 'windows', '10', '2021-02-19 17:21:52.430065', 'third_party/src/askalono')  
````   
- The checksum and tlshchecksum values are output to binary.txt when fosslight_binary is executed.


## How to load data from your DB
- When calling fosslight_binary, write your DB information with the -d option.
ex)
````
fosslight_binary -p path_to_analyze -d postgresql://username:password@host:port/database_name
````




