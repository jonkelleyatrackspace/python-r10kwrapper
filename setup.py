from setuptools import setup
from sys import path

path.insert(0, '.')

NAME = "r10kwrapper"

if __name__ == "__main__":

    setup(
        name = NAME,
        version = "0.1.0",
        author = "Jon Kelley",
        author_email = "jon.kelley@rackspace.com",
        url = "https://github.com/jonkelleyatrackspace/r10kwrapper",
        license = 'internal use',
        packages = [NAME],
        package_dir = {NAME: NAME},
        description = "zabbixctl - Utility that connects to Zabbix API",

        install_requires = ['subprocess',
                            'argparse',
                            'logging',
                            'ConfigParser'],
        entry_points={
            'console_scripts': [ 'r10kwrapper = r10kwrapper.r10kwrapper:main' ],
        }
    )

