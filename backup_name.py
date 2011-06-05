""" Copyright 2011 Rikard Anglerud
For licensing information, see the COPYING file. 

This is a module to create a new filename for a wordpress backup. This does
not do any backing up itself. 

The only method you need to use is get_backup_name(path)

What this method does is: 
Read today's date.
Look in the directory specified, see if any backups exist. 
Find out the max backup there, else start at 1
Create date-number.zip as the name
"""

import datetime, filepath, re


backup_name_re = re.compile('(\d{8})-(\d+)\.zip')

def today_str():
    """ Today's date in str format. """
    return datetime.datetime.now().strftime('%Y%m%d')

def is_backup(backup_file):
    """ See if this filename is a backup. """
    m = backup_name_re.search(backup_file.basename())
    if m: return True
    return False

def previous_backups(path):
    """ Find all the previous backups. """
    return (f for f in 
        filepath.FilePath(path).children()
        if f.isfile() and is_backup(f))

def todays_backups(files):
    """ Find all the backups done today. """
    ts = today_str()
    groups = ((f, backup_name_re.search(f.basename()).groups()) for f in files)
    return ((f, day, num) for f, (day, num) in groups if day == ts)

def backup_number(file_tuples):
    """ Find the backup number we should use, last backup today + 1. """
    return max([0] + [int(i) for i in (num for f, day, num in file_tuples)])

def backup_name(last_number):
    """ Create a string path of the date, backup number and .zip ext. """
    return today_str() + '-' + str(last_number + 1).zfill(2) + '.zip'


def get_backup_name(path):
    return backup_name(backup_number(todays_backups(previous_backups(path))))


if __name__ == '__main__':
    # Example use:
    print get_backup_name('.')
