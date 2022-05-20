# python 3 headers, required if submitting to Ansible

from __future__ import (absolute_import, print_function)
__metaclass__ = type

from ansible.utils.display import Display

display = Display()


class FilterModule(object):
    """
        Ansible file jinja2 tests
    """

    def filters(self):
        return {
            'group_members': self.group_members,
            'remove_group_members': self.remove_group_members,
        }

    def group_members(self, data, lookup):
        """
          filter group member entries from dict

          input:
            data: { 'initial_controller': ['k0s-1'] }
            lookup: 'initial_controller'
          output: ['k0s-1']

          input:
            data: { 'worker': ['k0s-3', 'k0s-4'] }
            lookup: 'worker'
          output: ['k0s-3', 'k0s-4']
        """
        display.v(f"group_members({data}, {lookup}")

        result = []

        if isinstance(data, dict):
            if data.get(lookup):
                result = data.get(lookup)

        result.sort()

        display.v(f"= {result}")

        return result

    def remove_group_members(self, data, not_in_group):
        """
          filter entries from HostVars

          removes entries that occur in not_in_group

          input:
            data: HostVars
            not_in_group: ['initial_controller']

          output: ['k0s-2', 'k0s-3', 'k0s-4']
        """
        result = []
        for host_name, host_data in data.items():
            _name = host_data.get('host_name', '')
            if _name:
                host_name = _name

            if host_name not in not_in_group:
                result.append(host_name)

        result.sort()

        display.v("= {}".format(result))

        return result
