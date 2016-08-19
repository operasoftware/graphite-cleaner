#!/usr/bin/env python

import errno
import logging
import re
import os
from time import time

from argh import arg
from argh.dispatching import dispatch_command


logging.basicConfig()
logger = logging.getLogger(__name__)


RED = "\033[1;31m{0}\033[00m"
GREEN = "\033[1;36m{0}\033[00m"
YELLOW = "\033[1;33m{0}\033[00m"

BYTES_TO_MEGABYTES = 1024.0 * 1024.0
DAY_IN_SECONDS = 24 * 60 * 60


def get_stale_files(path, days, ignore_patterns=None):
    if ignore_patterns is None:
        ignore_patterns = []

    def should_ignore(file_path):
        for ignore_pattern in ignore_patterns:
            if ignore_pattern.search(file_path):
                return True

    stale_files = []
    stale_files_size = 0
    total_size = 0
    for dir_path, _, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(dir_path, filename)
            file_size = os.path.getsize(file_path)

            mtime = os.path.getmtime(file_path)

            if should_ignore(file_path):
                result = 'IGNORE'
            elif mtime < time() - days * DAY_IN_SECONDS:
                stale_files.append(file_path)
                stale_files_size += file_size
                result = 'DELETABLE'
            else:
                result = 'OMIT'

            log_msg = 'Analyze %s (mtime %s)... %s' % (file_path, mtime, result)
            logger.debug(log_msg)
            total_size += file_size

    return stale_files, stale_files_size, total_size


def remove_empty_folders(path):
    for root, dirnames, _ in os.walk(path, topdown=False):
        for dirname in dirnames:
            try:
                os.rmdir(os.path.realpath(os.path.join(root, dirname)))
                print GREEN.format('[REMOVED]'), os.path.join(root, dirname)
            except OSError as exception:
                if exception.errno != errno.ENOTEMPTY:
                    raise


def parse_ignore_file(f):
    patterns = []
    for line in f:
        line = line.rstrip()
        if not line:
            continue
        pattern = re.compile(line)
        patterns.append(pattern)
    return patterns


@arg('--days', type=int, default=30,
     help='files older than this value will be removed')
@arg('--path', default='/opt/graphite/storage/whisper',
     help='path to Graphite Whisper storage directory')
@arg('--noinput', action='store_true')
@arg('-n', '--dry-run', action='store_true')
@arg('-i', '--ignorefile',
     help='file containing regex patterns specyfing paths to ignore',
     default='/etc/graphite-cleaner/ignore.lst')
@arg('-l', '--loglevel', default='ERROR')
def remove_stale_files(args):
    logger.setLevel(logging.getLevelName(args.loglevel))

    print 'Graphite Whisper stale database files remover\n'

    ignore_patterns = None

    if args.ignorefile:
        if os.path.exists(args.ignorefile):
            ignore_patterns = parse_ignore_file(open(args.ignorefile))
        else:
            print 'Ignore file %s does not exist.' % args.ignorefile

    files, size, total_size = get_stale_files(args.path, args.days, ignore_patterns)

    if not files:
        print 'No deletable files found.'
        return

    for file_path in files:
        print file_path

    print('Found {count} files. '
          'Size: {size:.2f}MB/{total_size:.2f}MB ({percent:.2%})').format(
              size=size / BYTES_TO_MEGABYTES,
              total_size=total_size / BYTES_TO_MEGABYTES,
              percent=float(size) / total_size if total_size != 0 else 0,
              count=len(files))

    if args.dry_run:
        return

    if not args.noinput:
        print YELLOW.format('The files listed above are going to be removed. '
                            'Continue? [y/N]')
        choice = raw_input().lower()

        if choice != 'y':
            print YELLOW.format('Operation aborted.')
            return

    for file_path in files:
        try:
            os.remove(file_path)
            print GREEN.format('[REMOVED]'), file_path
        except OSError as exception:
            print RED.format('[ERROR]'), file_path
            print exception
    remove_empty_folders(args.path)
    print 'Finished.'


def main():
    dispatch_command(remove_stale_files)


if __name__ == '__main__':
    main()
