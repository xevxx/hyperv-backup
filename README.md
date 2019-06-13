# Hyperv Backup
Python3 Hyperv backup script using wbadmin - It allows the user to configure local storage, network storage and ftp storage for backups and a maximum age (in days) before autodeleting

The script can be run using 
```
python hyperv-backup.py
```

Tested againt python 3.7.3 on Windows server 2012 R2

### dependencies
- 7zip https://www.7-zip.org/download.html
- python 3 https://www.python.org/downloads/
- wbadmin - part of windows

#### installing wbadmin on server
This script uses wbadmin to create backup copies of hyperv vms as described in https://blogs.msdn.microsoft.com/virtual_pc_guy/2013/02/25/backing-up-hyper-v-virtual-machines-from-the-command-line/

1. Log in to Server01 and open Server Manager.
2. Click Manage → Roles and Features.
3. Click Next when the Add Roles and Features Wizard appears.
4. Click Next on the Select installation type screen.
5. Click Next on the Select destination server screen.
6. Click Next on the Select server roles screen.
7. Select Windows Server Backup and click Next.
8. Select Restart the destination server automatically if required and click Yes to allow automatic restarts.
9. Click Install and then click Close


# Configuration
All configurable settings are located in the Settings section of the script. All are marked with '*change values*'

The configurable values include:

- Local backup folder and local share folder (WBadmin will only accept network sahre for backing up to, this is gotten round by accessing a local folder using a network share path.
- network backup folder
- ftp settings (tested against Filezilla server with tls enabled)
- email settings (tested against gmail)


The backups can be configured using the vms.ini

vms.ini should be formatted:
```
vmname1|local,network,ftp,3
vmname2|network,20
```
VM Name separated from options with pipe | symbol
options are:
  - local = keep local copy
  - network = create network share copy
  - ftp = create ftp copy
  - 3 = days to keep backups - optional will default to main setting for daysOld
  
# What it does
WBadmin creates a backup folder at the desired local folder (using share path - '\\machinename\sharetolocalfolder')
This folder is archived to 7z using 7zip command line
Backup folder is deleted
Depending on configuration:
  - move or copy 7z to network storage
  - transfer 7z to ftp server using tls
  - delete local 7z

Check each of the three storage locations and delete backups older than the configured days old
Send email of log to desired email address stating success or failures

This is successfully run nightly on multiple servers of my own using task scheduler
```
C:\Windows\System32\cmd.exe
/c python *path to script*\hyper-vbackup.py
```
###### This program is free software. It comes without any warranty, to the extent permitted by applicable law. You can redistribute it and/or modify it under the terms of MIT licence
