# Ansible Role: BorgBackup Client

[![Test](https://github.com/borgbase/ansible-role-borgbackup/actions/workflows/main.yml/badge.svg)](https://github.com/borgbase/ansible-role-borgbackup/actions/workflows/main.yml) [![Ansible Galaxy](https://img.shields.io/ansible/role/48519)](https://galaxy.ansible.com/m3nu/ansible_role_borgbackup)

Set up encrypted, compressed and deduplicated backups using [BorgBackup](https://borgbackup.readthedocs.io/en/stable/) and [Borgmatic](https://github.com/witten/borgmatic). Currently supports Debian/Ubuntu, CentOS/Red Hat/Fedora, Archlinux and Manjaro.

Works great with [BorgBase.com](https://www.borgbase.com) - Simple and Secure Hosting for your Borg Repositories. To manage BorgBase repos via Ansible, also see Andy Hawkins' [BorgBase Collection](https://galaxy.ansible.com/adhawkins/borgbase).

Main features:
- Set up Borg and Borgmatic
- Add cron job at random time
- Provision new remote [BorgBase.com](https://www.borgbase.com) repo for storing backups (optional)


## Example Playbook

```
- hosts: webservers
  roles:
  - role: m3nu.ansible_role_borgbackup
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


## Role Variables

### Required Arguments
- `borg_repository`: Full path to repository. Your own server or [BorgBase.com](https://www.borgbase.com) repo. Not required when using auto creation of repositories. Can be a list if you want to backup to multiple repositories.
- `borg_source_directories`: List of local folders to back up.

### Optional Arguments
- `borg_encryption_passcommand`: The standard output of this command is used to unlock the encryption key.
- `borg_encryption_passphrase`: Password to use for repokey or keyfile. Empty if repo is unencrypted.
- `borg_exclude_from`: Read exclude patterns from one or more separate named files, one pattern per line.
- `borg_exclude_patterns`: Paths or patterns to exclude from backup. See [official documentation](https://borgbackup.readthedocs.io/en/stable/usage/help.html#borg-help-patterns) for more.
- `borg_lock_wait_time`: Config maximum seconds to wait for acquiring a repository/cache lock. Defaults to 5 seconds.
- `borg_one_file_system`: Don't cross file-system boundaries. Defaults to `true`
- `borg_remote_path`: Path to the borg executable on the remote. It will default to `borg`.
- `borg_remote_rate_limit`: Remote network upload rate limit in kiBytes/second.
- `borg_retention_policy`: Retention policy for how many backups to keep in each category (daily, weekly, monthly, etc).
- `borg_ssh_command`: Command to use instead of just "ssh". This can be used to specify ssh options.
- `borgmatic_check_last`: Number of archives to check. Defaults to `3`
- `borgmatic_checks`: List of consistency checks. Defaults to `['repository']`
- `borgmatic_config_name`: Name to use for the borgmatic config file. Defaults to `config.yaml`
- `borgmatic_cron_checks_day`: Day when cron job for infrequent checks will run. Defaults to `{{ 28 | random }}`
- `borgmatic_cron_checks_hour`: Hour when cron job for infrequent checks will run. Defaults to `{{ range(7, 24) | random }}`
- `borgmatic_cron_checks_minute`: Minute when cron job for infrequent checks will run. Defaults to  `{{ 59 | random }}`
- `borgmatic_cron_hour`: Hour when regular create and prune cron job will run. Defaults to `{{ 6 | random }}`
- `borgmatic_cron_minute`: Minute when regular create and prune cron job will run. Defaults to  `{{ 59 | random }}`
- `borgmatic_hooks`: Hooks to monitor your backups e.g. with [Healthchecks](https://healthchecks.io/). See [official documentation](https://torsion.org/borgmatic/docs/how-to/monitor-your-backups/) for more.
- `borgmatic_large_repo`: Less frequent, monthly repo checking. Defaults to `true`
- `borgmatic_relocated_repo_access_is_ok`: Bypass Borg error about a repository that has been moved. Defaults to `false`
- `borgmatic_store_atime`: Store atime into archive. Defaults to `true`
- `borgmatic_store_ctime`: Store ctime into archive. Defaults to `true`
- `ssh_key_file`: Path to a private ssh key file (default is `.ssh/id_ed25519`). It generates a ed25519 key if the file doesn't exist yet.
- `borg_version`: Force a specific borg version to be installed
- `borgmatic_version`: Force a specific borgmatic version to be installed


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
