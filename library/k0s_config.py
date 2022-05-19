#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os

from ansible.module_utils.basic import AnsibleModule


class K0sConfig(object):
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
        self.arguments = module.params.get("arguments")

        module.log(msg="----------------------------")
        module.log(msg=" k0s          : {} ({})".format(self._k0s, type(self._k0s)))
        module.log(msg=" state        : {} ({})".format(self.state, type(self.state)))
        module.log(msg=" force        : {} ({})".format(self.force, type(self.force)))
        module.log(msg=" config       : {} ({})".format(self.config, type(self.config)))
        module.log(msg=" arguments    : {} ({})".format(self.arguments, type(self.arguments)))
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

        result = self.k0s_config()

        return result

    def k0s_config(self):
        """
            k0s config --help
            Configuration related sub-commands

            Usage:
              k0s config [command]

            Available Commands:
              create      Output the default k0s configuration yaml to stdout
              edit        Launch the editor configured in your shell to edit k0s configuration
              status      Display dynamic configuration reconciliation status
              validate    Validate k0s configuration
        """
        _failed = True
        _changed = False
        _cmd = None
        _msg = "initial call"

        if self.force:
            self.module.log(msg="force mode ...")
            os.remove(self.config)

        if os.path.isfile(self.config):
            return dict(
                msg=f"config file {self.config} already exists",
                changed=False,
                failed=False
            )

        args = []
        args.append(self._k0s)
        args.append("config")
        args.append(self.state)

        if len(self.arguments) > 0:
            for arg in self.arguments:
                args.append(arg)

        self.module.log(msg=f" - args {args}")

        rc, out, err = self._exec(args)

        if rc == 0:
            _failed = False
            _changed = True

            self._save_config(out)

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
        """
        """
        self.module.log(msg="remove directory {}".format(directory))

        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def _save_config(self, data):
        """
        """
        data_file = open(self.config, 'w')
        data_file.write(json.dumps(data, indent=2))
        data_file.close()

        force_mode = "0600"
        if isinstance(force_mode, str):
            mode = int(force_mode, base=8)

        os.chmod(self.config, mode)


    def _exec(self, args):
        """
        """
        rc, out, err = self.module.run_command(args, check_rc=True)
        self.module.log(msg="  rc : '{}'".format(rc))
        self.module.log(msg="  out: '{}' ({})".format(out, type(out)))
        self.module.log(msg="  err: '{}'".format(err))
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
                default="create",
                choices=["create", "edit", "status", "validate"]
            ),
            config=dict(
                required=True,
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

    k = K0sConfig(module)
    result = k.run()

    module.log(msg="= result: {}".format(result))

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
