# Additional Examples

## Custom SSH key for backups only

```yaml
- hosts: webservers
  roles:
    - role: borgbase.ansible_role_borgbackup
      borgbackup_user:
        name: backupuser
        group: backupuser
      borgbackup_timer:
        type: systemd
      borgbackup_ssh:
        key_name: id_backup
        key_comment: backup key
        command: "ssh -i /home/backupuser/.ssh/id_backup -o StrictHostKeyChecking=accept-new"
      borgbackup_config:
        encryption_passphrase: CHANGEME
        repositories:
          - ssh://m5vz9gp4@m5vz9gp4.repo.borgbase.com/./repo
```

## Use service user and copy SSH key to target server

Installs and configures the Borgmatic client and also initializes the repo on the remote backup server. This example keeps the repository initialization as explicit playbook tasks.

```yaml
- name: Configure backup
  hosts: test.lab
  vars:
    backup_repository: USER@TARGET_SERVER:/PATH/TO/BACKUP
    backup_user: srv_backup

  tasks:
    - name: Configure Borg Backup and Borgmatic
      ansible.builtin.include_role:
        name: ansible_role_borgbackup
      vars:
        borgbackup_user:
          name: "{{ backup_user }}"
          group: "{{ backup_user }}"
        borgbackup_ssh:
          key_name: id_backup
          command: "ssh -i /home/{{ backup_user }}/.ssh/id_backup -o StrictHostKeyChecking=accept-new"
        borgbackup_timer:
          type: systemd
        borgbackup_config:
          encryption_passphrase: CHANGEME
          repositories:
            - "{{ backup_repository }}"
          source_directories:
            - /srv/www
            - /var/lib/automysqlbackup
          exclude_patterns:
            - /srv/www/old-sites
          retention:
            keep_hourly: 3
            keep_daily: 7
            keep_weekly: 4
            keep_monthly: 6
          hooks:
            before_backup:
              - echo "`date` - Starting backup."

    - name: Read SSH key
      ansible.builtin.slurp:
        src: "/home/{{ backup_user }}/.ssh/id_backup.pub"
      register: backup_local_ssh_key
      tags:
        - never
        - backup_init_repo

    - name: Set authorized key on target server
      ansible.posix.authorized_key:
        user: "{{ backup_repository | regex_search('(.*)@', '\\1') | first }}"
        state: present
        key: "{{ backup_local_ssh_key.content | b64decode }}"
      delegate_to: "{{ backup_repository | regex_search('@(.*):', '\\1') | first }}"
      tags:
        - never
        - backup_init_repo

    - name: Initialize repository
      ansible.builtin.command:
        cmd: "su - {{ backup_user }} -c '/usr/local/bin/borgmatic rcreate --encryption keyfile --append-only'"
      changed_when: true
      tags:
        - never
        - backup_init_repo
```
