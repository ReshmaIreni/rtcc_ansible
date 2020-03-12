#!/usr/bin/python

from ansible.module_utils.basic import *
import os
import re
import fileinput
from zipfile import ZipFile

DOCUMENTATION = r'''
---
module: install_ai_patch
short_description: Install patch using AutoInstaller tool
description:
    - Unpack patch into NETCRACKER_HOME directory.
    - Modify configuration file(s).
    - Start AutoInstaller tool by executing install.sh script.
options:
    netcracker_home:
        required: true
        description:
            - Absolute path to NETCRACKER_HOME directory. 
            - AutoInstaller should be installed in this path.
    patch:
        required: true
        description:
            - Absolute path to AutoInstaller zip package.
    args:
        description:
            - Arguments that should be passed to install.sh script.
    config_files:
        description:
            - One or more file names for properties files.
            - If patch contains etalon property file (e.g. etalon_config_TEST.properties), it will be
              renamed.
            - After rename parameters will be updated with values from C(properties) option.
        type: list
    properties:
        description:
            - Key-value pairs (dictionary) with properties. 
            - If any property matches to one from config file it will be updated.
            - Passwords are not updated by default.
            - To change passwords need use C(recreate_config) option.
        type: dict
    recreate_config:
        description:
            - Recreate config file from scratch (rename etalon file and fill it with properties).
        default: 'no'
        type: bool

'''

EXAMPLES = r'''
- name: Install patch with minimum configuration
  install_ai_patch:
    netcracker_home: /srv/netcracker_home
    patch: /srv/kits/TEST_autoinstaller.zip

- name: Install patch with extra arguments for AutoInstaller
  install_ai_patch:
    netcracker_home: /srv/netcracker_home
    patch: /srv/kits/TEST_autoinstaller.zip
    args: "-skip_sqltest"
    
- name: Prepare parameters and install patch
  install_ai_patch:
    netcracker_home: /srv/netcracker_home
    patch: /srv/kits/TEST_autoinstaller.zip
    config_files: ['config_TEST.properties']
    properties:
        foo: bar
        
- name: Recreate properties file and install patch
  install_ai_patch:
    netcracker_home: /srv/netcracker_home
    patch: /srv/kits/TEST_autoinstaller.zip
    recreate_configs: true
    config_files: ['config_TEST.properties']
    properties:
        foo: bar
        foo.password: baz

'''

RETURN = r'''
    stdout:
        description: The shell standard output (AutoInstaller console log).
        returned: always
        type: string
    stderr:
        description: The shell standard error
        returned: always
        type: string
    rc:
        description: The command return code (0 means success).
        returned: always
        type: int
        sample: 0
    updated_configs:
        description: All properties in config files that were modified.
        returned: always
        type: dict
        sample:
            config_TEST.properties:
                key: "foo"
                new_value: "bar"
                old_value: "baz"
'''


def update_configs(netcracker_home, config_files, properties, recreate_configs):
    params_diff = dict()
    if config_files:
        params_before = dict()
        params_after = dict()
        for config_file in config_files:
            params_before[config_file] = {}
            params_after[config_file] = {}
            params_diff[config_file] = []
            config_file_path = netcracker_home + "/AutoInstaller/" + config_file
            config_file_exists = os.path.isfile(config_file_path)
            if config_file_exists:
                params_before[config_file] = read_property_file(config_file_path)
            etalon_config_file = netcracker_home + "/AutoInstaller/etalon_" + config_file
            if os.path.isfile(etalon_config_file) and (not config_file_exists or recreate_configs):
                os.rename(etalon_config_file, config_file_path)
            if os.path.isfile(config_file_path):
                for k, v in properties.items():
                    k_esc = re.escape(k)
                    if (not config_file_exists or recreate_configs) or not re.search('password', k, re.IGNORECASE):
                        for line in fileinput.input(config_file_path, inplace=1):
                            line = re.sub('^\s*?#?\s*?%s[ \t]*=.*$' % k_esc, "%s = %s" % (k, v), line.rstrip(), flags=re.M)
                            print(line)
                params_after[config_file] = read_property_file(config_file_path)
            diffkeys = [k for k in params_after[config_file]
                        if params_after[config_file][k] != params_before[config_file].get(k, "")]

            for k in diffkeys:
                params_diff[config_file].append({
                    "key": k,
                    "old_value": params_before[config_file].get(k, ""),
                    "new_value": params_after[config_file][k]
                })
    return params_diff


def read_property_file(filename):
    prop_file = open(filename, "r+")
    prop_dict = dict()
    for prop_line in prop_file:
        prop_def = prop_line.strip()
        if len(prop_def) == 0:
            continue
        if prop_def[0] in ('!', '#'):
            continue
        punctuation = [prop_def.find(c) for c in ':= '] + [len(prop_def)]
        found = min([pos for pos in punctuation if pos != -1])
        name = prop_def[:found].rstrip()
        value = prop_def[found:].lstrip(":= ").rstrip()
        if not re.search('password', name, re.IGNORECASE):
            prop_dict[name] = value
    prop_file.close()
    return prop_dict


def main():
    module = AnsibleModule(
        argument_spec=dict(
            netcracker_home=dict(required=True, type='str'),
            patch=dict(required=True, type='str'),
            args=dict(default='', type='str'),
            config_files=dict(default=[], type='list'),
            properties=dict(default={}, type='dict'),
            recreate_configs=dict(type='bool', default=False)
        )
    )

    netcracker_home = module.params['netcracker_home']
    patch = module.params['patch']
    args = module.params['args']
    config_files = module.params['config_files']
    properties = module.params['properties']
    recreate_configs = module.params['recreate_configs']

    if not os.path.exists(netcracker_home):
        module.fail_json(msg="Path %s not found" % netcracker_home)
    if not os.access(netcracker_home, os.W_OK):
        module.fail_json(msg="Directory %s not writable" % netcracker_home)

    if not os.path.isfile(patch):
        module.fail_json(msg="File %s not found" % patch)
    if not os.access(netcracker_home, os.R_OK):
        module.fail_json(msg="File %s not readable" % netcracker_home)

    if (not os.path.isfile(netcracker_home + "/AutoInstaller/build.xml")) and (
            not os.path.isfile(netcracker_home + "/AutoInstaller/install.sh")):
        module.fail_json(msg="AutoInstaller not found in %s" % netcracker_home)

    if not config_files and any(properties):
        module.fail_json(msg="Both config_files and properties parameters should be defined")

    ai_patch = ZipFile(patch, 'r')
    ai_patch.extractall(netcracker_home)
    ai_patch.close()

    updated_configs = update_configs(netcracker_home, config_files, properties, recreate_configs)

    chdir = os.path.abspath(netcracker_home)
    os.chdir(chdir)
    os.chmod("install.sh", 0o775)

    args = "./install.sh " + args
    rc, out, err = module.run_command(args)

    result = dict(
        stdout=out.rstrip(b"\r\n"),
        stderr=err.rstrip(b"\r\n"),
        rc=rc,
        changed=True,
        updated_configs=updated_configs
    )

    if rc != 0:
        module.fail_json(msg='non-zero return code', **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
