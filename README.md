# Ansible Role: BorgBackup Client

An Ansible Role that installs that sets up BorgBackup on Debian/Ubuntu.

## Role Variables

- `borg_repository` (required): Full path to repository. Your own server or [BorgBase.com](https://www.borgbase.com).
- `borg_encryption_passphrase` (optional): Password to use for repokey or keyfile. Empty if repo is unencrypted.
- `borg_source_directories` (required): List of local folders to back up.
- `borg_exclude_patterns` (optional): List of local folders to exclude.


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
      - /srv/www/upload
```

## License

MIT/BSD

## Author

Manuel Riel. Created for [BorgBase.com](https://www.borgbase.com) - Simple and Secure Hosting for your Borg Repositories.
