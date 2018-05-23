#!/usr/bin/python2.7
# -*- coding: utf-8 -*

from __future__ import print_function
import httplib2
import os, io, csv, sys

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

def assemble_file(path):
    try:
        queues_file = open(tmp_queue_file, 'w')
        queues_file.write(general_section)
        for day, queues in rules.iteritems():
            for queue in queues:
                queues_file.write(queue_section.format(queue.encode('utf-8'), day.encode('utf-8')))
                for member in queues[queue]:
                    queues_file.write(member_section.format(member.encode('utf-8')))
        print('queues.conf file created')
    except Exception as e:
        sys.exit('Failed to create queues.conf: %s' % e)

def fix_permissions(uid,gid,chmod,tmp_file):
    try:
        os.chown(tmp_file, uid, gid)
        print('queues.conf owner and group changed to %s:%s' % (uid, gid))
    except Exception as e:
        sys.exit('Failed to change owner and group for queues.conf: %s' % e)

    try:
        os.chmod(tmp_file, chmod)
        print('queues.conf permissions chanded to %02o' % (chmod,))
    except Exception as e:
        sys.exit('Failed to change permissions for queues.conf: %s' % e)

# Obtaining csv file from Google Spreadsheet
export_file(file_id, csv_file)
raw_csv = open(csv_file, 'rb')

# Parse file and create daytype\queue\member mapping
rules = parse_csv(raw_csv, daytypes)

# Assemble queues.conf file
assemble_file(tmp_queue_file)

# Change file owner and rights
fix_permissions(uid,gid,chmod,tmp_queue_file)

try:
    os.rename(tmp_queue_file, queue_path)
    print('Moved queues.conf to asterisk working dir')
except Exception as e:
    sys.exit('Failed to move queues.conf to asterisk working dir: %s' % e)

# Reloading queues from AMI
reload_status = reload_queues()
if reload_status is True:
    print('Queues configuration reload successfully')
else:
    sys.exit('Failed to reload queues: %s' % reload_status)
