#!/usr/bin/python3

import sys
from datetime import datetime
import tarfile
import os.path
import os
import requests


def log(message, status='INFO'):
    print('[', datetime.now(), '] (' + status + ')', message)


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, 'w:gz') as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))


def get_project_name():
    return os.getcwd().split('/').pop()


def send_directory():
    log('Compressing directory...')
    if not os.path.exists('/var/tmp/syncomatic'):
        log('Syncomatic dir doesn\'t exist. Creating...')
        os.makedirs('/var/tmp/syncomatic/')
    make_tarfile('/var/tmp/syncomatic/archive.tar.gz', os.getcwd())
    log('Compressed!')
    log('Uploading directory...')
    with open('/var/tmp/syncomatic/archive.tar.gz', 'rb') as file:
        project_name = get_project_name()
        params = {
            'project_name': project_name
        }
        r = requests.post('http://localhost:3000/upload', params=params,
                          files={'archive.tar.gz': file})
        if r.status_code == 200:
            log('Uploaded successfully!', 'SUCCESS')
        else:
            log('Upload failed: ' + str(r.status_code), 'FAIL')

    log('Finished!')


def project_exists_remote(project):
    params = {
        'project_name': project
    }
    r = requests.get('http://localhost:3000/exists', params=params)
    return r.status_code == 200


def download_project_remote(project_name):
    params = {
        'project_name': project_name
    }
    r = requests.get('http://localhost:3000/download', params=params)
    open(project_name + '.tar.gz', 'wb').write(r.content)
    if (r.status_code == 200):
        log('Downloaded!', 'SUCCESS')
    else:
        log('Download Failed :(', 'FAIL')


def pull_directory():
    log('Pulling directory...')
    project_name = ''
    if len(sys.argv) == 2:
        log('No project specified, falling back to current directory')
        project_name = get_project_name()
    else:
        project_name = sys.argv[2]
        log('Project name has been specified. Searching for ' + project_name)

    if project_exists_remote(project_name):
        log('Found project ' + project_name + ' remotely. Downloading...')
        download_project_remote(project_name)
    else:
        log('Could not find project ' + project_name + ' remotely.', 'FAIL')


def show_help():
    print('Something helpful')


if (len(sys.argv) == 1):
    show_help()
elif (sys.argv[1] == 'send'):
    send_directory()
elif (sys.argv[1] == 'pull'):
    pull_directory()
else:
    log('Doing nothing')
