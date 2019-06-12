# hypervbackup
Python3 Hyperv backup script using wbadmin

Tested againt python 3.7.3 on Windows server 2012 R2

#installing wbadmin on server
Log in to Server01 and open Server Manager.
Click Manage → Roles and Features.
Click Next when the Add Roles and Features Wizard appears.
Click Next on the Select installation type screen.
Click Next on the Select destination server screen.
Click Next on the Select server roles screen.
Select Windows Server Backup and click Next.
Select Restart the destination server automatically if required and click Yes to allow automatic restarts.
Click Install and then click Close

This script uses wbadmin to create backup copies of hyperv vms. 
https://blogs.msdn.microsoft.com/virtual_pc_guy/2013/02/25/backing-up-hyper-v-virtual-machines-from-the-command-line/

it allows the user to configure local storage, network storage and ftp storage for backups and a maximum age (in days) before autodeleting

the script can be run using 

python hyperv-backup.py

all configurable settings are located in the Setting section of the script. All are marked with '*change values*'

The configurable values include:

Local backup folder and local share folder (WBadmin will only accept network sahre for backing up to, this is gotten round by acessing a local folder using a network share path.
network backup folder
ftp settings (tested against Filezilla server with tls enabled)
email settings (tested against gmail)

The backups can be configured using the vms.ini

vms.ini should be formatted:
vmname|local,network,ftp,3
vmname seperated from options with pipe symbol
options are:
  - local = keep local copy
  - network = create network share copy
  - ftp = create ftp copy
  - 3 = days to keep backups - optional will default to main setting for daysOld
  
WBadmin creates a backup folder at the desired local folder (using share path - '\\machinename\sharetolocalfolder'
this folder is archived to 7z using 7zip command line
backup folder is deleted
depending on configuration:
  - move or copy 7z to network storage
  - transfer 7z to ftp server using tls
  - delete local 7z

check each of the three storage locations and delete and older backups older than the configured days old
Send email of log to desired email address stating success or failures

This is successfully run nightly on multiple servers of my own

 /* This program is free software. It comes without any warranty, to
 * the extent permitted by applicable law. You can redistribute it
 * and/or modify it under the terms of MIT licence */
