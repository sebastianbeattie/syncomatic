#!/usr/bin/python3

import sys
from datetime import datetime
import tarfile
import os.path
import os
import requests
import yaml


def init_config():
    config_path = os.path.expanduser('~') + '/.config/syncomatic/'
    if not os.path.exists(config_path):
        log('Syncomatic config dir doesn\'t exist. Creating...')
        os.makedirs(config_path)
    config_file_path = config_path + 'config.yml'
    if not os.path.isfile(config_file_path):
        log('Syncomatic config file doesn\'t exist. Creating default...')
        config = {'server': 'http://localhost:3000'}
        with open(config_file_path, 'w') as file:
            yaml.dump(config, file)


def get_server_url():
    init_config()
    config_path = os.path.expanduser('~') + '/.config/syncomatic/config.yml'
    with open(config_path, 'r') as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
        return config['server']


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
        log('Syncomatic archive dir doesn\'t exist. Creating...')
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
    file_name = project_name + '.tar.gz'
    open(file_name, 'wb').write(r.content)
    if (r.status_code == 200):
        log('Downloaded!', 'SUCCESS')
        log('Extracting project...')
        tar = tarfile.open(file_name)
        tar.extractall('..')
        tar.close()
        os.remove(file_name)
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


def setup_remote():
    if (len(sys.argv) == 2):
        log('Current server URL: ' + get_server_url())
    else:
        new_url = sys.argv[2]
        log('Changed remote URL to ' + new_url)


get_server_url()

if (len(sys.argv) == 1):
    show_help()
elif (sys.argv[1] == 'send'):
    send_directory()
elif (sys.argv[1] == 'pull'):
    pull_directory()
elif (sys.argv[1] == 'remote'):
    setup_remote()
else:
    log('Doing nothing')
