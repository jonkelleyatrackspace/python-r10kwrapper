r10kwrapper
===================
The wrapper to make using the r10k command easier and even bring some automation into your life.

**Authors:** Jon Kelley <jon.kelley@rackspace.com>

Synopsis
-------------
The problem this wrapper seeks to solve is the unweildy methods to passing Puppetfiles and module destinations to r10k. The native way r10k works is to export those options as shell vars, then run r10k. This wraps that functionality.

This wrapper takes explicit arguements to define *PUPPETFILE* path and *MODULE PATH* or it can load this information automatically out of a config file (`/etc/r10k/wrapper.conf`), and perform operations on 1 or more *PUPPETFILE* or *MODULE PATHS*.


Usage
-------------

```
usage: r10kwrapper [-h] [-p PUPPETFILE] [-d DEST] [-c CONFIGSECTION]
                   [-C CONFIGFILE] -x ACTION [-v VERBOSITY] [-f FLAGS_APPEND]

Wrapper for r10k to ease management of the Rackspace Puppet r10k structure.

optional arguments:
  -h, --help            show this help message and exit
  -p PUPPETFILE, --puppetfile PUPPETFILE
                        Path to Puppetfile holding module dependecies.
  -d DEST, --dest DEST  Path to deploy Puppetfile modules to.
  -c CONFIGSECTION, --configsection CONFIGSECTION
                        Loads r10k settings from a ini section. This arguement
                        can be supplied multiple times. If ALL is supplied,
                        all sections will be executed. (ex -i modules -i
                        profiles -i signup -i cloudfeeds)
  -C CONFIGFILE, --configfile CONFIGFILE
                        Defines the ini file to load. Otherwise it assumes
                        /etc/r10k/wrapper.conf
  -x ACTION, --action ACTION
                        Action to perform with Puppetfile
                        (check,install,purge) supported.
  -v VERBOSITY, --verbosity VERBOSITY
                        Log level (0 = error, 1 = warn, 2 = info, 3 = debug)
                        (Default: 3)
  -f FLAGS_APPEND, --flags_append FLAGS_APPEND
                        Pass trailing arguements to r10k command, (ex. -v
                        debug)
```


## Real world copy-pasta friendly examples.
Below are some real-world examples on using this tool.

All of these examples pretty much derive a `Puppetfile` with the wrapper script resolving for the tier and environment inherant to the command, `r10k`does its magic with Puppetfile and dumps the repositories under `/etc/puppet/something`.
###1) Install or Update "shared modules" with explicit path definitions.
This would explicitly update /etc/puppet/modules based on your provided puppetfile.

**bash$**
`r10kwrapper -x install -p /etc/r10k/modules.Puppetfile -m /etc/puppet/modules`

**Resulting Actions**
```
PUPPETFILE LOADED = /etc/r10k/modules.Puppetfile
MODULE PATH CREATED = /etc/puppet/modules/<CLONED MODULES>

```

###2) Install or Update *ALL* modules based on config

**bash$**
`r10kwrapper -x install -c ALL`

**Resulting Actions**
```
1) PUPPETFILE LOADED = /etc/r10k/modules.Puppetfile
1) MODULE PATH CREATED = /etc/puppet/modules/<CLONED MODULES>
2) PUPPETFILE LOADED = /etc/r10k/profiles.Puppetfile
2) MODULE PATH CREATED = /etc/puppet/environments/<CLONED MODULES>
3) PUPPETFILE LOADED = /etc/r10k/environments/Signup.puppetfile
3) MODULE PATH CREATED = /etc/puppet/environments/signup_svc/<CLONED MODULES>
```

 **Assumptions**:
 `/etc/r10k/wrapper.ini` resembles:

```
#FILE: /etc/r10k/wrapper/ini

[modules]
puppetfile=/etc/r10k/modules.Puppetfile
moduledest=/etc/puppet/modules

[profiles]
puppetfile=/etc/r10k/profiles.Puppetfile
moduledest=/etc/puppet/environments

[signup]
puppetfile=/etc/r10k/environments/Signup.puppetfile
moduledest=/etc/puppet/environments/signup_svc

```

###2) Install or Update *cloud signup* modules based on config

**bash$**
`r10kwrapper -x install -c signup`

**Resulting Actions**
```
PUPPETFILE LOADED = /etc/r10k/environments/Signup.puppetfile
MODULE PATH CREATED = /etc/puppet/environments/signup_svc/<CLONED MODULES>
```

 **Assumptions**:
 `/etc/r10k/wrapper.ini` resembles:

```
#FILE: /etc/r10k/wrapper/ini

[modules]
puppetfile=/etc/r10k/modules.Puppetfile
moduledest=/etc/puppet/modules

[profiles]
puppetfile=/etc/r10k/profiles.Puppetfile
moduledest=/etc/puppet/environments

[signup]
puppetfile=/etc/r10k/environments/Signup.puppetfile
moduledest=/etc/puppet/environments/signup_svc

```
