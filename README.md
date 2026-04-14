# Cloud Backup & Recovery Automation

## Overview
Automated backup and restore system with scheduling.

## Architecture
```
Cron Job → Backup Script → Storage → Restore Script
```

## Run Backup
```bash
python backup.py
```

Back up from a custom source and destination:
```bash
python backup.py --source /path/to/source --dest /path/to/backups
```

Environment variables `BACKUP_SOURCE` and `BACKUP_DEST` can also be used to
configure the default source and destination directories.

## Restore
```bash
python restore.py backup_folder
```

Restore to a specific target directory:
```bash
python restore.py backup_folder --target /path/to/restore
```

## CI/CD
```yaml
name: Backup CI
on: [push]
jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Backup Script
        run: python backup.py
```

## Cloud Deployment
- Store backups in AWS S3
- Automate via cron on EC2

## Real-World Scenarios
- Data loss simulation
- Recovery testing