rdb-fullstack
=============

Common code for the Relational Databases and Full Stack Fundamentals courses


##Installation

Either clone the repository using git clone command, or use the download ZIP link on the right hand side of the screen.In order to run the code:
- cd to the project folder
- Launch vagrant using ***vagrant up*** and ***vagrant ssh***
- This launches vagrant and cd to the tournament folder
- Run ***psql*** to launch CLI for Postgresql database server
- Run ***\i tournament.sql*** to create the database
- Quit the psql CLI using ***\q***
- Run ***python tournament_test.py***
