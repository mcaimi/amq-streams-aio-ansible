# AMQ Streams Deployment Playbook

This is a simple playbook I wrote to deploy an AMQ Streams instance on a RedHat Enterprise Linux virtual machine for development purposes.
Multiple environments can be deployed by using variable files.

Requirements:

* Valid RedHat subscription credentials for both
  * RedHat AMQ Streams
  * RedHat Enterprise Linux
* VMWare or KVM-based virtualization environment

The playbook currently manages to:

* Create OS-level Users
* Deploys one (or more) Zookeeper Instances
* Deploys one (or more) AMQ Streams Broker Instances

**This playbook is intended to install and manage only RedHat supported software coming from RedHat repositories. It should be fairly trivial however to adapt the playbook to install the upstream Kafka distribution on CentOS**

## Broker Version and Download link

Tarball link and software versions can be changed/updated inside `vars/common`:

```yaml
common:
  amq_artifact_download_url: https://access.redhat.com/jbossnetwork/restricted/softwareDownload.html?softwareId=101031&product=jboss.amq.streams
  remote_src: "yes"
  amq_version: "1.8.0"
```

## Setup Customer Portal Credentials

Username/password pairs used to access the Customer Portal can be set up inside the `vars/credentials/customerportal` file:

```yaml
customerportal:
  username: your_csp_username
  password: your_csp_password
```

## Create an installation Environment

An example environment is provided under `vars/environments/`. Either customize that or make a new one.

## Broker installation

Include the desired environment in the playbook (or create a dedicated playbook for the environment):

```yaml
  pre_tasks:
    - include_vars:
        file: "common"
    - include_vars:
        file: "environments/dev"
    - include_vars:
        file: "credentials/customerportal"
```

Run the playbook:

```bash
$ ansible-playbook -i hosts kafka-aio.yaml
```

# TODO

- [ ] Better detail installation steps
- [ ] Document playbook switches
- [ ] Refine playbook veriables
