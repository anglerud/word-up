"""  Copyright 2011 Rikard Anglerud
For licensing information, see the COPYING file. 

This is a quick way to back up the data in wordpress installs.
It's intended to be launched via cron or similar for best effect, and followed
by backup_cleanup.py to limit the space taken. 

Use like this: 
python backup.py /path/to/wordpress /path/to/store/backups/in
"""
import os.path, re, subprocess

from fs import mountfs, osfs, zipfs

import backup_name


def get_args():
    """ Get the cmdline args passed in. """
    import argparse
    description = 'Remove all but the last N wordpress backups.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('backup_path', action='store', help='Path to backups.')
    parser.add_argument('storage_path', action='store', help='Path to store.')

    return parser.parse_args()


def get_storage_cfg(args):
    """ Create a dict with the config we need. """
    base_dir, project = os.path.split(args.backup_path)
    backup_file_name = backup_name.get_backup_name(args.storage_path)
    backup_file = '{0}/{1}'.format(args.storage_path, backup_file_name)
    db_backup_dir = '{0}/db'.format(project)
    db_backup_file = '{0}/mysql_database_backup.bak'.format(db_backup_dir)
    wp_backup_dir = '{0}/wp'.format(project)
    return dict(base_dir=base_dir, project=project, 
                backup_file_name=backup_file_name, backup_file=backup_file,
                db_backup_dir=db_backup_dir, db_backup_file=db_backup_file,
                wp_backup_dir=wp_backup_dir)


def get_combined_fs(s_cfg):
    """ Return a 'fs' filesystem which is a combination mount of a fsfs
        filesystem to read the files from, and a zip filesystem to store them
        in. """
    # Create the backup zipfile
    zip_fs = zipfs.ZipFS(s_cfg['backup_file'], mode='w')
    src_fs = osfs.OSFS('{0}/{1}'.format(s_cfg['base_dir'], s_cfg['project']))
    # Mount the zip and the src directory in the same combined namespace.
    combined_fs = mountfs.MountFS()
    combined_fs.mountdir('src', src_fs)
    combined_fs.mountdir('dst', zip_fs)
    # Prepare the filestructure inside the zipfile
    combined_fs.makedir('src/' + s_cfg['db_backup_dir'], recursive=True, 
                        allow_recreate=True)
    combined_fs.makedir('src/' + s_cfg['wp_backup_dir'], recursive=True, 
                        allow_recreate=True)

    return zip_fs, combined_fs


def get_wordpress_config(combined_fs):
    """ Read the values out of the wordpress config. We're most interested in
        DB_NAME, DB_USER, DB_PASSWORD """
    re_define = re.compile('define\(\'(.*?)\',\s*\'(.*?)\'\);')
    config = dict()
    config_file = combined_fs.open('/src/' + 'wp-config.php')
    for line in config_file:
        config_vals = re_define.search(line)
        if config_vals: config.update(dict([config_vals.groups()]))
    return config


def db_backup(w_cfg, combined_fs, s_cfg):
    """ Dump the wordpress database into the zip file. """
    # Launch the mysqldump command, which spews the backup to stdout. 
    cmd = ['mysqldump', '--add-drop-table', '-h', 'localhost', '-u', 
           w_cfg['DB_USER'], '--password={0}'.format(w_cfg['DB_PASSWORD']), 
           w_cfg['DB_NAME']]
    backup = subprocess.Popen(cmd, stdout=subprocess.PIPE)

    # Write that data into the zipfile's db backup. 
    db_backup = combined_fs.open('/dst/' + s_cfg['db_backup_file'], mode='w')
    for l in backup.stdout:
        db_backup.write(l)
    db_backup.close()


def wp_backup(combined_fs, s_cfg):
    """ Copy in the wp-content and wp-config.php files into the zip file. """
    # Copy the user-specific parts of the wordpress install into the backup.
    combined_fs.copy('src/wp-config.php', 
                     'dst/{0}/wp-config.php'.format(s_cfg['wp_backup_dir']))
    combined_fs.copydir('src/wp-content', 
                        'dst/{0}/wp-content'.format(s_cfg['wp_backup_dir']))


def backup():
    """ Figure out what to back up to where, and do it. """
    # Setup
    args = get_args()
    s_cfg = get_storage_cfg(args)
    zip_fs, combined_fs = get_combined_fs(s_cfg)
    w_cfg = get_wordpress_config(combined_fs)

    # Backup
    db_backup(w_cfg, combined_fs, s_cfg)
    wp_backup(combined_fs, s_cfg)

    # There is a bug in fs that causes corrupt zips unless it's closed
    # here
    zip_fs.close()


if __name__ == '__main__':
    # We're invoked at the commandline, perform a backup.
    backup()

