# Ansible Role: BorgBackup Client

[![Test](https://github.com/borgbase/ansible-role-borgbackup/actions/workflows/main.yml/badge.svg)](https://github.com/borgbase/ansible-role-borgbackup/actions/workflows/main.yml) [![Ansible Galaxy](https://img.shields.io/ansible/role/48519)](https://galaxy.ansible.com/m3nu/ansible_role_borgbackup)

Set up encrypted, compressed and deduplicated backups using [BorgBackup](https://borgbackup.readthedocs.io/en/stable/) and [Borgmatic](https://github.com/witten/borgmatic). Currently supports Debian/Ubuntu, CentOS/Red Hat/Fedora, Archlinux and Manjaro.

Works great with [BorgBase.com](https://www.borgbase.com) - Simple and Secure Hosting for your Borg Repositories. To manage BorgBase repos via Ansible, also see Andy Hawkins' [BorgBase Collection](https://galaxy.ansible.com/adhawkins/borgbase).

Main features:
- Set up Borg and Borgmatic
- Add systemd timer random time
- Provision new remote [BorgBase.com](https://www.borgbase.com) repo for storing backups (optional)


## Example Playbook with root as backup user and Cron timer

```
- hosts: webservers
  roles:
  - role: m3nu.ansible_role_borgbackup
    borg_encryption_passphrase: CHANGEME
    borg_repository: m5vz9gp4@m5vz9gp4.repo.borgbase.com:repo
    borgmatic_timer: cron
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
    borgmatic_hooks:
      before_backup:
      - echo "`date` - Starting backup."
      postgresql_databases:
      - name: users
        hostname: database1.example.org
        port: 5433
```

## Example Playbook with service user and Systemd timer
`` Attention: `` The following implementation leads to problems.
If you already use this role and use the user: "root" or the SSH key id_ed25519!

```
- hosts: webservers
  roles:
  - role: m3nu.ansible_role_borgbackup
    borg_encryption_passphrase: CHANGEME
    borg_repository: m5vz9gp4@m5vz9gp4.repo.borgbase.com:repo
    borgmatic_timer: systemd
    borg_ssh_key_file_path: "{{ backup_user_info.home }}/.ssh/backup"
    borg_ssh_command: "ssh -i {{ borg_ssh_key_file_path }} -o StrictHostKeyChecking=no"
    borgbackup_user: "srv_backup"
    borgbackup_group: "srv_backup"
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
    borgmatic_hooks:
      before_backup:
      - echo "`date` - Starting backup."
      postgresql_databases:
      - name: users
        hostname: database1.example.org
        port: 5433
```


## Installation

Download from Ansible Galaxy
```
$ ansible-galaxy install m3nu.ansible_role_borgbackup
```

Clone latest version from Github
```
$ git clone https://github.com/borgbase/ansible-role-borgbackup.git roles/ansible_role_borgbackup
```


## Tags:
This Role supports the following ansible tags:

- `install_backup`: Tag for only run that part.
- `backup_install_helper` Tag to additionally install the backup helper skripts. Currently only docker.

### Example
To install the helper scrit.

```
$ ANSIBLE_STDOUT_CALLBACK=yaml ansible-playbook test.example.com -t backup_install_helper
```


## Role Variables

### Required Arguments
- `borg_repository`: Full path to repository. Your own server or [BorgBase.com](https://www.borgbase.com) repo. Not required when using auto creation of repositories. Can be a list if you want to backup to multiple repositories.


### Optional Arguments
- `borg_dep_packages`: Dependancy Packages to install `borg(backup)` and `borgmatic`.
- `borg_distro_packages`: contains the names of distributions packages for `borg(backup)` and `borgmatic`, only used if `borg_install_method` is set to `package`.
- `borg_encryption_passcommand`: The standard output of this command is used to unlock the encryption key.
- `borg_encryption_passphrase`: Password to use for repokey or keyfile. Empty if repo is unencrypted.
- `borg_exclude_from`: Read exclude patterns from one or more separate named files, one pattern per line.
- `borg_exclude_patterns`: Paths or patterns to exclude from backup. See [official documentation](https://borgbackup.readthedocs.io/en/stable/usage/help.html#borg-help-patterns) for more.
- `borg_install_method`: By default `pip` is used to install borgmatic. To install via your distributions package manager set this to `package` and (if needed) overwrite the `borg_distro_packages` variable to contain your distributions package names required to install borgmatic. Note that many distributions ship outdated versions of borgbackup and borgmatic; use at your own risk.
- `borg_lock_wait_time`: Config maximum seconds to wait for acquiring a repository/cache lock. Defaults to 5 seconds.
- `borg_one_file_system`: Don't cross file-system boundaries. Defaults to `true`
- `borg_pip_packages`: Dependancy Packages (pip) to install `borg(backup)` and `borgmatic`.
- `borg_remote_path`: Path to the borg executable on the remote. It will default to `borg`.
- `borg_remote_rate_limit`: Remote network upload rate limit in kiBytes/second.
- `borg_retention_policy`: Retention policy for how many backups to keep in each category (daily, weekly, monthly, etc).
- `borg_source_directories`: List of local folders to back up. Default is `/etc/hostname` to prevent an empty backup.
- `borg_ssh_key_name`: Name of the SSH public and pivate key. Default `id_ed25519`
- `borg_ssh_key_file_path`: SSH-key to be used. Default `~/.ssh/{{ borg_ssh_key_name }}`
- `borg_ssh_key_type`: The algorithm used to generate the SSH private key. Choose: `rsa`, `dsa`, `rsa1`, `ecdsa`, `ed25519`. Default: `ed25519`
- `borg_ssh_command`: Command to use instead of just "ssh". This can be used to specify ssh options.
- `borg_version`: Force a specific borg version to be installed
- `borg_venv_path`: Path to store the venv for `borg(backup)` and `borgmatic`

- `borgmatic_check_last`: Number of archives to check. Defaults to `3`
- `borgmatic_checks`: List of consistency checks. Defaults to `['repository']`
- `borgmatic_config_name`: Name to use for the borgmatic config file. Defaults to `config.yaml`
- `borgmatic_timer_hour`: Hour when regular create and prune cron/systemd-timer job will run. Defaults to `{{ 6 | random }}`
- `borgmatic_timer_minute`: Minute when regular create and prune cron/systemd-timer job will run. Defaults to  `{{ 59 | random }}`
- `borgmatic_hooks`: Hooks to monitor your backups e.g. with [Healthchecks](https://healthchecks.io/). See [official documentation](https://torsion.org/borgmatic/docs/how-to/monitor-your-backups/) for more.
- `borgmatic_timer`: If the variable is set, a timer is installed. A choice must be made between `cron` and `systemd`.
- `borgmatic_relocated_repo_access_is_ok`: Bypass Borg error about a repository that has been moved. Defaults to `false`
- `borgmatic_store_atime`: Store atime into archive. Defaults to `true`
- `borgmatic_store_ctime`: Store ctime into archive. Defaults to `true`
- `borgmatic_version`: Force a specific borgmatic version to be installed

- `borgbackup_user`: Name of the User to create Backups (Service Account)
- `borgbackup_group`: Name of the Group to create Backups (Service Account)


## Contributing

Pull requests (PR) are welcome, as long as they add features that are relevant for a meaningful number of users. All PRs are tested for style and functionality. To run tests locally (needs Docker):

```
$ pip install -r requirements-dev.txt
$ molecule test
```

## License

MIT/BSD

## Author

© 2018-2023 Manuel Riel and contributors.
