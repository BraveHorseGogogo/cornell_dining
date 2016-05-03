Cornell Dining App Server
=======
### Server Installation Instruction

1. Upload the 'dining' dir to the server. Currently, the server is running in /users/yt438/CornellDining2/HelloSE/dining dir
2. kill the httpd serveice running on 80 port
3. sudo -s, switch to root user
4. use '. venv/bin/activate' to activate vertual environment  
    * the environment should install cx_Oracle and flask
    * make sure the environment variable 'LD_LIBRARAY_PATH' and 'ORACLE_HOME' are right
5. set the email address in dining.py, which will receive user's comments
6. type 'python dining.py' and wait for seconds, the server's running!

### Important Files

1. 'dining.py' the main program
2. 'hours.py' the script parsing ics files
3. 'dining.sqlite' the local database
4. 'dining-all-cafe-backup.sqlite' the back up of local database storing the original url of each dining hall
5. 'static' dir the places stores images and ics files
6. 'grab_images.py" the script download images to 'static' dir and then update the data