# coding: utf-8
from __future__ import unicode_literals

from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

import json
import pytest
import os

import testinfra.utils.ansible_runner

HOST= 'k0s-controller'

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts(HOST)


def pp_json(json_thing, sort=True, indents=2):
    if type(json_thing) is str:
        print(json.dumps(json.loads(json_thing), sort_keys=sort, indent=indents))
    else:
        print(json.dumps(json_thing, sort_keys=sort, indent=indents))
    return None


def base_directory():
    """
    """
    cwd = os.getcwd()

    if 'group_vars' in os.listdir(cwd):
        directory = "../.."
        molecule_directory = "."
    else:
        directory = "."
        molecule_directory = f"molecule/{os.environ.get('MOLECULE_SCENARIO_NAME')}"

    return directory, molecule_directory


def read_ansible_yaml(file_name, role_name):
    """
    """
    read_file = None

    for e in ["yml", "yaml"]:
        test_file = "{}.{}".format(file_name, e)
        if os.path.isfile(test_file):
            read_file = test_file
            break

    return f"file={read_file} name={role_name}"


@pytest.fixture()
def get_vars(host):
    """
        parse ansible variables
        - defaults/main.yml
        - vars/main.yml
        - vars/${DISTRIBUTION}.yaml
        - molecule/${MOLECULE_SCENARIO_NAME}/group_vars/all/vars.yml
    """
    base_dir, molecule_dir = base_directory()
    distribution = host.system_info.distribution
    operation_system = None

    if distribution in ['debian', 'ubuntu']:
        operation_system = "debian"
    elif distribution in ['redhat', 'ol', 'centos', 'rocky', 'almalinux']:
        operation_system = "redhat"
    elif distribution in ['arch', 'artix']:
        operation_system = f"{distribution}linux"

    # print(" -> {} / {}".format(distribution, os))
    # print(" -> {}".format(base_dir))

    file_defaults = read_ansible_yaml(f"{base_dir}/defaults/main", "role_defaults")
    file_vars = read_ansible_yaml(f"{base_dir}/vars/main", "role_vars")
    file_distibution = read_ansible_yaml(f"{base_dir}/vars/{operation_system}", "role_distibution")
    file_molecule = read_ansible_yaml(f"{molecule_dir}/group_vars/all/vars", "test_vars")
    # file_host_molecule = read_ansible_yaml("{}/host_vars/{}/vars".format(base_dir, HOST), "host_vars")

    defaults_vars = host.ansible("include_vars", file_defaults).get("ansible_facts").get("role_defaults")
    vars_vars = host.ansible("include_vars", file_vars).get("ansible_facts").get("role_vars")
    distibution_vars = host.ansible("include_vars", file_distibution).get("ansible_facts").get("role_distibution")
    molecule_vars = host.ansible("include_vars", file_molecule).get("ansible_facts").get("test_vars")
    # host_vars          = host.ansible("include_vars", file_host_molecule).get("ansible_facts").get("host_vars")

    ansible_vars = defaults_vars
    ansible_vars.update(vars_vars)
    ansible_vars.update(distibution_vars)
    ansible_vars.update(molecule_vars)
    # ansible_vars.update(host_vars)

    templar = Templar(loader=DataLoader(), variables=ansible_vars)
    result = templar.template(ansible_vars, fail_on_undefined=False)

    return result


def test_directories(host, get_vars):
    """
    """
    data_directory = get_vars.get("k0s_data_dir", None)

    dirs = [
        "{0}/bin",
        "{0}/etcd",
        "{0}/manifests",
        "{0}/manifests/autopilot",
        "{0}/manifests/bootstraprbac",
        "{0}/manifests/calico",
        "{0}/manifests/calico_init",
        "{0}/manifests/coredns",
        "{0}/manifests/helm",
        "{0}/manifests/kubelet",
        "{0}/manifests/kubeproxy",
        "{0}/manifests/kuberouter",
        "{0}/manifests/metricserver",
        "{0}/pki",
        "{0}/pki/etcd",
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
        "{0}/bin/etcd",
        "{0}/bin/iptables",
        "{0}/bin/iptables-restore",
        "{0}/bin/iptables-save",
        "{0}/bin/kube-apiserver",
        "{0}/bin/kube-controller-manager",
        "{0}/bin/kube-scheduler",
        "{0}/bin/kubelet",
        "{0}/bin/runc",
        "{0}/pki/admin.conf",
        "{0}/pki/admin.crt",
        "{0}/pki/admin.key",
        "{0}/pki/etcd/server.crt",
        "{0}/pki/scheduler.conf",
        "{0}/pki/scheduler.crt",
        "{0}/pki/scheduler.key",
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
    service = host.service("k0scontroller")

    assert service.is_enabled
    assert service.is_running

# runs not in docker ... WHY!?
# def test_listen(host, get_vars):
#     """
#         test sockets
#     """
#     listening = host.socket.get_listening_sockets()
#     interfaces = host.interface.names()
#     eth = []
#
#     if "eth0" in interfaces:
#         eth = host.interface("eth0").addresses
#
#     for i in listening:
#         print(i)
#
#     for i in interfaces:
#         print(i)
#
#     for i in eth:
#         print(i)
#
#     # k0s
#     # runs not in docker ... WHY!?
#     # assert host.socket("tcp://0.0.0.0:9443").is_listening
#     # etcd
#     assert host.socket("tcp://127.0.0.1:2379").is_listening
#     assert host.socket(f"tcp://{eth[0]}:2380").is_listening
#     # kube-apiserver
#     assert host.socket("tcp://0.0.0.0:6443").is_listening
#     # kube-controller
#     assert host.socket("tcp://127.0.0.1:10257").is_listening
#     # kube-scheduler
#     assert host.socket("tcp://127.0.0.1:10259").is_listening
#     # konnectivity-se
#     #  runs not in docker ... WHY!?
#     # assert host.socket("tcp://0.0.0.0:8092").is_listening
#     # assert host.socket("tcp://127.0.0.1:8133").is_listening
#     # assert host.socket("tcp://0.0.0.0:8132").is_listening
#     # sockets
#     # assert host.socket("unix:///run/k0s/konnectivity-server/konnectivity-server.sock").is_listening
