# Ansible Role: BorgBackup Client

[![Test](https://github.com/borgbase/ansible-role-borgbackup/actions/workflows/main.yml/badge.svg)](https://github.com/borgbase/ansible-role-borgbackup/actions/workflows/main.yml) [![Ansible Galaxy](https://img.shields.io/ansible/role/48519)](https://galaxy.ansible.com/borgbase/ansible_role_borgbackup)

Set up encrypted, compressed and deduplicated backups using [BorgBackup](https://borgbackup.readthedocs.io/en/stable/) and [Borgmatic](https://github.com/witten/borgmatic). Currently supports Debian/Ubuntu, CentOS/Red Hat/Fedora, Archlinux and Manjaro.

Works great with [BorgBase.com](https://www.borgbase.com) - Simple and Secure Hosting for your Borg Repositories. To manage BorgBase repos via Ansible, also see Andy Hawkins' [BorgBase Collection](https://galaxy.ansible.com/adhawkins/borgbase).

**Main features**
- Install Borg and Borgmatic from PyPi or distro packages
- Set up Borgmatic config
- Schedule regular backups using Cron or Systemd timer

## Breaking changes
- Older versions of this role set up a separate Cron job for creating and checking
  backups. With recent Borgmatic version, this feature is now managed in Borgmatic.
  As a result the extra Cron job will be removed by this role.
- Older versions of this role only supported Cron for scheduling. If you use
  Systemd timers, be sure to remove the Cron job in `/etc/cron.d/borgmatic` first.
  The role will also alert you when trying to use both timers.

## Example playbook with root as backup user and Cron timer

```
- hosts: all
  roles:
  - role: borgbase.ansible_role_borgbackup
    borg_encryption_passphrase: CHANGEME
    borg_repository: ssh://xxxxxx@xxxxxx.repo.borgbase.com/./repo
    borg_source_directories:
      - /var/www
    borgmatic_hooks:
      before_backup:
      - echo "`date` - Starting backup."
      postgresql_databases:
      - name: users
        hostname: database1.example.org
        port: 5433
```

## Example playbook with service user and Systemd timer

```
- hosts: all
  roles:
  - role: borgbase.ansible_role_borgbackup
    borg_encryption_passphrase: CHANGEME
    borg_repository: ssh://xxxxxx@xxxxxx.repo.borgbase.com/./repo
    borgmatic_timer: systemd
    borg_user: "backupuser"
    borg_group: "backupuser"
    borg_source_directories:
      - /var/www
    borg_retention_policy:
      keep_hourly: 3
      keep_daily: 7
      keep_weekly: 4
      keep_monthly: 6
```



## Installation

Download from Ansible Galaxy
```
$ ansible-galaxy install borgbase.ansible_role_borgbackup
```

Clone latest version from Github
```
$ git clone https://github.com/borgbase/ansible-role-borgbackup.git roles/ansible_role_borgbackup
```


## Role Variables

### Required Variables
- `borg_repository`: Full path to repository. Your own server or [BorgBase.com](https://www.borgbase.com) repo.
  Can be a list if you want to backup to multiple repositories.

### Optional Variables
- `borg_dep_packages`: Dependency Packages to install `borg(backup)` and `borgmatic`.
- `borg_distro_packages`: contains the names of distributions packages for `borg(backup)` and `borgmatic`, only used if `borg_install_method` is set to `package`.
- `borg_encryption_passcommand`: The standard output of this command is used to unlock the encryption key.
- `borg_encryption_passphrase`: Password to use for repokey or keyfile. Empty if repo is unencrypted.
- `borg_exclude_from`: Read exclude patterns from one or more separate named files, one pattern per line.
- `borg_exclude_patterns`: Paths or patterns to exclude from backup. See [official documentation](https://borgbackup.readthedocs.io/en/stable/usage/help.html#borg-help-patterns) for more.
- `borg_install_method`: By default `pip` is used to install borgmatic. To install via your distributions package manager set this to `package` and (if needed) overwrite the `borg_distro_packages` variable to contain your distributions package names required to install borgmatic. Note that many distributions ship outdated versions of borgbackup and borgmatic; use at your own risk.
- `borg_require_epel`: When using `borg_install_method: package` on RHEL-based distributions, the EPEL repo is required. To disable the check (e.g. when using a custom mirror instead of the `epel-release` package), set this to `false`. Defaults to `{{ ansible_os_family == 'RedHat' and ansible_distribution != 'Fedora' }}` (i.e. `true` on Enterprise Linux-based distros).
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
- `borg_ssh_command`: Command to use instead of just "ssh". This can be used to specify SSH options.
- `borg_version`: Force a specific borg version to be installed
- `borg_venv_path`: Path to store the venv for `borg(backup)` and `borgmatic`

- `borgmatic_check_last`: Number of archives to check. Defaults to `3`
- `borgmatic_checks`: List of consistency checks. Defaults to monthly checks. See [docs](https://torsion.org/borgmatic/docs/how-to/deal-with-very-large-backups/#check-frequency) for all options.
- `borgmatic_config_name`: Name to use for the Borgmatic config file. Defaults to `config.yaml`
- `borgmatic_timer_hour`: Hour when regular create and prune cron/systemd-timer job will run. Defaults to `{{ 6 | random }}`
- `borgmatic_timer_minute`: Minute when regular create and prune cron/systemd-timer job will run. Defaults to  `{{ 59 | random }}`
- `borgmatic_hooks`: Hooks to monitor your backups e.g. with [Healthchecks](https://healthchecks.io/). See [official documentation](https://torsion.org/borgmatic/docs/how-to/monitor-your-backups/) for more.
- `borgmatic_timer`: If the variable is set, a timer is installed. A choice must be made between `cron` and `systemd`.
- `borgmatic_relocated_repo_access_is_ok`: Bypass Borg error about a repository that has been moved. Defaults to `false`
- `borgmatic_store_atime`: Store atime into archive. Defaults to `true`
- `borgmatic_store_ctime`: Store ctime into archive. Defaults to `true`
- `borgmatic_version`: Force a specific borgmatic version to be installed

- `borg_user`: Name of the User to create Backups (service account)
- `borg_group`: Name of the Group to create Backups (service account)


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
