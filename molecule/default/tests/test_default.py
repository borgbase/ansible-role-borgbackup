import os
# import pytest
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_borgmatic_config(host):
    f = host.file('/etc/borgmatic/config.yml')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


# @pytest.mark.parametrize('file, content', [
#   ("/etc/firewalld/zones/public.xml", "<service name=\"http\"/>"),
#   ("/var/www/html/index.html", "Managed by Ansible")
# ])
# def test_files(host, file, content):
#     file = host.file(file)

#     assert file.exists
#     assert file.contains(content)
