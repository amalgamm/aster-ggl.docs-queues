#!/usr/bin/python2.7
# -*- coding: utf-8 -*

from __future__ import print_function
import httplib2
import io, csv, sys,shutil

from apiclient import discovery
from apiclient import http as ghttp
from template import general_section,queue_section,member_section

from config import *
from ami import reload_queues
import auth

authInst = auth.auth(SCOPES, CLIENT_SECRET_FILE, APPLICATION_NAME)
credentials = authInst.getCredentials()

http = credentials.authorize(httplib2.Http())
drive_service = discovery.build('drive', 'v3', http=http)


def export_file(file_id, filepath):
    request = drive_service.files().export_media(fileId=file_id,
                                                 mimeType='text/csv')
    fh = io.BytesIO()
    downloader = ghttp.MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with io.open(filepath, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())

def is_exten(text):
    if text.isdigit():
        if int(text) in range(exten_from, exten_to):
            return True
        else:
            return False

def parse_csv(csv_file,daytypes):
    tab = csv.DictReader(csv_file, delimiter=',')
    mapping = {}
    for daytype in daytypes:
        mapping[daytype] = {}
    for row in tab:
        daytype = row['exten']
        trunkname = row['Имя']
        if daytype not in mapping:
            continue
        if trunkname not in mapping[daytype]:
            mapping[daytype][trunkname] = []
        for item, val in row.iteritems():
            if is_exten(item) and val == '+':
                if item not in mapping[daytype][trunkname]:
                    mapping[daytype][trunkname].append(item)
    return mapping

def assemble_file(path,rules):
    try:
        queues_file = open(path, 'w')
        queues_file.write(general_section)
        for day, queues in rules.iteritems():
            for queue in queues:
                queues_file.write(queue_section.format(queue.encode('utf-8'), day.encode('utf-8')))
                for member in queues[queue]:
                    queues_file.write(member_section.format(member.encode('utf-8')))
        queues_file.flush()
        print('queues.conf file altered')
        return True
    except Exception as e:
        print('Failed to alter queues.conf: %s' % e)
        return False

def backup_file(bck_path,path):
    try:
        shutil.copyfile(path,bck_path)
        print('queues.conf backuped successfuly')
    except Exception as e:
        sys.exit('Failed to backup queues.conf: %s' % e)

def rollover(bck_path,path):
    try:
        bck_file = open(bck_path,'r')
        orig_file = open(path,'w')
        orig_file.write(bck_file.read())
        print('Original queues.conf restored')
        bck_file.flush()
        orig_file.flush()
    except Exception as e:
        sys.exit('Failed to rollover queues.conf: %s' % e)

# Obtaining csv file from Google Spreadsheet
export_file(file_id, csv_file)
raw_csv = open(csv_file, 'rb')

# Parse file and create daytype\queue\member mapping
rules = parse_csv(raw_csv, daytypes)

# Make a backup version of queues.conf
backup_file(backup_queue_file,queue_path)

# Assemble queues.conf file
if assemble_file(queue_path) is True:
    # Reload queues if OK
    reload_status = reload_queues()
    if reload_status is True:
        print('Queues configuration reload successfully')
    else:
        sys.exit('Failed to reload queues: %s' % reload_status)
else:
    rollover(backup_queue_file,queue_path)



