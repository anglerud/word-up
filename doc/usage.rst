Backup
======
To perform a backup all you have to do is tell 'backup.py' where your
wordpress is installed. Use it like this::

    python backup.py /var/www/yourwordpress.com /home/you/backups

To clean up backups that are no longer needed::

    python backup_cleanup.py /home/you/backups

You can tell backup_cleanup.py how many backups to keep with the --keep
flag. The default is to keep the three latest ones. 



Restore
=======

To restore a wordpress site from a backup - start by unzipping the
backup file. Inside there are two directories, 'db', which contains
the database backup, and 'wp' which contains the wordpress files
you need. 

To restore the database backup::

    you@machine:~/backup/db> mysql -h host -u user -p dbname < backup.sql

Then restore the files by copying the config file from the wp directory
into your wordpress install, then copy the rest of the files into your
wp-content directory. 


Scheduling
==========

I suggest using cron to schedule at least weekly backups with a pair of
entries like this::

    0 3 * * * /to/virtualenv/bin/python /to/word_up/backup.py \
              /www/www/wordpress.com /home/you/backups
    0 4 * * * /to/virtualenv/bin/python /to/word_up/backup_cleanup.py \
              /home/you/backups
