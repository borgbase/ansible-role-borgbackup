# Additional Examples

## Custom SSH key for backups only

```
- hosts: webservers
  roles:
  - role: borgbase.ansible_role_borgbackup
    borg_encryption_passphrase: CHANGEME
    borg_repository: ssh://m5vz9gp4@m5vz9gp4.repo.borgbase.com/./repo
    borgmatic_timer: systemd
    borg_ssh_key_name: id_backup
    borg_ssh_command: "ssh -i {{ borg_ssh_key_file_path }} -o StrictHostKeyChecking=accept-new"
    borg_user: backupuser
    borg_group: backupuser
```

## Use service user and copy SSH key to target server

Installs and configures the Borgmatic client and also initializes the repo on the
remote backup server. (not tested)

```
- name: Configure backup
  hosts: test.lab
  pre_tasks:
  - name: Get home of {{ borg_user }}
    ansible.builtin.user:
      name: "{{ borg_user }}"
      state: present
    register: user_info
    changed_when: false
    check_mode: true  # Important, otherwise user will be created

  - name: Save the user_info, we need them for the home_dir
    ansible.builtin.set_fact:
      backup_user_info: "{{ user_info }}"
  vars_files: []
  vars:
    borg_encryption_passphrase: "CHANGEME"
    borg_repository: "USER@TARGET_SERVER:/PATH/TO/BACKUP"
    borg_user: "srv_backup"
    borg_group: "srv_backup"
    borg_ssh_key_name: id_backup
    borg_ssh_command: "ssh -i {{ borg_ssh_key_file_path }} -o StrictHostKeyChecking=accept-new"
    borgmatic_timer: systemd
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
  tasks:
    - name: Configure Borg Backup and Backupmatic
      tags:
        - always
        - install_backup
      ansible.builtin.include_role:
        name: ansible_role_borgbackup
        apply:
          tags:
            - always


    - name: Copy SSH-Key to Target {{ borg_repository }} and Init Repo
      tags:
        - never
        - backup_init_repo
      block:
        - name: Read ssh key
          ansible.builtin.slurp:
            src: "{{ borg_ssh_key_file_path }}.pub"
          register: backup_local_ssh_key

        - name: Set authorized key taken from file
          ansible.posix.authorized_key:
            # example:
            #   borg_repository: m5vz9gp4@m5vz9gp4.repo.borgbase.com:repo
            #   have three parts: "username"@"FQDN":"path/to/store/backup", specific:
            #     a) user: m5vz9gp4
            #     b) fqdn: m5vz9gp4.repo.borgbase.co
            #     c) dir: repo
            user: "{{ borg_repository | regex_search('(.*)@', '\\1') | first }}" # part a)
            state: present
            key: "{{ backup_local_ssh_key['content'] | b64decode }}"
          delegate_to: "{{ borg_repository | regex_search('@(.*):', '\\1') | first }}" # part b)

        - name: Init repository
          ansible.builtin.command:
            cmd: "su - {{ borg_user }} -c '/usr/local/bin/borgmatic rcreate --encryption keyfile --append-only'"

    - name: Activate systemd service and timer
      when:
        - borgmatic_timer is defined and borgmatic_timer == "systemd"
      tags:
        - never
        - backup_init_repo
      block:
        - name: Populate service facts
          ansible.builtin.service_facts:

        - name: Start borgmatic services
          ansible.builtin.systemd:
            name: "{{ item }}"
            state: started
            enabled: true
            masked: false
            daemon_reload: true
          when: "item in services"
          with_items:
            - borgmatic.service

        # bug: Need own section without masked else the timer are skipped
        - name: Start borgmatic timers
          ansible.builtin.systemd:
            name: "{{ item }}"
            state: started
            enabled: true
            daemon_reload: true
          with_items:
            - "borgmatic.timer"
```
