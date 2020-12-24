# Ansible Role: BorgBackup Client

![Test](https://github.com/m3nu/ansible-role-borgbackup/workflows/Test/badge.svg) [![Ansible Galaxy](https://img.shields.io/ansible/role/30531)](https://galaxy.ansible.com/m3nu/ansible_role_borgbackup)

Set up encrypted, compressed and deduplicated backups using [BorgBackup](https://borgbackup.readthedocs.io/en/stable/) and [Borgmatic](https://github.com/witten/borgmatic). Currently supports Debian/Ubuntu and CentOS/Red Hat.

Works great with [BorgBase.com](https://www.borgbase.com) - Simple and Secure Hosting for your Borg Repositories.

Main features:
- Set up Borg and Borgmatic
- Add cron job at random time
- Provision new remote [BorgBase.com](https://www.borgbase.com) repo for storing backups (optional)


## Example Playbook

```
- hosts: webservers
  roles:
  - role: borgbackup
    borg_encryption_passphrase: CHANGEME
    borg_repository: m5vz9gp4@m5vz9gp4.repo.borgbase.com:repo
    borg_source_directories:
      - /srv/www
      - /var/lib/automysqlbackup
    borg_exclude_patterns:
      - /srv/www/old-sites
    borg_retention_policy:
      keep_hourly: 3
      keep_daily: 7
      keep_weekly: 4
      keep_monthly: 6
```


## Installation

Download from Ansible Galaxy

```
$ ansible-galaxy install m3nu.ansible_role_borgbackup
```

Clone to local folder

```
$ git clone https://github.com/borgbase/ansible-role-borgbackup.git roles/borgbackup
```


## Role Variables

### Required Arguments
- `borg_repository`: Full path to repository. Your own server or [BorgBase.com](https://www.borgbase.com) repo. Not required when using auto creation of repositories. Can be a list if you want to backup to multiple repositories.
- `borg_source_directories`: List of local folders to back up.

### Optional Arguments
- `borg_encryption_passphrase`: Password to use for repokey or keyfile. Empty if repo is unencrypted.
- `borgmatic_checks`: List of consistency checks. Defaults to `['repository']`
- `borgmatic_check_last`: Number of archives to check. Defaults to `3`
- `borgmatic_store_atime`: Store atime into archive. Defaults to `true`
- `borgmatic_store_ctime`: Store ctime into archive. Defaults to `true`
- `borgmatic_relocated_repo_access_is_ok`: Bypass Borg error about a repository that has been moved. Defaults to `false`
- `borgmatic_config_name`: Name to use for the borgmatic config file. Defaults to `config.yaml`
- `borgmatic_large_repo`: Less frequent, monthly repo checking. Defaults to `true`
- `borgmatic_failure_command`: Run this command when an error occurs. E.g. `curl -s -F "token=xxx" -F "user=xxx" -F "message=Error during backup" https://api.pushover.net/1/messages.json`
- `borgmatic_before_backup_command`: Run this command before the backup. E.g. `dump-a-database /to/file.sql`
- `borgmatic_after_backup_command`: Run this command after the backup. E.g. `rm /to/file.sql`
- `borgmatic_hooks`: Hooks to monitor your backups e.g. with [Healthchecks](https://healthchecks.io/). See [official documentation](https://torsion.org/borgmatic/docs/how-to/monitor-your-backups/) for more.
- `borg_exclude_patterns`: Paths or patterns to exclude from backup. See [official documentation](https://borgbackup.readthedocs.io/en/stable/usage/help.html#borg-help-patterns) for more.
- `borg_one_file_system`: Don't cross file-system boundaries. Defaults to `true`
- `borg_exclude_from`: Read exclude patterns from one or more separate named files, one pattern per line.
- `borg_lock_wait_time`: Config maximum seconds to wait for acquiring a repository/cache lock. Defaults to 5 seconds.
- `borg_ssh_command`: Command to use instead of just "ssh". This can be used to specify ssh options.
- `borg_remote_path`: Path to the borg executable on the remote. It will default to `borg`.
- `borg_remote_rate_limit`: Remote network upload rate limit in kiBytes/second.
- `borg_encryption_passcommand`: The standard output of this command is used to unlock the encryption key.
- `borg_retention_policy`: Retention policy for how many backups to keep in each category (daily, weekly, monthly, etc).
- `ssh_key_file`: Path to a private ssh key file (default is `.ssh/id_ed25519`). It generates a ed25519 key if the file doesn't exist yet.
- `borgmatic_cron_hour`: Hour when regular create and prune cron job will run. Defaults to `{{ 6 | random }}`
- `borgmatic_cron_minute`: Minute when regular create and prune cron job will run. Defaults to  `{{ 59 | random }}`
- `borgmatic_cron_checks_day`: Day when cron job for infrequent checks will run. Defaults to `{{ 28 | random }}`
- `borgmatic_cron_checks_hour`: Hour when cron job for infrequent checks will run. Defaults to `{{ range(7, 24) | random }}`
- `borgmatic_cron_checks_minute`: Minute when cron job for infrequent checks will run. Defaults to  `{{ 59 | random }}`


### Optional Arguments for [BorgBase.com](https://www.borgbase.com) repository auto creation
This role can also set up a new repository on BorgBase, using the arguments below. Thanks to [Philipp Rintz](https://github.com/p-rintz) for contribution of this feature.

- `create_repo`: Whether to let the role create the repository for the server. Default: False
- `bb_token`: Your [BorgBase.com](https://www.borgbase.com) API-Token. Should be Create Only for security reasons.
- `bb_region`: Which region the backups should be saved in. Choice: "eu" or "us".
- `bb_new_sshkey`: Whether to use the automatically created SSH_key. Default: True
- `bb_sshkey`: If there is a key already available on [BorgBase.com](https://www.borgbase.com) that should be used, it can be set with this variable. The key needs to be exactly the same, including key-comment.
- `bb_append`: Should the permission of the newly created repository be append only? Default: True
- `bb_quota`: To use a quota for the Server. Default: False
- `bb_quota_size`: Will need to be set if `bb_quota` is set to True. In Gigabyte.
- `bb_alertdays`: After how many days of no backup activity should alerts be sent out? Defaults to off. 
- `bb_repo_name`: What name the created repository should have. Defaults to the inventory_hostname.


### Use BorgBase Module Standalone
You can also use the BorgBase-Ansible module directly if needed:

```
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
```



## Planned features

- [x] Testing
- [ ] Multiple repos in one role-call instead of callng this role multiple times.
- [ ] Support more OSs, like Red Hat/Fedora/CentOS, SuSE, Gentoo, Slackware, Arch, BSD


## Contributing

Pull requests (PR) are welcome, as long as they add features that are relevant for a meaningful number of users. All PRs are tested for style and functionality. To run tests locally (needs Docker):

```
$ pip install -r requirements-dev.txt
$ molecule test
```

## License

MIT/BSD

## Author

© 2018-2020 Manuel Riel and contributors.
