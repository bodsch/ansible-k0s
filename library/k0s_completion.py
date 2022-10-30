#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
import os
import json

from ansible.module_utils.basic import AnsibleModule


class K0sCompletion(object):
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

        self.shell = module.params.get("shell")
        self.arguments = module.params.get("arguments")

        module.log(msg="----------------------------")
        module.log(msg=f" k0s          : {self._k0s}")
        module.log(msg=f" shell        : {self.shell}")
        module.log(msg=f" arguments    : {self.arguments}")
        module.log(msg="----------------------------")

        self.bash_completion_file = "/etc/bash_completion.d/k0s"

    def run(self):
        """
          runner
        """
        result = dict(
            rc=1,
            failed=True,
            changed=False,
        )

        result = self.k0s_completion()

        return result

    def k0s_completion(self):
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


        if self.shell == "bash" and os.path.isfile(self.bash_completion_file):
            return dict(
                failed = False,
                changed = False,
                msg = "bash completion already created."
            )

        args = []
        args.append(self._k0s)
        args.append("completion")
        args.append(self.shell)

        # if self.shell == "bash":
        #     args.append(">")
        #     args.append("/etc/bash_completion.d/k0s")
        # elif self.shell == "zsh":
        #     args.append(">")
        #     args.append("${fpath[1]}/_k0s")
        # elif self.shell == "fish":
        #     args.append("|")
        #     args.append("source")

        self.module.log(msg=f" - args {args}")

        rc, out, err = self._exec(args)

        if rc == 0:
            _failed = False
            _changed = False
            _msg = out

            if self.shell == "bash":
                with open(self.bash_completion_file, 'w') as file:
                    file.writelines(out)
                    file.close()

                    return dict(
                        failed = False,
                        changed = False,
                        msg = "bash completion successfully written."
                    )
            elif self.shell == "zsh":
                # TODO
                pass
            elif self.shell == "fish":
                # TODO
                pass

            return dict(
                rc=rc,
                cmd=" ".join(args),
                msg=_msg,
                state="installed",
                failed=_failed,
                changed=_changed
            )

        else:
            return dict(
                cmd=" ".join(args),
                msg=err,
                state="missing",
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
            shell=dict(
                default="bash",
                choices=["bash", "zsh", "fish"]
            ),
            arguments=dict(
                required=False,
                default=[],
                type=list
            )
        ),
        supports_check_mode=True,
    )

    k = K0sCompletion(module)
    result = k.run()

    module.log(msg=f"= result: {result}")

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
