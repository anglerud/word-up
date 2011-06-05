About
=====
A very simple set of cron-based backup scripts. 'backup.py' creates a backup,
and 'backup_cleanup.py' removes old backups.  Being very simple, it has no
concept of anything but the N last backups. What makes it especially simple
to use is that it picks up how to back up your database from your wordpress
config itself - there is nothing to configure, apart from pointing the 
backup tool to the right directory. 

The backup tool creates a zip file containing your wordpress files,
the wordpress config (but not the wordpress install), and a database dump. 
This is everything you need to restore a previous backup, or migrate the site
somewhere else. 


Requirements 
============
argparse, fs, filepath. These are all are pip installable. I suggest
setting up a virtual env.


Usage
=====
Command line flags and help:
python backup.py --help
python backup_cleanup.py --help


To back up a wordpress install:
python backup.py /var/www/yourwordpress.com /home/you/backups
python backup_cleanup.py /home/you/backups/
I suggest scheculing these via cron. 


To restore from a backup zip file:
1) Unzip the backup file. 
2) Restore the DB
user@linux:~/backup/db> mysql -h mysqlhostserver -u mysqlusername
 -p databasename < blog.bak.sql
3) Restore files: 
Copy the files into your wordpress install. 
Copy the config file into the wordpress install.


Contact information
===================
Created by Rikard Anglerud <anglerud@gmail.com>.


License
=======
GPLv3 or later. 

