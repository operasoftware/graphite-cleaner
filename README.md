# graphite-cleaner
Wipe out stale Whisper files.

[Graphite](https://github.com/graphite-project/graphite-web) or [Whisper](https://github.com/graphite-project/whisper) won't remove automatically data for old or renamed metrics. `graphite-cleaner` launched periodically as f.ex. cron job will do it.

# usage
```
usage: main.py [-h] [--days DAYS] [--path PATH] [--noinput] [-n]
               [-i IGNOREFILE] [-l LOGLEVEL]

optional arguments:
  -h, --help            show this help message and exit
  --days DAYS           files older than this value will be removed (default:
                        30)
  --path PATH           path to Graphite Whisper storage directory (default:
                        /opt/graphite/storage/whisper)
  --noinput
  -n, --dry-run
  -i IGNOREFILE, --ignorefile IGNOREFILE
                        file containing regex patterns specyfing paths to
                        ignore (default: None)
  -l LOGLEVEL, --loglevel LOGLEVEL
  ```
