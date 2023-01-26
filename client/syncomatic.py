#!/usr/bin/python3

import sys
from datetime import datetime
import tarfile
import os.path
import os
import requests
import json


def init_config():
    config_path = os.path.expanduser('~') + '/.config/syncomatic/'
    if not os.path.exists(config_path):
        log('Syncomatic config dir doesn\'t exist. Creating...')
        os.makedirs(config_path)
    config_file_path = config_path + 'config.json'
    if not os.path.isfile(config_file_path):
        log('Syncomatic config file doesn\'t exist. Creating default...')
        config = {'server': 'http://localhost:3000'}
        with open(config_file_path, 'w') as file:
            json.dump(config, file)


def get_server_url():
    config_path = os.path.expanduser('~') + '/.config/syncomatic/config.json'
    with open(config_path, 'r') as file:
        config = json.load(file)
        return config['server']


def log(message, status='INFO'):
    print('[', datetime.now(), '] (' + status + ')', message)


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, 'w:gz') as tar:
        if os.path.isfile('.sm'):
            with open('.sm', 'r') as sm_file:
                config = json.load(sm_file)
                sm_file.close()
                files = os.listdir(".")
                for file in files:
                    if config is None:
                        tar.add(file)
                    elif not file.replace(source_dir, "") in config["ignored"]:
                        tar.add(file)
                tar.close()
        else:
            files = os.listdir(".")
            for file in files:
                tar.add(file)


def get_dir_name():
    return os.getcwd().split('/').pop()


def get_project_name():
    if not os.path.isfile('.sm'):
        return get_dir_name(), False
    else:
        with open('.sm', 'r') as sm_file:
            config = json.load(sm_file)
            sm_file.close()
            project_name = config['project']
            if (project_name is None):
                return get_dir_name(), False
            else:
                return project_name, True


def send_directory():
    log('Compressing directory...')
    if not os.path.exists('/var/tmp/syncomatic'):
        log('Syncomatic archive dir doesn\'t exist. Creating...')
        os.makedirs('/var/tmp/syncomatic/')
    make_tarfile('/var/tmp/syncomatic/archive.tar.gz', os.getcwd())
    log('Compressed!')
    log('Uploading directory...')
    with open('/var/tmp/syncomatic/archive.tar.gz', 'rb') as file:
        project_name, _ = get_project_name()
        params = {
            'project_name': project_name
        }
        r = requests.post(get_server_url() + '/upload', params=params,
                          files={'archive.tar.gz': file})
        if r.status_code == 200:
            log('Uploaded successfully!', 'SUCCESS')
        else:
            log('Upload failed: ' + str(r.status_code), 'FAIL')
    log('Finished! Cleaning up...')
    os.remove('/var/tmp/syncomatic/archive.tar.gz')
    log('Done!')


def project_exists_remote(project):
    params = {
        'project_name': project
    }
    r = requests.get(get_server_url() + '/exists', params=params)
    return r.status_code == 200


def download_project_remote(project_name, specified_by_user, from_config_file):
    params = {
        'project_name': project_name
    }
    r = requests.get(get_server_url() + '/download', params=params)
    file_name = project_name + '.tar.gz'
    open(file_name, 'wb').write(r.content)
    if (r.status_code == 200):
        log('Downloaded!', 'SUCCESS')
        log('Extracting project...')
        tar = tarfile.open(file_name)
        tar.extractall('.' if specified_by_user or from_config_file else '..')
        log("Extracted! Cleaning up...")
        tar.close()
        os.remove(file_name)
        log("All done!")
    else:
        log('Download Failed :(', 'FAIL')


def pull_directory():
    log('Pulling directory...')
    project_name = ''
    specified_by_user = False
    from_config_file = False
    if len(sys.argv) == 2:
        log('No project specified, falling back to current directory')
        project_name, from_config_file = get_project_name()
    else:
        project_name = sys.argv[2]
        specified_by_user = True
        log('Project name has been specified. Searching for ' + project_name)

    if project_exists_remote(project_name):
        log('Found project ' + project_name + ' remotely. Downloading...')
        download_project_remote(
            project_name, specified_by_user, from_config_file)
    else:
        log('Could not find project ' + project_name + ' remotely.', 'FAIL')


def show_help():
    print('Syncomatic Help\n\npush [project name] - Push the current directory\npull [project name] - Pull the current directory\nremote - View the current server URL\n\nConfig is in ~/.config/syncomatic/config.yml\nYou only need to set the `server` parameter to your Syncomatic server. By default, it is set to localhost on port 3000\n\nYou can create a file in the root of a project called .sm to set a project name override. Line 1 of this file should be the project name')


def setup_remote():
    log('Current server URL: ' + get_server_url())


init_config()

if (len(sys.argv) == 1):
    show_help()
elif (sys.argv[1] == 'push'):
    send_directory()
elif (sys.argv[1] == 'pull'):
    pull_directory()
elif (sys.argv[1] == 'remote'):
    setup_remote()
else:
    log('Doing nothing')
