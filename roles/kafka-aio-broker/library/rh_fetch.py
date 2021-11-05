##!/usr/bin/env python
# -*- coding: utf-8 -*-
#

DOCUMENTATION = r'''
module: rh_fetch
version: 0.1
options:
    username:
        description:
            - The Customer Portal Username to use during login
        required: True
    password:
        description:
            - The Customer Portal Password to use during login
        required: True
    artifact_url:
        description:
            - The URL from which to download the software
        required: True
    target:
        description:
            - Target absolute path where to store the downloaded artifact
        required: True
requirements:
    - requests
    - BeautifulSoup4
description:
    - Download artifacts from the RedHat Customer Portal with credentials
'''

EXAMPLES = r'''
- name: Download AMQ Broker Package
  rh_fetch:
      username: test@redhat.com
      pass: redhat123
      artifact_url: "https://access.redhat.com/jbossnetwork/restricted/softwareDownload.html?softwareId=84211"
      target: "/tmp/amq-broker.zip"
'''

from requests import Session
from bs4 import BeautifulSoup
import os,errno
from ansible.module_utils.basic import AnsibleModule


# Login to the Customer Portal and Download the requested artifact
def log_in_and_download(module, username, password, url, target):
    # authentication header
    auth_payload = {
            'username': username,
            'password': password
            }

    # prepare a Session request
    rh_csp_session_handler = Session()
    rh_csp_session = rh_csp_session_handler.get(url)

    # parse html response body
    try:
        html_response = BeautifulSoup(rh_csp_session.text, 'html.parser')
        sso_post_tags = html_response.find_all('form')

        # find sso url
        sso_post_url = list(filter(lambda x: x is not None, [ x.get('action') for x in sso_post_tags ])).pop(0)

        # perform authentication via HTTP POST
        rh_csp_session = rh_csp_session_handler.post(sso_post_url, data=auth_payload)
    except Exception:
        module.fail_json(msg="No SSO URL found in page")

    # check response code and download data
    if (rh_csp_session.status_code == 200) and ('html' not in rh_csp_session.headers.get('Content-Type')):
        # download is starting
        with open(target, 'wb') as payload:
            payload.write(rh_csp_session.content)
    else:
        module.fail_json(msg="Failed to retrieve artifact from RedHat CustomerPortal")

    # close session
    rh_csp_session.close()

# module handler function
def rh_fetch_module():
    # module options
    module_args = dict(
            username = dict(type='str', required=True),
            password = dict(type='str', required=True, no_log=True),
            target = dict(type='str', required=True),
            artifact_url = dict(type='str', required=True)
        )

    # declare module
    rh_fetch_module = AnsibleModule(argument_spec=module_args)

    # populate options from task
    username = rh_fetch_module.params.get('username')
    password = rh_fetch_module.params.get('password')
    artifact_url = rh_fetch_module.params.get('artifact_url')
    target = rh_fetch_module.params.get('target')

    # results dict
    res_args = dict(
        changed = False,
        artifact_url = artifact_url,
        target = target,
        message = "OK"
    )

    # target path sanity check
    if os.path.exists(target):
        # allow file attribute changes
        rh_fetch_module.params['path'] = target
        file_args = rh_fetch_module.load_file_common_arguments(rh_fetch_module.params)
        file_args['path'] = target
        changed = rh_fetch_module.set_fs_attributes_if_different(file_args, False)

        if changed:
            rh_fetch_module.exit_json(message="file already exists but file attributes changed", target=target, artifact_url=artifact_url, changed=changed)
        rh_fetch_module.exit_json(message="file already exists", target=target, artifact_url=artifact_url, changed=changed)
    else:
        # create directory structure
        fullpath = os.path.dirname(target)
        try:
            os.makedirs(fullpath)
        except OSError as makedir_exception:
            if makedir_exception.errno == errno.EEXIST and os.path.isdir(fullpath):
                pass
            else:
                raise rh_fetch_module.fail_json(msg=str(makedir_exception))

    # connect to the CustomerPortal and try to download package
    try:
        log_in_and_download(rh_fetch_module, username, password, artifact_url, target)
        # Set changed state switch to True
        res_args['changed'] = True
    except Exception as ex:
        rh_fetch_module.fail_json(msg=str(ex))

    # terminale module run
    rh_fetch_module.exit_json(**res_args)

# MAIN
if __name__=="__main__" :
    rh_fetch_module()
