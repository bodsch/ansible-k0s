#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os

from ansible.module_utils.basic import AnsibleModule


class K0sToken(object):
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
        self.role = module.params.get("role")
        self.expiry = module.params.get("expiry")
        self.config = module.params.get("config")
        self.data_dir = module.params.get("data_dir")
        self.arguments = module.params.get("arguments")

        module.log(msg="----------------------------")
        module.log(msg=f" k0s          : {self._k0s}")
        module.log(msg=f" state        : {self.state}")
        module.log(msg=f" role         : {self.role}")
        module.log(msg=f" expiry       : {self.expiry}")
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

        result = self.k0s_token()

        return result

    def k0s_token(self):
        """
            k0s token --help
            Manage join tokens

            Usage:
              k0s token [command]

            Available Commands:
              create      Create join token
              invalidate  Invalidates existing join token
              list        List join tokens
        """
        _failed = True
        _changed = False
        _cmd = None
        _msg = "initial call"

        args = []
        args.append(self._k0s)
        args.append("token")
        args.append(self.state)
        args.append("--role")
        args.append(self.role)
        args.append("--data-dir")
        args.append(self.data_dir)

        if len(self.expiry) > 0:
            args.append("--expiry")
            args.append(self.expiry)

        if self.state == "create":
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

            if self.state == "create":
                return dict(
                    rc=rc,
                    cmd=" ".join(args),
                    token=out,
                    failed=_failed,
                    changed=_changed
                )
            elif self.state == "list":
                _changed = False
                return dict(
                    rc=rc,
                    cmd=" ".join(args),
                    msg=out.trim(),
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

    def _exec(self, args):
        """
        """
        rc, out, err = self.module.run_command(args, check_rc=True)
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
            state=dict(
                default="create",
                choices=["create", "invalidate", "list"]
            ),
            role=dict(
                required=False,
                default="worker",
                choices=["controller", "worker", ""]
            ),
            expiry=dict(
                required=False,
                type=str
            ),
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

    k = K0sToken(module)
    result = k.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
