import subprocess, os, sys, glob, shutil, time,datetime
from tempfile import TemporaryFile
import math
from ftplib import FTP_TLS
from os import listdir
from os.path import isfile, join
import logging
from logging.handlers import RotatingFileHandler
logLocation = os.path.join(os.getcwd() + '\hyperv-backup.log')
logging.basicConfig(format='%(asctime)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', handlers=[RotatingFileHandler(filename=logLocation, maxBytes=2048000,backupCount=5)])

applogger = logging.getLogger('hyperv-logger')
applogger.setLevel(logging.INFO) # NOTSET  = all logs
applogger.info('Starting of HyperV Backup: ' + os.environ['COMPUTERNAME'])

######  SETTINGS ###################################################
### General Settings ###
deleteLocal = True # overwritten by vms.txt configuration
zip7 = r'C:\Program Files\7-Zip\7z.exe' # requires 7zip installed
direc = os.getcwd()
file = r'\vms.ini' # file with names of vms to backup with new line separation
'''
    vms.ini should be formatted:
    vmname|local,network,ftp,3
    vmname seperated from options with pipe symbol
    options are:
    local = keep local copy
    network = create network share copy
    ftp = create ftp copy
    3 = days to keep backups - optional will default to main setting for daysOld
'''
saveLoc = '*backup parent folder*'
networkSaveLoc = '*Local folder network share link*' # wbadmin network share required as output (local folder configured as network)
backTo = saveLoc + 'backup folder'
daysOld = 3 # days to keep backups on ftp server

### ftp settings ###
useFTP = False # overwritten by vms.txt configuration
ftphost='*IP address or host name*'
ftpuser='*ftp username*'
ftppass='*ftp password*'

### Email Settings ###
useEmail = True # overwritten by vms.txt configuration
sendEmail = '*email address to send from*'
emailUser = '*email login*'
emailPass = '*email password*'
emailHost = '*smtp server*' # currently tested against gmail
emailPort = 465
receiptEmail = ['emaill address1, email address2'] # array of comma seperated values
emailSubject = os.environ['COMPUTERNAME'] + ': HyperV BackUp'
emailMsg = ''

### Network share settings ###
useNetworkShare = False # overwritten by vms.txt configuration
netShare= '*Network share folder to copy backup to*'
networkShareSettingsCorrect = netShare
####################################################################

# check that all config settings are correct
ftpSettingsCorrect = ftphost and ftpuser and ftppass
if not ftpSettingsCorrect:
    useFTP = False
if not sendEmail or not emailUser or not emailPass or not emailHost or not emailPort or not receiptEmail:
    useEmail = False
if not networkShareSettingsCorrect:
    useNetworkShare = False

processSuccess = True # changed to false if exception happens
daysKeptObj = {}
hypervList = list()

if not os.path.isdir(saveLoc): 
    os.mkdir(saveLoc)
if not os.path.isdir(backTo): 
    os.mkdir(backTo)

count_deleted_local = 0
count_deleted_network = 0
count_deleted_ftp = 0
vmProcessOptions = ''

with TemporaryFile() as output:
    with open(direc + file) as f:
        s = set()
        for line in f: # Check for duplicate in vm list and dont process
            vmName = line.split('|')[0]
            vmName = vmName.rstrip()
            if vmName not in s:
                s.add(line)
            else:
                applogger.debug('Duplicate VM ' + vmName + ' removed from VM list')
        for line in s:
            details = line.split('|')
            vmName = details[0].rstrip()
            if len(details) > 1:
                backUpOptions = details[1].rstrip().split(',')
                if 'local' in backUpOptions:
                    deleteLocal = False
                if 'network' in backUpOptions and networkShareSettingsCorrect:
                    useNetworkShare = True
                if 'ftp' in backUpOptions and ftpSettingsCorrect:
                    useFTP = True
                try:
                    daysKept = int(backUpOptions[-1])
                    daysKeptObj[vmName] = daysKept
                except Exception as e:
                    daysKeptObj[vmName] = daysOld
                    pass
            else:
                daysKeptObj[vmName] = daysOld
            hypervList.append(vmName)
            curTime = time.strftime('%Y%m%d-%H%M%S') + '.' + str(math.floor(time.time()))
            newFileName = os.path.join(networkSaveLoc,vmName + '.' + curTime + '.7z')
            args = 'wbadmin', 'start', 'backup', '-backupTarget:' + networkSaveLoc, '-hyperv:' + vmName, '-quiet'
            outputFolder =  os.path.join(networkSaveLoc,'WindowsImageBackup')
            args7zip = zip7, 'a' ,newFileName, outputFolder
            if 'str' in vmName:
                break
            try:
                willow = subprocess.list2cmdline(args)
                applogger.info('creating VM Backup - ' + vmName)
                result = subprocess.Popen(args,stdin=subprocess.PIPE, stdout=output, stderr=subprocess.PIPE)
                result.wait()
                applogger.info('created VM Backup - ' + vmName)
                result2 = subprocess.Popen(args7zip,stdin=subprocess.PIPE, stdout=output, stderr=subprocess.PIPE)
                result2.wait()
                applogger.info('zip VM completed - ' + vmName)
                #stdout, stderr = result.communicate()
                shutil.rmtree(outputFolder)
                applogger.info('ProcessComplete - ' + vmName)
                if useFTP:
                    try:
                        ftps = FTP_TLS(ftphost) # only works agains ftps ssl secured ftp server
                        ftps.login(ftpuser, ftppass)         
                        ftps.prot_p()          # switch to secure data connection.. IMPORTANT! Otherwise, only the user and password is encrypted and not all the file data.
                        file123 = open(newFileName,'rb')                  # file to send
                        applogger.info('Start FTP Transfer - ' + vmName)
                        ftps.storbinary('STOR ' + vmName + '.' + curTime + '.7z', file123)     # send the file
                        applogger.info('Complete FTP Transfer - ' + vmName)
                    except Exception as e:
                        applogger.info('Complete FTP Transfer (with captured exception) - ' + vmName)
                    finally:
                        file123.close() 
                        ftps.quit()
                if useNetworkShare and deleteLocal:
                    applogger.info('Start Network Transfer - ' + vmName)
                    shutil.move(newFileName, os.path.join(netShare,vmName + '.' + curTime + '.7z'))
                    applogger.info('Complete Network Transfer - ' + vmName)
                else:
                    applogger.info('Start Network Transfer - ' + vmName)
                    shutil.copy(newFileName, os.path.join(netShare,vmName + '.' + curTime + '.7z'))
                    applogger.info('Complete Network Transfer - ' + vmName)
                if not useNetworkShare and deleteLocal:
                    os.remove(newFileName)
            except Exception as e:
                    applogger.debug('Unexpected exception running command: %s', e)
                    processSuccess = False
            else:
                if result.returncode!=0:
                    applogger.debug('Error code=%d running command: %s', subprocess.list2cmdline(args))
                    processSuccess = False


quite_old= math.floor(time.time() - daysOld*86400) # three days

def deleteFiles(fileList, delType):
    global count_deleted_local,count_deleted_network,count_deleted_ftp
    currentTime = math.floor(time.time())
    for fi in fileList:
        file_parts = fi.split('.')
        if len(file_parts) == 4:
            vmName = file_parts[0]
             try:
                daysKept = int(daysKeptObj[vmName])
                quite_old = currentTime - daysKept*86400      
            except Exception as e:
                daysKept = daysOld
                quite_old = currentTime - daysKept*86400 
            if vmName in tuple(hypervList):
                timeDate =  file_parts[len(file_parts)-2]

                if int(quite_old) >= int(timeDate):
                    if delType == 'local':
                        count_deleted_local +=  1
                    elif delType == 'network':
                        count_deleted_network +=  1
                    elif delType == 'ftp':
                        count_deleted_ftp +=  1
                    
                    try:
                        applogger.info('Removing ' + delType + ' Backup ' + str(fi) + ' it\'s over ' + str(daysOld) + ' days old')
                        if delType == 'local':
                            os.remove(os.path.join(networkSaveLoc, fi)) 
                        if delType == 'network':
                            os.remove(os.path.join(netShare, fi))
                        else:
                            ftps.delete(fi)
                    except Exception as e:
                        applogger.debug('Exception on '+ delType +' delete ' + str(fi))
                        processSuccess = False
                        pass

if not deleteLocal: # delete after time limit
    try:
        onlyfiles = [f for f in listdir(backTo) if isfile(join(backTo, f))]
        deleteFiles(onlyfiles,'local')
    except Exception as e:
        applogger.debug('Error with local file delete: %s', e)    
        processSuccess = False

if useNetworkShare:  # delete after time limit
    try:
        onlyfiles = [f for f in listdir(netShare) if isfile(join(netShare, f))]
        deleteFiles(onlyfiles,'network')
    except Exception as e:
        applogger.debug('Error with network file delete: %s', e)    
        processSuccess = False

if useFTP:  # delete after time limit
    try:
        ftps = FTP_TLS(ftphost)
        ftps.login(ftpuser, ftppass)           
        ftps.prot_p() 
        files = ftps.nlst()
        deleteFiles(files,'ftp')
    except Exception as e:
        applogger.debug('Error with directory listing: %s', e)    
        processSuccess = False
    finally:
        ftps.quit()

def deletedErrorMessage(count,delType):
    applogger.info('Removed ' + str(count) + ' ' + delType + ' Backups')

if count_deleted_local > 0:
    deletedErrorMessage(count_deleted_local,'local')
if count_deleted_network > 0:
    deletedErrorMessage(count_deleted_network,'network')
if count_deleted_ftp > 0:
    deletedErrorMessage(count_deleted_ftp,'ftp')


if useEmail:
    import smtplib
    from os.path import basename
    from email.mime.application import MIMEApplication
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from email.utils import COMMASPACE, formatdate


    def send_mail(send_from, send_to, subject, text, files=None,
                server='127.0.0.1', port=25):

        msg = MIMEMultipart()
        msg['From'] = send_from
        msg['To'] = COMMASPACE.join(send_to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject

        msg.attach(MIMEText(text))

        for f in files or []:
            with open(f, 'rb') as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)


        smtp = smtplib.SMTP_SSL(server,port)
        smtp.ehlo() 
        smtp.login(emailUser, emailPass)
        smtp.sendmail(send_from, send_to, msg.as_string())
        smtp.close()

    if processSuccess:
        emailMsg += 'Backup was a success'
    else:
        emailMsg += 'Backup has errors, please see attached log'
    try:
        send_mail(sendEmail,receiptEmail,emailSubject,emailMsg, [logLocation], emailHost,emailPort)
    except ValueError:
        applogger.info('Email not sent correctly')
        
        
