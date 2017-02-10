rdb-fullstack
=============

##Installation

Either clone the repository using git clone command, or use the download ZIP link on the right hand side of the screen.In order to run the code:
- cd to the folder and cd to catalog directory
- Launch vagrant using ***vagrant up*** and ***vagrant ssh***
- This launches vagrant and cd to the catalog folder
- Run ***python catalogDB.py*** to create database for the project
- Run ***python catalogDBData.py*** to fill the data in the database
- Run Run ***python project.py*** to run the server
- Open the link ***http://localhost:5080/*** in the web browser


##Few points to remember:
- An User can edit or delete their own items
- An User cannot edit or delete items created by other users.
