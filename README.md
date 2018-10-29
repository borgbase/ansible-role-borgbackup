# Ansible Role: BorgBackup Client

An Ansible Role that installs that sets up BorgBackup on Debian/Ubuntu.

## Role Variables

- `borg_repository` (required): Full path to repository. Your own server or [BorgBase.com](https://www.borgbase.com) repo.
- `borg_source_directories` (required): List of local folders to back up.
- `borg_encryption_passphrase` (optional): Password to use for repokey or keyfile. Empty if repo is unencrypted.
- `borgmatic_config_name` (optional): Name to use for the borgmatic config file. Defaults to `config.yml`
- `borg_exclude_patterns` (optional): Paths or patterns to exclude from backup. See [official documentation](https://borgbackup.readthedocs.io/en/stable/usage/help.html#borg-help-patterns) for more.


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
```

## Planned features
- [ ] Testing via vagrant
- [ ] Multiple repos in one role-call instead of callng this role multiple times.


## License

MIT/BSD

## Author

Manuel Riel. Created for [BorgBase.com](https://www.borgbase.com) - Simple and Secure Hosting for your Borg Repositories.
