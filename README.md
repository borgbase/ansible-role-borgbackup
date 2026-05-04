# Ansible Role: BorgBackup Client

[![Test](https://github.com/borgbase/ansible-role-borgbackup/actions/workflows/main.yml/badge.svg)](https://github.com/borgbase/ansible-role-borgbackup/actions/workflows/main.yml) [![Ansible Galaxy](https://img.shields.io/ansible/role/d/borgbase/ansible_role_borgbackup?logo=ansible&color=5cbec1&label=Ansible%20Galaxy)](https://galaxy.ansible.com/ui/standalone/roles/borgbase/ansible_role_borgbackup/)

Set up encrypted, compressed, deduplicated backups using [BorgBackup](https://borgbackup.readthedocs.io/en/stable/) and [Borgmatic](https://github.com/witten/borgmatic). The role supports Debian/Ubuntu, CentOS/Red Hat/Fedora, Archlinux, and Manjaro.

Works well with [BorgBase.com](https://www.borgbase.com). To manage BorgBase repos via Ansible, also see Andy Hawkins' [BorgBase Collection](https://galaxy.ansible.com/adhawkins/borgbase).

## Breaking changes in v2

- Public variables now use grouped `borgbackup_*` dictionaries.
- Legacy flat variables such as `borg_repository`, `borg_user`, and `borgmatic_timer` are rejected.
- Borgmatic 1.8.0 or newer is required.
- The role uses one modern borgmatic config template and no longer supports borgmatic 1.7 config rendering.

## Example playbook with root as backup user, distro package install, and cron

```yaml
- hosts: all
  roles:
    - role: borgbase.ansible_role_borgbackup
      borgbackup_install:
        method: package
      borgbackup_config:
        encryption_passphrase: CHANGEME
        repositories:
          - ssh://xxxxxx@xxxxxx.repo.borgbase.com/./repo
        source_directories:
          - /var/www
        hooks:
          before_backup:
            - echo "`date` - Starting backup."
          postgresql_databases:
            - name: users
              hostname: database1.example.org
              port: 5433
```

## Example playbook with service user and systemd timer

```yaml
- hosts: all
  roles:
    - role: borgbase.ansible_role_borgbackup
      borgbackup_user:
        name: backupuser
        group: backupuser
      borgbackup_timer:
        type: systemd
      borgbackup_config:
        encryption_passphrase: CHANGEME
        repositories:
          - ssh://xxxxxx@xxxxxx.repo.borgbase.com/./repo
        source_directories:
          - /var/www
        retention:
          keep_hourly: 3
          keep_daily: 7
          keep_weekly: 4
          keep_monthly: 6
```

## Example playbook with additional borgmatic options

```yaml
- hosts: all
  roles:
    - role: borgbase.ansible_role_borgbackup
      borgbackup_config:
        encryption_passphrase: CHANGEME
        repositories:
          - ssh://xxxxxx@xxxxxx.repo.borgbase.com/./repo
        source_directories:
          - /var/www
        extra:
          uptime_kuma:
            push_url: https://uptime.kuma.example.com/abcd1234
          ntfy:
            topic: backups
            server: https://ntfy.sh
          verbosity: 1
```

## Installation

Download from Ansible Galaxy:

```bash
ansible-galaxy install borgbase.ansible_role_borgbackup
```

Clone the latest version from GitHub:

```bash
git clone https://github.com/borgbase/ansible-role-borgbackup.git roles/ansible_role_borgbackup
```

## Role Variables

The role accepts partial dictionaries. For example, setting only `borgbackup_timer.type` keeps all other timer defaults.

### `borgbackup_install`

- `method`: `pip`, `uv`, `package`, or `none`. Defaults to `pip`.
- `venv_path`: virtualenv path for pip installs, or uv tool directory for uv installs. Defaults to `/opt/borgmatic`.
- `borg_version`: optional borgbackup version constraint for pip and uv installs.
- `borgmatic_version`: borgmatic version constraint for pip and uv installs. Defaults to `>=1.8.0`.
- `require_epel`: require `epel-release` before package installs on Enterprise Linux.
- `uv_bin`: uv executable for uv installs. Defaults to `uv`. The role does not install uv itself.
- `dep_packages`, `pip_packages`, `distro_packages`, `python_bin`: platform override hooks.

### `borgbackup_user`

- `name`: backup user. Defaults to `root`.
- `group`: backup group. Defaults to `root`.
- `create`: create the local user and group when `name` is not `root`. Defaults to `true`.
- `shell`: shell for a created user. Defaults to `/bin/bash`.
- `sudo`: manage sudoers rules for a non-root user. Defaults to `true`.

### `borgbackup_ssh`

- `key_type`: SSH key type. Defaults to `ed25519`.
- `key_name`: SSH key filename. Defaults to `id_<key_type>`.
- `key_path`: private key path. Defaults to the backup user's `.ssh` directory.
- `key_comment`: public key comment.
- `command`: explicit borgmatic `ssh_command`.

### `borgbackup_config`

- `repositories`: required repository path, list of paths, or list of borgmatic repository dictionaries.
- `name`: config filename under `/etc/borgmatic`. Defaults to `config.yaml`.
- `source_directories`: local paths to back up. Defaults to `/etc/hostname`.
- `one_file_system`, `exclude_patterns`, `exclude_from`, `exclude_caches`, `exclude_if_present`, `compression`, `lock_wait`: borgmatic source and storage settings.
- `encryption_passphrase`, `encryption_passcommand`, `remote_path`, `upload_rate_limit`: repository access settings.
- `store_atime`, `store_ctime`, `umask`, `relocated_repo_access_is_ok`, `unknown_unencrypted_repo_access_is_ok`: borgmatic storage flags.
- `retention`: borgmatic `keep_*` retention settings.
- `checks`, `check_last`: borgmatic consistency checks.
- `hooks`: borgmatic hooks and database backup configuration.
- `extra`: additional borgmatic config merged into the generated config.

### `borgbackup_timer`

- `type`: `cron`, `systemd`, `none`, or empty. Defaults to `cron`.
- `name`: cron file and job name. Defaults to `borgmatic`.
- `hour`, `minute`: schedule. Defaults to a deterministic per-host random time between 00:00 and 04:58.
- `flags`: extra scheduler flags passed to borgmatic.
- `enabled`: enable and start the systemd timer. Defaults to `true`.
- `systemd_no_new_privileges`: systemd `NoNewPrivileges` value. Defaults to `yes`.

## Layering inventory across group_vars and host_vars

The role's variables are dictionaries. Ansible's default variable precedence replaces dict variables wholesale rather than merging them, so setting `borgbackup_user: {group: backup}` in `host_vars` would wipe out the `name` key inherited from `group_vars`. Two patterns avoid this without changing the role.

### Per-host scalars referenced from the role call

The simplest and most common approach: keep the dict structure in the playbook and reference per-host scalars via Jinja. Plain scalars layer correctly across `group_vars` and `host_vars` without any merging.

```yaml
# playbook.yml
- hosts: all
  roles:
    - role: borgbase.ansible_role_borgbackup
      borgbackup_install:
        method: package
      borgbackup_config:
        repositories:
          - "{{ borgbackup_repository }}"
        encryption_passphrase: "{{ borgbackup_passphrase }}"
```

```yaml
# host_vars/host1.example.com.yml
borgbackup_repository: ssh://abc123@abc123.repo.borgbase.com/./repo
borgbackup_passphrase: 'PASSPHRASE'
  ...
```

Use this pattern for repository URLs, passphrases, and other per-host values. Group-wide defaults can live in `group_vars/all/` and be overridden in `host_vars/` exactly like any plain Ansible scalar.

### Inventory-driven dicts via `combine`

When you want the dict itself to live in inventory (e.g. a fully inventory-driven setup), define the base as a separate variable and rebuild the role's input via the `combine` filter:

```yaml
# group_vars/all/borgbackup.yml
borgbackup_user_base:
  name: backupuser
  group: backupuser
  shell: /bin/bash

borgbackup_user: "{{ borgbackup_user_base }}"
```

```yaml
# host_vars/foo.yml
borgbackup_user: "{{ borgbackup_user_base | combine({'group': 'something'}) }}"
```

The role then receives the merged dict and applies its own defaults on top, so the effective precedence is `role defaults < group base < host overrides`. Use `combine(..., recursive=true)` if your override touches nested keys (e.g. inside `borgbackup_config.retention`).

Avoid setting `DEFAULT_HASH_BEHAVIOUR=merge` in `ansible.cfg` — it has been deprecated since Ansible 2.13, applies controller-globally, and can break unrelated roles.

## v1 to v2 migration map

| v1 variable | v2 location |
| --- | --- |
| `borg_install_method` | `borgbackup_install.method` |
| `borg_venv_path` | `borgbackup_install.venv_path` |
| `borg_version` | `borgbackup_install.borg_version` |
| `borgmatic_version` | `borgbackup_install.borgmatic_version` |
| `borg_user` | `borgbackup_user.name` |
| `borg_group` | `borgbackup_user.group` |
| `backup_create_local_user` | `borgbackup_user.create` |
| `borg_ssh_key_type` | `borgbackup_ssh.key_type` |
| `borg_ssh_key_name` | `borgbackup_ssh.key_name` |
| `borg_ssh_key_file_path` | `borgbackup_ssh.key_path` |
| `borg_ssh_key_comment` | `borgbackup_ssh.key_comment` |
| `borg_ssh_command` | `borgbackup_ssh.command` |
| `borg_repository` | `borgbackup_config.repositories` |
| `borg_source_directories` | `borgbackup_config.source_directories` |
| `borg_encryption_passphrase` | `borgbackup_config.encryption_passphrase` |
| `borg_encryption_passcommand` | `borgbackup_config.encryption_passcommand` |
| `borg_exclude_patterns` | `borgbackup_config.exclude_patterns` |
| `borg_exclude_from` | `borgbackup_config.exclude_from` |
| `borg_retention_policy` | `borgbackup_config.retention` |
| `borgmatic_checks` | `borgbackup_config.checks` |
| `borgmatic_hooks` | `borgbackup_config.hooks` |
| `borgmatic_custom_config` | `borgbackup_config.extra` |
| `borgmatic_timer` | `borgbackup_timer.type` |
| `borgmatic_timer_cron_name` | `borgbackup_timer.name` |
| `borgmatic_timer_hour` | `borgbackup_timer.hour` |
| `borgmatic_timer_minute` | `borgbackup_timer.minute` |
| `borgmatic_timer_flags` | `borgbackup_timer.flags` |
| `borgmatic_timer_enabled` | `borgbackup_timer.enabled` |
| `borgmatic_systemd_nonewprivileges` | `borgbackup_timer.systemd_no_new_privileges` |

## Contributing

Pull requests are welcome when they add features that are relevant for a meaningful number of users. To run tests locally, install Docker and run:

```bash
pip install -r requirements-dev.txt
molecule test
```

## License

MIT/BSD

## Author

© 2018-2026 Manuel Riel and contributors.
