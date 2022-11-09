#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os

from ansible.module_utils.basic import AnsibleModule


class K0sInstall(object):
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
        self.force = module.params.get("force")
        self.config = module.params.get("config")
        self.data_dir = module.params.get("data_dir")
        self.enable_worker = module.params.get("enable_worker")
        self.token_file = module.params.get("token_file")
        self.arguments = module.params.get("arguments")

        self._controller_systemd_unit_file = "/etc/systemd/system/k0scontroller.service"
        self._worker_systemd_unit_file = "/etc/systemd/system/k0sworker.service"

        module.log(msg="----------------------------")
        module.log(msg=f" k0s          : {self._k0s}")
        module.log(msg=f" state        : {self.state}")
        module.log(msg=f" force        : {self.force}")
        module.log(msg=f" config       : {self.config}")
        module.log(msg=f" data_dir     : {self.data_dir}")
        module.log(msg=f" enable_worker: {self.enable_worker}")
        module.log(msg=f" token_file   : {self.token_file}")
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

        result = self.k0s_install()

        return result

    def k0s_install(self):
        """
        """
        _failed = True
        _changed = False
        _cmd = None
        _msg = "initial call"

        if self.force:
            self.module.log(msg="force mode ...")
            if self.state == "controller" and os.path.isfile(self._controller_systemd_unit_file):
                os.remove(self._controller_systemd_unit_file)

            if self.state == "worker" and os.path.isfile(self._worker_systemd_unit_file):
                os.remove(self._worker_systemd_unit_file)

        if self.state in ["initial-controller", "controller"]:
            if not self.config or not os.path.isfile(self.config):
                return dict(
                    msg=f"config file {self.config} not exists",
                    changed=False,
                    failed=True
                )

            if os.path.isfile(self._controller_systemd_unit_file):
                return dict(
                    msg=f"systemd unit file {self._controller_systemd_unit_file} already created.",
                    changed=False,
                    failed=False
                )

        if self.state == "worker":
            if os.path.isfile(self._worker_systemd_unit_file):
                return dict(
                    msg=f"systemd unit file {self._worker_systemd_unit_file} already created.",
                    changed=False,
                    failed=False
                )

        args = []
        args.append(self._k0s)
        args.append("install")

        if self.state in ["initial-controller", "controller"]:
            args.append("controller")
        else:
            args.append(self.state)

        args.append("--data-dir")
        args.append(self.data_dir)

        if self.state in ["initial-controller", "controller"] and self.enable_worker:
            args.append("--enable-worker")

        if self.config is not None and os.path.isfile(self.config):
            args.append("--config")
            args.append(self.config)

        if self.token_file is not None and os.path.isfile(self.token_file):
            args.append("--token-file")
            args.append(self.token_file)

        if len(self.arguments) > 0:
            for arg in self.arguments:
                args.append(arg)

        self.module.log(msg=f" - args {args}")

        rc, out, err = self._exec(args)

        if rc == 0:
            if self.state in ["initial-controller", "controller"]:
                if self._verify_unit_file(self._controller_systemd_unit_file):
                    _msg = f"systemd unit file {self._controller_systemd_unit_file} successful created.",

            if self.state == "worker":
                if self._verify_unit_file(self._worker_systemd_unit_file):
                    _msg = f"systemd unit file {self._worker_systemd_unit_file} successful created.",

            _failed = False
            _changed = True
            _msg = _msg
            _cmd = " ".join(args)
        else:
            return dict(
                rc=rc,
                cmd=" ".join(args),
                msg=err,
                failed=True
            )

        return dict(
            rc=rc,
            failed=_failed,
            changed=_changed,
            cmd=_cmd,
            msg=_msg
        )

    def _verify_unit_file(self, unit_file):
        """
        """
        if os.path.isfile(self._controller_systemd_unit_file):
            if self.config is not None and os.path.isfile(self.config):
                file_size = int(os.path.getsize(self.config))
                if file_size > 0:
                    return True

                return False

            return True

    def _remove_directory(self, directory):
        """
        """
        self.module.log(msg=f"remove directory {directory}")

        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

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
            force=dict(
                required=False,
                default=False,
                type=bool
            ),
            state=dict(
                default="worker",
                choices=["initial-controller", "controller", "worker"]
            ),
            config=dict(
                required=False,
                type='str'
            ),
            token_file=dict(
                required=False,
                type='str'
            ),
            data_dir=dict(
                required=False,
                default="/var/lib/k0s",
                type='str'
            ),
            enable_worker=dict(
                required=False,
                default=False,
                type=bool
            ),
            arguments=dict(
                required=False,
                default=[],
                type=list
            )
        ),
        supports_check_mode=True,
    )

    k = K0sInstall(module)
    result = k.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
