# Ansible Role: BorgBackup Client
The following example installs and configures the Borgmatic client and also initializes the repo on the BackupServer.

## Fullautomated Playbook with service user -> this has sudo power
```
- name: Configure backup
  hosts: test.lab
  pre_tasks:
  - name: Get home of {{ borgbackup_user }}
    ansible.builtin.user:
      name: "{{ borgbackup_user }}"
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
    borgbackup_user: "srv_backup"
    borgbackup_group: "srv_backup"
    borg_repository: "{{ vault_borg.backup_user }}@{{ backup_server }}:{{ backup_path }}/{{ ansible_host }}"
    borg_ssh_key_file_path: "{{ backup_user_info.home }}/.ssh/backup"
    borg_ssh_command: "ssh -i {{ borg_ssh_key_file_path }} -o StrictHostKeyChecking=no"
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
            cmd: "su - {{ borgbackup_user }} -c '/usr/local/bin/borgmatic rcreate --encryption keyfile --append-only'"

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