#!/usr/bin/python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os
import json

from ansible.module_utils.basic import AnsibleModule


class K0sStatus(object):
    """
      Main Class
    """
    module = None

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self._k0s = module.get_bin_path('k0s', True)

        self.state = module.params.get("state")
        self.data_dir = module.params.get("data_dir")
        self.arguments = module.params.get("arguments")

        module.log(msg="----------------------------")
        module.log(msg=f" k0s          : {self._k0s}")
        module.log(msg=f" state        : {self.state}")
        module.log(msg=f" data_dir     : {self.data_dir}")
        module.log(msg=f" arguments    : {self.arguments}")
        module.log(msg="----------------------------")

    def run(self):
        """
          runner
        """
        result = dict(
            rc=1,
            failed=True,
            changed=False,
        )

        result = self.k0s_token()

        return result

    def k0s_token(self):
        """
            k0s status --help
            Get k0s instance status information

            Usage:
              k0s status [flags]

            Examples:
            The command will return information about system init, PID, k0s role, kubeconfig and similar.
        """
        _failed = True
        _changed = False
        _cmd = None
        _msg = "initial call"

        args = []
        args.append(self._k0s)
        args.append("status")
        # args.append("--data-dir")
        # args.append(self.data_dir)
        args.append("--out")
        args.append("json")

        self.module.log(msg=f" - args {args}")

        rc, out, err = self._exec(args)

        if rc == 0:
            _failed = False
            _changed = False
            _msg = out

            # defaults
            version = None
            role = None
            kubelet_auth_cfg = None
            admin_kube_config = None

            data = json.loads(out)  # json.dumps(, sort_keys=True)
            # self.module.log(msg=f"  {type(data)}")
            # self.module.log(msg=f"  {json.dumps(data)}")
            if isinstance(data, dict):
                version = data.get('Version')
                role = data.get('Role')
                kubelet_auth_cfg = data.get('K0sVars', {}).get('KubeletAuthConfigPath', None)
                admin_kube_config = data.get('K0sVars', {}).get('AdminKubeConfigPath', None)

            self.module.log(msg=f"  role: {role}")
            self.module.log(msg=f"  version: {version}")
            self.module.log(msg=f"  kubelet_auth_cfg: {kubelet_auth_cfg}")
            self.module.log(msg=f"  admin_kube_config: {admin_kube_config}")

            if self.state == "initial-controller":
                if kubelet_auth_cfg:
                    if os.path.isfile(kubelet_auth_cfg):
                        _msg = f"This k0s instance has already been successfully installed and configured in version {version}."
                    else:
                        _msg = f"This k0s instance has already been in version {version} installed and configured, but the auth configfile {kubelet_auth_cfg} is missing!"

            elif self.state == "controller":
                if admin_kube_config:
                    if os.path.isfile(admin_kube_config):
                        _msg = f"This k0s instance has already been successfully installed and configured in version {version}."

            return dict(
                rc=rc,
                cmd=" ".join(args),
                role=role,
                msg=_msg,
                version=version,
                state="installed",
                failed=_failed,
                changed=_changed
            )

        else:
            return dict(
                cmd=" ".join(args),
                msg=err,
                role=None,
                version=None,
                state="missing",
                # failed=False
            )

        return dict(
            failed=_failed,
            changed=_changed,
            cmd=_cmd,
            msg=_msg
        )

    def _exec(self, args):
        """
        """
        rc, out, err = self.module.run_command(args, check_rc=False)
        self.module.log(msg=f"  rc : '{rc}'")

        if rc != 0:
            self.module.log(msg=f"  out: '{out}'")
            self.module.log(msg=f"  err: '{err}'")
        return rc, out, err


# ===========================================
# Module execution.
#


def main():

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                default="worker",
                choices=["initial-controller", "controller", "worker"]
            ),
            data_dir=dict(
                required=False,
                default="/var/lib/k0s",
                type='str'
            ),
            arguments=dict(
                required=False,
                default=[],
                type=list
            )
        ),
        supports_check_mode=True,
    )

    k = K0sStatus(module)
    result = k.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
