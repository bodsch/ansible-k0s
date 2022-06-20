
# Ansible Role:  `k0s`

Create a Kubernetes Cluster using Ansible.

Use vanilla upstream Kubernetes distro [k0s](https://github.com/k0sproject/k0s).

Similar to [movd/k0s-ansible](https://github.com/movd/k0s-ansible), **but** better (i think so ;) )


[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/bodsch/ansible-k0s/CI)][ci]
[![GitHub issues](https://img.shields.io/github/issues/bodsch/ansible-k0s)][issues]
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/bodsch/ansible-k0s)][releases]

[ci]: https://github.com/bodsch/ansible-k0s/actions
[issues]: https://github.com/bodsch/ansible-k0s/issues?q=is%3Aopen+is%3Aissue
[releases]: https://github.com/bodsch/ansible-k0s/releases


## Why better?

This Ansible role can be used atomically.
If no changes are necessary, none will be made.

Avoid `command` calls.
Wherever possible, separate Ansible modules are used for this.

One role for all cases.

Soon also available via ansible-galaxy



## supported Operating systems

Tested on

* ArchLinux
* Debian based
    - Debian 10 / 11

## usage

```yaml
k0s_version: 1.23.6+k0s.1
k0s_release_download_url: https://github.com/k0sproject/k0s/releases

k0s_system_user: "{{ ansible_user }}"
k0s_system_group: "{{ ansible_user }}"

k0s_cluster_nodes:
  initial_controller: ""
  controllers: []
  workers: []

k0s_config_dir: /etc/k0s
k0s_data_dir: /var/lib/k0s
k0s_libexec_dir: /usr/libexec/k0s

k0s_token_expiry: "1h"

k0s_use_custom_config: false

k0s_direct_download: false

k0s_artifacts_dir: "{{ inventory_dir }}/artifacts"
```

### tags

- `k0s_configure`
- `k0s_controller`
- `k0s_download`
- `k0s_initial_configure`
- `k0s_install`
- `k0s_prepare`
- `k0s_service`
- `k0s_worker`

### kubectl

```bash
export ...

```



## Contribution

Please read [Contribution](CONTRIBUTING.md)


## Development,  Branches (Git Tags)

The `master` Branch is my *Working Horse* includes the "latest, hot shit" and can be complete broken!

If you want to use something stable, please use a [Tagged Version](https://gitlab.com/bodsch/ansible-k0s/-/tags)!

## Credits

- [Moritz](https://github.com/movd)



