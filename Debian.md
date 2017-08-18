This file covers the case when you want to install jenkins-package-builder in
a Debian machine running Jenkins to build RPM packages.

## Installing

You can find the Debian packaging in debian/. Running: `dpkg-buildpackage`
from the root directory will build a Debian packaging for Jessie.
Remember to install the build dependencies before building the package,
they're listed in `debian/control` .

## About jenkins-package-builder

jenkins-package-builder provides 3 binaries:

* `jpb_generate_source_package`

Creates a source RPM package `*.src.rpm`

* `jpb_generate_binary_package`

Builds a RPM source package and creates one or serveral rpm.

* `jpb_provide_package`

Adds the RPM package in a RPM repository.


## Support files and packages

To create RPM chroots you'll need mock that's already include in dependency
list of jenkins-package-builder. If you want your `jenkins` user to be able
to use mock, you'll need to add it to the `mock` group:

    addgroup mock
	addgroup jenkins mock

Besides, you'll need to add under /etc/mock the files for the distributions
you use, if needed, and copy somewhere in your system the GPG public keys
for the external and internal RPM repositories.


## Using jenkins-job-builder
If you use jenkins-job-builder for handling the jenkins jobs, here you have
a quick example:


- project:
    name: software
    repos: http://mywebgitserver/cgit/software.git
    repos_branch: next
    target_distribution_rpm: rhel-6.5
    final_repository_rpm: rhel6.5-custom
    architecture: x86_64
    jobs:
      - '{name}-sourcerpm'
      - '{name}-binariesrpm'


- job-template:
      name: '{name}-sourcerpm'
      project-type: freestyle
      description: 'Build RPM source package of {name}.<br />Do not edit
this job through the web, it is generated via jenkins-package-builder!'
      disabled: false
      scm:
        - git:
            url: '{repos}'
            name: origin
            refspec: +refs/heads/*:refs/remotes/origin/*
            basedir: source
            branches:
              - '{repos_branch}'
            wipe-workspace: false
      logrotate:
        numToKeep: 3
      builders:
        - shell: 'rm -f ./* || true'
        - shell: |
            # when using git:
            /usr/bin/jpb_generate_source_package
      publishers:
        - archive:
            artifacts: '*.src.rpm,*.gz'
        - trigger:
            project: '{name}-binariesrpm'
            threshold: UNSTABLE
        - fingerprint:
            record-artifacts: true
      wrappers:
        - timestamps

- job-template:
      name: '{name}-binariesrpm'
      project-type: matrix
      description: |
          <p>Build RPM binary packages of {name}.<br />Do not edit this job through the web, it is generated via jenkins-job-builder!</p>
          <p>Access to this repository is available at: </p>
          <pre>

            https://myserver/repos/jenkins/{final_repository_rpm}
            or
            myserver:/srv/repos/jenkins/{final_repository_rpm}
          </pre>
      execution-strategy:
        sequential: true
      logrotate:
        numToKeep: 3
      builders:
        - copyartifact:
            project: '{name}-sourcerpm'
            filter: '*'
            which-build: upstream-build
            fallback-to-last-successful: true
        - shell: |
            export distribution={target_distribution_rpm}
            export architecture={architecture}
            /usr/bin/jpb_generate_binary_package
            echo "Adding packages to {final_repository_rpm}:"
            export REPONAME={final_repository_rpm}
            export REPOSITORY=/srv/repos/jenkins/
            /usr/bin/jpb_provide_package
      publishers:
        - archive:
            artifacts: '*.rpm,*.txt'
        - fingerprint:
            record-artifacts: true
        - workspace-cleanup:
            dirmatch: false
      wrappers:
        - timestamps

-- Ana Guerrero <ana-externe.guerrero@edf.fr>  Fri, 17 Aug 2017 09:54:48 +0200

