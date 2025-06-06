
# Ansible Role:  `bodsch.k0s`

Create a Kubernetes Cluster using Ansible.

Use vanilla upstream Kubernetes distro [k0s](https://github.com/k0sproject/k0s).

Similar to [movd/k0s-ansible](https://github.com/movd/k0s-ansible), **but** better (i think so ;) )

> I am currently unable to find a sensible use for a local Kubernetes installation.
> I will therefore stop maintaining this repository due to lack of time.


[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/bodsch/ansible-k0s/main.yml?logo=github&branch=main)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-k0s?logo=github)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-k0s?logo=github)][releases]
[![Ansible Downloads](https://img.shields.io/ansible/role/d/bodsch/k0s?logo=ansible)][galaxy]

[ci]: https://github.com/bodsch/ansible-k0s/actions
[issues]: https://github.com/bodsch/ansible-k0s/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-k0s/releases
[galaxy]: https://galaxy.ansible.com/bodsch/k0s


If `latest` is set for `k0s_version`, the role tries to install the latest release version.  
**Please use this with caution, as incompatibilities between releases may occur!**

The binaries are installed below `/usr/local/bin/k0s/${k0s_version}` and later linked to `/usr/bin`.  
This should make it possible to downgrade relatively safely.

The k0s archive is stored on the Ansible controller, unpacked and then the binaries are copied to the target system.
The cache directory can be defined via the environment variable `CUSTOM_LOCAL_TMP_DIRECTORY`.  
By default it is `${HOME}/.cache/ansible/k0s`.  
If this type of installation is not desired, the download can take place directly on the target system.  
However, this must be explicitly activated by setting `k0s_direct_download` to `true`.

## Requirements & Dependencies

Ansible Collections

- [bodsch.core](https://github.com/bodsch/ansible-collection-core)
- [bodsch.scm](https://github.com/bodsch/ansible-collection-scm)

```bash
ansible-galaxy collection install bodsch.core
ansible-galaxy collection install bodsch.scm
```
or
```bash
ansible-galaxy collection install --requirements-file collections.yml
```


## Why better?

This Ansible role can be used atomically.  
If no changes are necessary, none will be made.

Avoid `command` calls.  
Wherever possible, separate Ansible modules are used for this.

One role for all cases.


## supported Operating systems

Tested on

* ArchLinux
* Debian based
    - Debian 10 / 11 / 12
    - Ubuntu 20.04 / 22.04 / 24.04


## working implementation

The example of a working implementation can be viewed at [GitLab](https://gitlab.com/integration-tests/k0s).  
A suitable infrastructure based on KVM and Terraform can be created in the repository.

There are some tests in `molecule` that could be used.
For reasons that are not clear to me, the tests in a docker container are not very meaningful.
I have therefore extended the tests with the *Vagrant* driver.

There is a `Makefile` to start the tests:

```shell
make test -e TOX_SCENARIO=multi-worker
```


```shell
make test -e TOX_SCENARIO=vagrant-multi-worker
```


## Contribution

Please read [Contribution](CONTRIBUTING.md)


## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://github.com/bodsch/ansible-k0s/tags)!


## usage

```yaml
k0s_version: 1.25.2+k0s.0
k0s_release_download_url: https://github.com/k0sproject/k0s/releases

k0s_system_user: k0s
k0s_system_group: k0s

k0s_config_dir: /etc/k0s
k0s_data_dir: /var/lib/k0s
k0s_libexec_dir: /usr/libexec/k0s

k0s_direct_download: false

k0s_worker_on_controller: false
k0s_no_taints: false

k0s_force: false
k0s_debug: false
k0s_verbose: false

k0s_cluster_nodes:
  initial_controller: ""
  controllers: []
  workers: []

k0s_extra_arguments:
  controller:
    - --enable-metrics-scraper

k0s_config_overwrites: {}

k0s_token_expiry: "15m"

k0s_artifacts_dir: "{{ inventory_dir }}/artifacts"
```

### `k0s_config_overwrites`

Extension of the automatically created `k0s.yaml`
The structure must correspond to the created configuration. An example file can be viewed [here](./k0s_config.example).


### single controller

```yaml
k0s_cluster_nodes:
  initial_controller: controller-1.k0s.local
  controllers: []
  workers: []
```


### one controller with multi workers

```yaml
k0s_cluster_nodes:
  initial_controller: controller-1.k0s.local
  controllers: []
  workers:
    - worker-1.k0s.local
    - worker-2.k0s.local
    - worker-3.k0s.local
```

### multi controllers with multi workers

```yaml
k0s_cluster_nodes:
  initial_controller: controller-1.k0s.local
  controllers:
    - controller-2.k0s.local
    - controller-3.k0s.local
  workers:
    - worker-1.k0s.local
    - worker-2.k0s.local
    - worker-3.k0s.local
```


## Credits

- [Moritz](https://github.com/movd)

## other dokumentaions

[Upgrading a k0s cluster in-place from single-master to HA](https://vadosware.io/post/upgrading-a-k0s-cluster-from-single-to-ha/#get-all-your-workloads-off-the-current-master-controllerworker-role-node)

