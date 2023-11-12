#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os
# import json
import yaml

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
        self.config_file = module.params.get("config_file")
        self.config_overwrites = module.params.get("config_overwrites")
        self.data_dir = module.params.get("data_dir")
        self.arguments = module.params.get("arguments")

        module.log(msg="----------------------------")
        module.log(msg=f" k0s               : {self._k0s}")
        module.log(msg=f" state             : {self.state}")
        module.log(msg=f" force             : {self.force}")
        module.log(msg=f" config file       : {self.config_file}")
        module.log(msg=f" config overwrites : {self.config_overwrites}")
        module.log(msg=f" data_dir          : {self.data_dir}")
        module.log(msg=f" arguments         : {self.arguments}")
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
        file_size = 0

        if self.force and os.path.isfile(self.config_file):
            self.module.log(msg="force mode ...")
            os.remove(self.config_file)

        if self.state == "create" and os.path.isfile(self.config_file):
            file_size = int(os.path.getsize(self.config_file))
            if self._config_same() and file_size > 0:
                return dict(
                    msg=f"The configuration file {self.config_file} already exists or hasn't changed.",
                    changed=False,
                    failed=False
                )

        result = self._create_config()

        return result

    def _config_same(self):
        """
        """
        data = None
        if os.path.isfile(self.config_file):
            with open(self.config_file, "r") as stream:
                try:
                    data = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    self.module.log(msg=f"  ERROR : '{exc}'")

        return self._rec_merge(data, self.config_overwrites) == data

    def _create_config(self):
        """
        """
        args = []
        args.append(self._k0s)
        args.append("config")
        args.append(self.state)
        args.append("--data-dir")
        args.append(self.data_dir)

        if self.state == "validate":
            args.append("--config")
            args.append(self.config_file)

        if len(self.arguments) > 0:
            for arg in self.arguments:
                args.append(arg)

        self.module.log(msg=f" - args {args}")

        rc, out, err = self._exec(args)

        if rc == 0:
            _failed = False
            _changed = True

            if self.state == "create":

                self._save_config(out)

                if self.config_overwrites and len(self.config_overwrites) > 0:
                    self._apply_overwrites()

                return dict(
                    rc=rc,
                    cmd=" ".join(args),
                    msg=f"The configuration file {self.config_file} was successfully created.",
                    failed=_failed,
                    changed=_changed
                )
            elif self.state == "validate":
                _changed = False
                return dict(
                    rc=rc,
                    cmd=" ".join(args),
                    msg=f"The configuration file {self.config_file} is valid.",
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

    def _remove_directory(self, directory):
        """
        """
        self.module.log(msg=f"remove directory {directory}")

        for root, dirs, files in os.walk(directory, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

    def _save_config(self, data):
        """
        """
        data_file = open(self.config_file, 'w')
        data_file.write(data)
        data_file.close()

        force_mode = "0660"
        if isinstance(force_mode, str):
            mode = int(force_mode, base=8)

        os.chmod(self.config_file, mode)

    def _apply_overwrites(self):
        """
        """
        data = None
        if os.path.isfile(self.config_file):
            with open(self.config_file, "r") as stream:
                try:
                    data = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    self.module.log(msg=f"  ERROR : '{exc}'")

            if data:
                data = self._rec_merge(data, self.config_overwrites)

                with open(self.config_file, 'w') as file:
                    _ = yaml.dump(data, file)

    def _rec_merge(self, d1, d2):
        '''
        Update two dicts of dicts recursively,
        if either mapping has leaves that are non-dicts,
        the second's leaf overwrites the first's.
        '''
        from collections.abc import MutableMapping

        for k, v in d1.items():
            if k in d2:
                # this next check is the only difference!
                if all(isinstance(e, MutableMapping) for e in (v, d2[k])):
                    d2[k] = self._rec_merge(v, d2[k])
                # we could further check types and merge as appropriate here.
        d3 = d1.copy()
        d3.update(d2)
        return d3

    def _exec(self, args):
        """
        """
        rc, out, err = self.module.run_command(args, check_rc=True)
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
                default="create",
                choices=["create", "edit", "status", "validate"]
            ),
            config_file=dict(
                required=True,
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
            ),
            config_overwrites=dict(
                required=False,
                default={},
                type=dict
            ),
        ),
        supports_check_mode=True,
    )

    k = K0sConfig(module)
    result = k.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
