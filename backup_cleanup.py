""" Copyright 2011 Rikard Anglerud
For licensing information, see the COPYING file.  """

import collections, datetime, filepath, itertools, re, subprocess


backup_name_re = re.compile('(\d{8})-(\d+)\.zip')

def is_backup(backup_file):
    """ See if this file is likely to be a backup file. """
    m = backup_name_re.search(backup_file.basename())
    if m: return True
    return False

def previous_backups(storage_path):
    """ Find the previous backups. """
    return (f for f in 
        filepath.FilePath(storage_path).children()
        if f.isfile() and is_backup(f))

def backup_buckets(files):
    """ Group the backup files into buckets by day. """
    buckets = collections.defaultdict(list)

    groups = ((f, backup_name_re.search(f.basename()).groups()) for f in files)
    for f, (day, num) in groups:
        buckets[day].append(f)
    return buckets

def find_buckets(buckets, keep_buckets):
    """ Select the buckets to delete. """
    return sorted(buckets.iteritems())[:-keep_buckets]

def to_delete_files(buckets):
    """ Get the files to delete out of the buckets. """
    # each bucket is (date, filelist)
    for backup_date, bucket in buckets:
        for f in bucket: yield f

def delete_files(files):
    """ Delete the files. """
    for f in files: 
        f.remove()


def get_args():
    """ Get the cmdline args passed in. """
    import argparse
    description = 'Remove all but the last N wordpress backups.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('path', action='store', help='Path to backups.')
    parser.add_argument('--keep', action="store", dest="keep", type=int,
                        help='How many backps to kee keep', default=3)

    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    backup_files   = previous_backups(args.path)
    backup_buckets = backup_buckets(backup_files)
    buckets        = find_buckets(backup_buckets, args.keep)
    files          = to_delete_files(buckets)
    delete_files(files)

