#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os

from ansible.module_utils.basic import AnsibleModule


class K0sReset(object):
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

        self.config = module.params.get("config")
        self.data_dir = module.params.get("data_dir")
        self.arguments = module.params.get("arguments")

        self._controller_systemd_unit_file = "/etc/systemd/system/k0scontroller.service"
        self._worker_systemd_unit_file = "/etc/systemd/system/k0sworker.service"

        module.log(msg="----------------------------")
        module.log(msg=f" k0s          : {self._k0s}")
        module.log(msg=f" config       : {self.config}")
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

        result = self.k0s_reset()

        return result

    def k0s_reset(self):
        """
            k0s stop
            Stop the k0s service configured on this host. Must be run as root (or with sudo)

            k0s reset
            Uninstall k0s. Must be run as root (or with sudo)

            Usage:
              k0s reset [flags]

            Flags:
              -c, --config string          config file, use '-' to read the config from stdin (default "/etc/k0s/k0s.yaml")
                  --cri-socket string      container runtime socket to use, default to internal containerd. Format: [remote|docker]:[path-to-socket]
                  --debugListenOn string   Http listenOn for Debug pprof handler (default ":6060")
              -h, --help                   help for reset
                  --status-socket string   Full file path to the socket file. (default "/run/k0s/status.sock")
              -v, --verbose                Verbose logging (default: false)

            Global Flags:
                  --data-dir string   Data Directory for k0s (default: /var/lib/k0s). DO NOT CHANGE for an existing setup, things will break!
                  --debug             Debug logging (default: false)

        """
        _failed = True
        _changed = False
        _cmd = None
        _msg = "initial call"

        args = []
        args.append(self._k0s)
        args.append("stop")

        rc, out, err = self._exec(args)

        args = []
        args.append(self._k0s)
        args.append("reset")

        args.append("--data-dir")
        args.append(self.data_dir)

        if self.config is not None and os.path.isfile(self.config):
            args.append("--config")
            args.append(self.config)

        if len(self.arguments) > 0:
            for arg in self.arguments:
                args.append(arg)

        self.module.log(msg=f" - args {args}")

        rc, out, err = self._exec(args)

        if rc == 0:
            _failed = False
            _changed = True

            self._remove_directory(self.data_dir)

            if self.config is not None and os.path.isfile(self.config):
                os.remove(self.config)

            if os.path.isfile(self._controller_systemd_unit_file):
                os.remove(self._controller_systemd_unit_file)
            if os.path.isfile(self._worker_systemd_unit_file):
                os.remove(self._worker_systemd_unit_file)

            _msg = "k0s was successful removed. To ensure a full reset, a node reboot is recommended."

            return dict(
                rc=rc,
                cmd=" ".join(args),
                msh=_msg,
                failed=_failed,
                changed=_changed
            )

        else:
            return dict(
                rc=rc,
                cmd=" ".join(args),
                msg=err,
                failed=True
            )

        return dict(
            failed=_failed,
            changed=_changed,
            cmd=_cmd,
            msg=_msg
        )

    def _remove_directory(self, directory):
        ''' .... '''
        self.module.log(msg=f"remove directory {directory}")

        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def _exec(self, args, check=False):
        """
        """
        rc, out, err = self.module.run_command(args, check_rc=check)
        self.module.log(msg=f"  rc : '{rc}'")
        self.module.log(msg=f"  out: '{out}'")
        self.module.log(msg=f"  err: '{err}'")
        return rc, out, err


# ===========================================
# Module execution.
#


def main():

    module = AnsibleModule(
        argument_spec=dict(
            config=dict(
                required=False,
                type='str'
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

    k = K0sReset(module)
    result = k.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
