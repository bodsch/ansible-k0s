
from ansible.parsing.dataloader import DataLoader
from ansible.template import Templar

import json
import pytest
import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('k0s-controller-1')


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
        "{0}/bin",
        "{0}/etcd",
        "{0}/manifests",
        "{0}/manifests/api-config",
        "{0}/manifests/autopilot",
        "{0}/manifests/bootstraprbac",
        "{0}/manifests/calico",
        "{0}/manifests/calico_init",
        "{0}/manifests/coredns",
        "{0}/manifests/helm",
        "{0}/manifests/kubelet",
        "{0}/manifests/kubeproxy",
        "{0}/manifests/kuberouter",
        "{0}/manifests/metrics",
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
        "{0}/bin/etcd",
        "{0}/bin/kube-apiserver",
        "{0}/bin/kube-controller-manager",
        "{0}/bin/kube-scheduler",
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
