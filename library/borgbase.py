#!/usr/bin/python

DOCUMENTATION = '''
---
module: borgbase
author: "Philipp Rintz (https://github.com/p-rintz)"
short_description: Ansible module for creating new repositories with borgbase.com
description:
  - Ansible Module for creating new repositories with borgbase.com including adding new ssh keys
version_added: "2.6"
'''

EXAMPLES = '''
- name: Create new repository for server in EU with new SSH_key and quota
  borgbase:
    repository_name: "{{ inventory_hostname }}"
    token: "Your Borgbase API Token"
    new_ssh_key: True
    ssh_key: "{{ some_variable }}"
    append_only: True
    quota_enable: True
    quota: 1000 #in GB
    region: eu
    alertdays: 2
  delegate_to: localhost
- name: Create new repository without new key and no quota/alerting in US region
  borgbase:
    repository_name: "{{ inventory_hostname }}"
    token: "Your Borgbase API Token"
    new_ssh_key: False
    ssh_key: "ssh-ed25519 AAAAC3Nz......aLqRJw+dl/E+2BJ xxx@yyy"
    region: us
  delegate_to: localhost
'''

from ansible.module_utils.basic import *
from ansible.module_utils.borgbase_api_client.client import GraphQLClient
from ansible.module_utils.borgbase_api_client.mutations import *
from ansible.module_utils.borgbase_api_client.queries import *


def get_key_id(ssh_key):
    res = client.execute(KEY_DETAILS)
    for i  in res['data']['sshList']:
        if i['keyData'] == ssh_key:
            key_id = i['id']
    return key_id

def add_ssh_key():
    key_name = 'Key for %s' % (module.params['repository_name'],)
    new_key_vars = {
        'name': key_name,
        'keyData': module.params['ssh_key']
    }
    res = client.execute(SSH_ADD, new_key_vars)
    new_key_id = res['data']['sshAdd']['keyAdded']['id']
    return new_key_id

def add_repo(key_id):
    if module.params['append_only']:
        access_level = 'appendOnlyKeys'
    else:
        access_level = 'fullAccessKeys'

    if not module.params['quota_enable']:
        new_repo_vars = {
            'name': module.params['repository_name'],
            'quotaEnabled': module.params['quota_enable'],
            access_level: [key_id],
            'alertDays': module.params['alertdays'],
            'region': module.params['region']
        }
    else:
        new_repo_vars = {
            'name': module.params['repository_name'],
            'quotaEnabled': module.params['quota_enable'],
            'quota': 1000*module.params['quota'],
            access_level: [key_id],
            'alertDays': module.params['alertdays'],
            'region': module.params['region']
        }
    res = client.execute(REPO_ADD, new_repo_vars)
    return res

def get_repo_id(name):
    res = client.execute(REPO_DETAILS)
    for repo in res['data']['repoList']:
        if repo['name'] == name:
            repo_id = repo['id']
            return repo_id
    return None

def edit_repo(repo_id, key_id):
    if module.params['append_only']:
        access_level = 'appendOnlyKeys'
    else:
        access_level = 'fullAccessKeys'

    if not module.params['quota_enable']:
        repo_vars = {
            'id': repo_id,
            'name': module.params['repository_name'],
            access_level: [key_id],
            'alertDays': module.params['alertdays'],
            'region': module.params['region']
        }
    else:
        repo_vars = {
            'id': repo_id,
            'name': module.params['repository_name'],
            'quotaEnabled': module.params['quota_enable'],
            'quota': 1000*module.params['quota'],
            access_level: [key_id],
            'alertDays': module.params['alertdays'],
            'region': module.params['region']
        }
    res = client.execute(REPO_EDIT, repo_vars)
    return res

def main():
    global module
    module = AnsibleModule(
             argument_spec  = dict(
                    repository_name = dict(
                        type='str',
                        required=True,
                    ),
                    token = dict(
                        required=True,
                        type='str',
                        no_log=True
                    ),
                    new_ssh_key = dict(
                        required=False,
                        default='True',
                        type='bool'
                    ),
                    ssh_key = dict(
                        required=True,
                        type='str'
                    ),
                    append_only = dict(
                        required=False,
                        default='True',
                        type='bool'
                    ),
                    quota_enable = dict(
                        required=False,
                        default='False',
                        type='bool'
                    ),
                    quota = dict(
                        required=False,
                        type='int'
                    ),
                    region = dict(
                        required=True,
                        type='str',
                        choice=["eu", "us"]
                    ),
                    alertdays = dict(
                        required=False,
                        default=0,
                        type='int'
                    )
            )
    )

    global client
    client = GraphQLClient(module.params['token'])

    # Add new SSH key or get ID of old key
    if module.params['new_ssh_key']:
        key_id = add_ssh_key()
    else:
        key_id = get_key_id(module.params['ssh_key'])

    # Check if repo with given name exists
    repo_id = get_repo_id(module.params['repository_name'])

    if repo_id is None:
        # Add new repo using the key
        res = add_repo(key_id)

    else:
        # Edit the repo
        res = edit_repo(repo_id, key_id)

    # Setup information for Ansible
    result = dict(
        changed = False,
        data = '',
        type = '',
        key_id = ''
    )

    # Test for success and change info
    if type(res) == dict:
        result['changed'] = True
        if repo_exist:
            result['data'] = res["data"]["repoEdit"]["repoEdited"]
        else:
            result['data'] = res['data']['repoAdd']['repoAdded']
        result['key_id'] = key_id
        module.exit_json(**result)
    else:
        result['data'] = res
        result['type'] = type(res)
        result['key_id'] = key_id
        module.fail_json(msg="Failed creating new respository.", **result)


if __name__ == '__main__':
    main()
