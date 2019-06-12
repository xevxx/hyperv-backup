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

python 
