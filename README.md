**SQL code formating**
*Desc:*

command-line args to format/verify *.sql files

Usage: `python3 sql_processor.py -b --config=config_templates/second_template.json -p input`

-(p|d|f) - required argument. Specifies the execution policy:

p - dirs recursively 

d - dirs (no recursion) 

f - file 

--config|-c)=path - optional, specifies formatting template

--beautify, -b - formats the input files

--verify, -v - verifies the input files

last release: added support of insert into 