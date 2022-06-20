#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# (c) 2022, Bodo Schulz <bodo@boone-schulz.de>
# BSD 2-clause (see LICENSE or https://opensource.org/licenses/BSD-2-Clause)

from __future__ import absolute_import, division, print_function
# from ruamel.yaml import YAML

from ansible.module_utils.basic import AnsibleModule


class KubeCtl(object):
    """
      Main Class
    """
    module = None

    def __init__(self, module):
        """
          Initialize all needed Variables
        """
        self.module = module

        self._kubectl = module.get_bin_path('kubectl', True)

        self.state = module.params.get("state")
        self.resource = module.params.get("resource")
        self.namespace = module.params.get("namespace")
        self.kubeconfig = module.params.get("kubeconfig")
        self.filename = module.params.get("filename")
        self.validate = module.params.get("validate")
        self.arguments = module.params.get("arguments")

        module.log(msg="----------------------------")
        module.log(msg=" kubectl      : {} ({})".format(self._kubectl, type(self._kubectl)))
        module.log(msg=" state        : '{}' ({})".format(self.state, type(self.state)))
        module.log(msg=" resource     : {} ({})".format(self.resource, type(self.resource)))
        module.log(msg=" namespace    : {} ({})".format(self.namespace, type(self.namespace)))
        module.log(msg=" kubeconfig   : {} ({})".format(self.kubeconfig, type(self.kubeconfig)))
        module.log(msg=" filename     : {} ({})".format(self.filename, type(self.filename)))
        module.log(msg=" validate     : {} ({})".format(self.validate, type(self.validate)))
        module.log(msg=" arguments    : {} ({})".format(self.arguments, type(self.arguments)))
        module.log(msg="----------------------------")

    def run(self):
        """
          runner
        """
        self.module.log(msg="  KubeCtl::run()")

        result = dict(
            rc=1,
            failed=True,
            changed=False,
        )

        if self.state == "get":
            result = self._get()
        if self.state == "apply":
            result = self._apply()
        else:
            pass

        return result

    def _get(self):
        """
        """
        self.module.log(msg="  KubeCtl::_get()")

        _failed = True
        _changed = False
        _cmd = None
        _msg = "initial call"

        if not self.resource:
            return dict(
                rc=2,
                failed=True,
                changed=False,
                msg="missing resource parameter for get state."
            )

        args = []
        args.append(self._kubectl)
        args.append("get")

        args.append(self.resource)

        if len(self.kubeconfig) > 0:
            args.append(f"--kubeconfig={self.kubeconfig.strip()}")

        if len(self.namespace) > 0:
            args.append(f"--namespace={self.namespace.strip()}")

        args.append("--output=custom-columns=NAME:.metadata.name,STATUS:.status.phase")

        if len(self.arguments) > 0:
            for arg in self.arguments:
                args.append(arg)

        self.module.log(msg=f" - args {args}")

        rc, out, err = self._exec(args)

        # if len(out) > 0:
        #     yaml = YAML()
        #     code = yaml.load(out)
        #
        #     self.module.log(msg=f"{code}")

        return dict(
            failed=_failed,
            changed=_changed,
            cmd=_cmd,
            msg=_msg
        )

    def _apply(self):
        """
        """
        self.module.log(msg="  KubeCtl::_apply()")

        _failed = True
        _changed = False
        _cmd = None
        _msg = "initial call"

        if not self.filename:
            return dict(
                rc=2,
                failed=True,
                changed=False,
                msg="missing filename parameter for apply state."
            )

        args = []
        args.append(self._kubectl)
        args.append("apply")

        if len(self.kubeconfig) > 0:
            args.append(f"--kubeconfig={self.kubeconfig.strip()}")

        args.append(f"--filename={self.filename}")
        args.append("--output=yaml")

        if len(self.arguments) > 0:
            for arg in self.arguments:
                args.append(arg)

        self.module.log(msg=f" - args {args}")

        rc, out, err = self._exec(args)

        # if len(out) > 0:
        #     yaml = YAML()
        #     code = yaml.load(out)
        #
        #     self.module.log(msg=f"{code}")

        # self.module.log(msg=f"{out.splitlines()}")

        # for line in out.splitlines():
        #    self.module.log(msg=f"{line}")

        if rc == 0:
            _failed = False
            _changed = True

            if self.state == "apply":
                return dict(
                    rc=rc,
                    cmd=" ".join(args),
                    msg=f"file {self.filename} successful applied.",
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
        rc, out, err = self.module.run_command(args, check_rc=False)
        self.module.log(msg=f"  rc : '{rc}'")
        self.module.log(msg=f"  out: '{out}' ({type(out)})")
        self.module.log(msg=f"  err: '{err}'")
        return rc, out, err

# ===========================================
# Module execution.
#


def main():
    """
    """
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(
                default="apply",
                choices=["apply", "get"]
            ),
            resource=dict(
                required=False,
                type=str
            ),
            namespace=dict(
                required=False,
                type=str
            ),
            kubeconfig=dict(
                required=False,
                type=str
            ),
            filename=dict(
                required=False,
                type=str
            ),
            validate=dict(
                required=False,
                default=False,
                type='bool'
            ),
            arguments=dict(
                required=False,
                default=[],
                type=list
            )
        ),
        supports_check_mode=True,
    )

    k = KubeCtl(module)
    result = k.run()

    module.log(msg="= result: {}".format(result))

    module.exit_json(**result)


# import module snippets
if __name__ == '__main__':
    main()
