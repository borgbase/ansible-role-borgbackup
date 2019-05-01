# Ansible Role: BorgBackup Client

An Ansible Role that sets up automated remote backups on the target machine. Uses [BorgBackup](https://borgbackup.readthedocs.io/en/stable/) and [Borgmatic](https://github.com/witten/borgmatic). Currently supports Debian and Ubuntu.

## Role Variables

- `borg_repository` (required): Full path to repository. Your own server or [BorgBase.com](https://www.borgbase.com) repo.
- `borg_source_directories` (required): List of local folders to back up.
- `borg_encryption_passphrase` (optional): Password to use for repokey or keyfile. Empty if repo is unencrypted.
- `borgmatic_config_name` (optional): Name to use for the borgmatic config file. Defaults to `config.yml`
- `borgmatic_large_repo` (optional): Does repo-checking on a weekly basis instead of daily. Good for repos with 100GB+ size.
- `borg_exclude_patterns` (optional): Paths or patterns to exclude from backup. See [official documentation](https://borgbackup.readthedocs.io/en/stable/usage/help.html#borg-help-patterns) for more.
- `borg_one_file_system` (optional): Don't cross file-system boundaries. Defaults to `true`
- `borg_exclude_from` (optional): Read exclude patterns from one or more separate named files, one pattern per line.
- `borg_ssh_command` (optional): Command to use instead of just "ssh". This can be used to specify ssh options.
- `borg_encryption_passcommand` (optional): The standard output of this command is used to unlock the encryption key.

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
- [ ] Support more OSs, like Red Hat/Fedora/CentOS, SuSE, Gentoo, Slackware, Arch, BSD

## License

MIT/BSD

## Author

Manuel Riel. Created for [BorgBase.com](https://www.borgbase.com) - Simple and Secure Hosting for your Borg Repositories.
