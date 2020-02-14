# Ansible Role: BorgBackup Client

An Ansible Role that sets up automated remote backups on the target machine. Uses [BorgBackup](https://borgbackup.readthedocs.io/en/stable/) and [Borgmatic](https://github.com/witten/borgmatic). Currently supports Debian/Ubuntu and CentOS/RHEL/Fedora.

## Role Variables

### Required Arguments
- `borg_repository`: Full path to repository. Your own server or [BorgBase.com](https://www.borgbase.com) repo. Only required if not using the [BorgBase.com](https://www.borgbase.com) auto creation of repositories.
- `borg_source_directories`: List of local folders to back up.

### Optional Arguments
- `borg_encryption_passphrase`: Password to use for repokey or keyfile. Empty if repo is unencrypted.
- `borgmatic_large_repo`: Does repo-checking on a weekly basis instead of daily. Good for repos with 100GB+ size.
- `borgmatic_failure_command`: Run this command when an error occurs. E.g. `curl -s -F "token=xxx" -F "user=xxx" -F "message=Error during backup" https://api.pushover.net/1/messages.json`
- `borgmatic_before_backup_command`: Run this command before the backup. E.g. `dump-a-database /to/file.sql`
- `borgmatic_after_backup_command`: Run this command after the backup. E.g. `rm /to/file.sql`
- `borgmatic_failure_command`: Run this command when an error occurs. E.g. `curl -s -F "token=xxx" -F "user=xxx" -F "message=Error during backup" https://api.pushover.net/1/messages.json`
- `borg_exclude_patterns`: Paths or patterns to exclude from backup. See [official documentation](https://borgbackup.readthedocs.io/en/stable/usage/help.html#borg-help-patterns) for more.
- `borg_one_file_system`: Don't cross file-system boundaries. Defaults to `true`
- `borg_exclude_from`: Read exclude patterns from one or more separate named files, one pattern per line.
- `borg_lock_wait_time`: Config maximum seconds to wait for acquiring a repository/cache lock. Defaults to 5 seconds.
- `borg_ssh_command`: Command to use instead of just "ssh". This can be used to specify ssh options.
- `borg_remote_path`: Path to the borg executable on the remote. It will default to `borg`.
- `borg_encryption_passcommand`: The standard output of this command is used to unlock the encryption key.
- `borg_retention_policy`: Retention policy for how many backups to keep in each category (daily, weekly, monthly, etc).
- `ssh_key_file`: Path to a private ssh key file (default is `.ssh/id_ed25519`). It generates a ed25519 key if the file doesn't exist yet.

### Optional Arguments for [BorgBase.com](https://www.borgbase.com) repository auto creation
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

## Planned features
- [ ] Testing via vagrant
- [ ] Multiple repos in one role-call instead of callng this role multiple times.
- [ ] Support more OSs, like Red Hat/Fedora/CentOS, SuSE, Gentoo, Slackware, Arch, BSD

## License

MIT/BSD

## Author

Manuel Riel. Created for [BorgBase.com](https://www.borgbase.com) - Simple and Secure Hosting for your Borg Repositories.
