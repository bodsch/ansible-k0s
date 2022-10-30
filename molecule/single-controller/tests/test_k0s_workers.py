
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

import json
import pytest
import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('k0s_workers')


def pp_json(json_thing, sort=True, indents=2):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


def base_directory():
    cwd = os.getcwd()

    if ('group_vars' in os.listdir(cwd)):
        directory = "../.."
        molecule_directory = "."
    else:
        directory = "."
        molecule_directory = "molecule/{}".format(os.environ.get('MOLECULE_SCENARIO_NAME'))

    return directory, molecule_directory


def read_ansible_yaml(file_name, role_name):
    ext_arr = ["yml", "yaml"]

    read_file = None

    for e in ext_arr:
        test_file = "{}.{}".format(file_name, e)
        if os.path.isfile(test_file):
            read_file = test_file
            break

    return "file={} name={}".format(read_file, role_name)


@pytest.fixture()
def get_vars(host):
    """

    """
    base_dir, molecule_dir = base_directory()
    distribution = host.system_info.distribution

    if distribution in ['debian', 'ubuntu']:
        os = "debian"
    elif distribution in ['redhat', 'ol', 'centos', 'rocky', 'almalinux']:
        os = "redhat"
    elif distribution in ['arch']:
        os = "archlinux"

    print(" -> {} / {}".format(distribution, os))

    file_defaults = read_ansible_yaml("{}/defaults/main".format(base_dir), "role_defaults")
    file_vars = read_ansible_yaml("{}/vars/main".format(base_dir), "role_vars")
    file_distibution = read_ansible_yaml("{}/vars/{}".format(base_dir, os), "role_distibution")
    file_molecule = read_ansible_yaml("{}/group_vars/all/vars".format(molecule_dir), "test_vars")

    defaults_vars = host.ansible("include_vars", file_defaults).get("ansible_facts").get("role_defaults")
    vars_vars = host.ansible("include_vars", file_vars).get("ansible_facts").get("role_vars")
    distibution_vars = host.ansible("include_vars", file_distibution).get("ansible_facts").get("role_distibution")
    molecule_vars = host.ansible("include_vars", file_molecule).get("ansible_facts").get("test_vars")

    ansible_vars = defaults_vars
    ansible_vars.update(vars_vars)
    ansible_vars.update(distibution_vars)
    ansible_vars.update(molecule_vars)

    templar = Templar(loader=DataLoader(), variables=ansible_vars)
    result = templar.template(ansible_vars, fail_on_undefined=False)

    return result


def test_directories(host, get_vars):
    """
    """
    data_directory = get_vars.get("k0s_data_dir", None)

    dirs = [
        "{0}/containerd",
        "{0}/images",
        "{0}/kubelet",
        "{0}/kubelet/pki",
        "{0}/kubelet/plugins",
        "{0}/kubelet/plugins_registry",
        "{0}/kubelet/pod-resources",
        "{0}/kubelet/pods",
    ]

    for directory in dirs:
        d = host.file(directory.format(data_directory))
        assert d.is_directory


def test_files(host, get_vars):
    """
    """
    data_directory = get_vars.get("k0s_data_dir", None)

    files = [
        "{0}/bin/containerd",
        "{0}/bin/containerd-shim",
        "{0}/bin/containerd-shim-runc-v1",
        "{0}/bin/containerd-shim-runc-v2",
        "{0}/bin/ip6tables",
        "{0}/bin/ip6tables-restore",
        "{0}/bin/ip6tables-save",
        "{0}/bin/iptables-restore",
        "{0}/bin/iptables-save",
        "{0}/bin/kubelet",
        "{0}/bin/runc",
        "{0}/bin/xtables-legacy-multi",
        "{0}/kubelet-bootstrap.conf",
        "{0}/kubelet-config.yaml",
        "{0}/kubelet.conf",
    ]

    for file in files:
        f = host.file(file.format(data_directory))
        assert f.exists


def test_service(host):
    """
        is service running and enabled
    """
    service = host.service("k0sworker")

    assert service.is_enabled
    assert service.is_running


def test_listen(host, get_vars):
    """
        test sockets
    """
    listening = host.socket.get_listening_sockets()
    interfaces = host.interface.names()
    eth = []

    if "eth0" in interfaces:
        eth = host.interface("eth0").addresses

    for i in listening:
        print(i)

    for i in interfaces:
        print(i)

    for i in eth:
        print(i)

    # kube-router
    # assert host.socket("tcp://0.0.0.0:8080").is_listening
    # assert host.socket("tcp://0.0.0.0:20244").is_listening
    # assert host.socket("tcp://127.0.0.1:50051").is_listening
    # assert host.socket("tcp://{0}:179".format(eth[0])).is_listening
    # assert host.socket("tcp://{0}:50051".format(eth[0])).is_listening
    # kubelet
    assert host.socket("tcp://127.0.0.1:10248").is_listening
    assert host.socket("tcp://0.0.0.0:10250").is_listening
    # kube-proxy
    assert host.socket("tcp://127.0.0.1:10249").is_listening
    assert host.socket("tcp://0.0.0.0:10256").is_listening
    # sockets
    assert host.socket("unix:///run/k0s/containerd.sock").is_listening
