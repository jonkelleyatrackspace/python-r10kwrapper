from setuptools import setup
from sys import path

path.insert(0, '.')

NAME = "r10kwrapper"

if __name__ == "__main__":

    setup(
        name = NAME,
        version = "0.1.3",
        author = "Jon Kelley",
        author_email = "jon.kelley@rackspace.com",
        url = "https://github.com/jonkelleyatrackspace/r10kwrapper",
        license = 'The FreeBSD Copyright',
        packages = [NAME],
        package_dir = {NAME: NAME},
        description = "r10kwrapper - a wrapper for r10k",
        entry_points={
            'console_scripts': [ 'r10kwrapper = r10kwrapper.r10kwrapper:main' ],
        }
    )

