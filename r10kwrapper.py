#!/usr/bin/python

import logging, argparse, sys, subprocess

# Command Usage
#  usage: r10kwrapper.py [-h] -p PUPPETFILE -m MODULE_DESTINATION [-x ACTION] [-v VERBOSITY] 
#                        [-f FLAGS_APPEND]
# Where
#
#  -x ACTION......... : Selects an action to pass to r10k. Possible values:
#                      [install] installs the modules from the puppetfile
#                      [check] checks the syntax
#                      [purge] purges modules
#  -p PUPPETFILE..... : Provides the puppetfile you wish to load into r10k
#  -m MOD_DESTINATION : Where the Puppetfile modules should be cloned under.
#  -v VERBOSITY...... : Possible values of 0-3 where higher is more verbosity.
#  -f FLAGS_APPEND... : Append additional flags to be passed at the end of the r10k command when wrapped.
#  -h HELP........... : Unknown

import logging, argparse, sys, subprocess

__author__ = 'Jonathan Kelley'
appname     = 'r10kwrapper'
r10k_binary = '/usr/bin/r10k'
r10k_module = 'puppetfile'

class ansi:
    """ ANSI colors """
    black  = '\033[30m'
    blue   = '\033[34m'
    green  = '\033[32m'
    cyan   = '\033[36m'
    red    = '\033[31m'
    purple = '\033[35m'
    brown  = '\033[33m'
    gray   = '\033[37m'
    clear  = '\033[0m'

def execute_r10k(puppetfile=None,modules_directory=None,action="check",r10k_append_flags=''):
    """ Wraps some magic around the r10k command """

    if not action == "check":
        execute_r10k(puppetfile=puppetfile,modules_directory=modules_directory,action="check",
            r10k_append_flags=r10k_append_flags)

    command = str(r10k_binary) + " " + str(r10k_module) + " " + str(action) + " " + str(r10k_append_flags)

    logging.info(ansi.cyan + "R10K_ACTION=" + ansi.green + str(action) + " " + ansi.cyan +
     "PUPPETFILE=" + ansi.green +puppetfile + ansi.cyan + " PUPPETFILE_DIR=" +
      ansi.green + modules_directory + ansi.clear)

    env_vars = {'PUPPETFILE': puppetfile, 'PUPPETFILE_DIR': modules_directory}
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE, env=env_vars)
    output = process.communicate()[0]
    if process.returncode > 0:
        logging.critical( ansi.red + appname + ': r10k execution failed.' + ansi.clear)
        sys.exit(1)

def parse_arguements():
    """ Parses and returns arguements defined by the user. """
    # Assign description to the help doc
    parser = argparse.ArgumentParser(
        description='Wrapper for r10k to ease management of the Rackspace Puppet r10k structure.')
    # Add arguments
    parser.add_argument(
        '-p', '--puppetfile', type=str, help='Path to Puppetfile (ex. /etc/r10k/dev/modules-rax/Puppetfile', required=True)
    parser.add_argument(
        '-m', '--module_destination', type=str, help='Path to deploy modules under (ex. /etc/puppet/modules-rax/)', required=True)
    parser.add_argument(
        '-x', '--action', type=str, help='Action to perform with Puppetfile (check,install,purge) supported.', required=False, default="check")
    parser.add_argument(
        '-v', '--verbosity', type=int, help='Log level (0 = error, 1 = warn, 2 = info, 3 = debug) (Default: 2)', required=False, default=2)
    parser.add_argument(
        '-f', '--flags_append', type=str, help='Pass trailing arguements to r10k command, (ex. -v debug)', required=False, default='')

    args = parser.parse_args()

    # verbosity input validation
    errorlevel = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG ]
    try:
        errorlevel = errorlevel[args.verbosity]
    except IndexError:
        print (ansi.red + "ERROR: Verbosity levels can only be 0-" + str(len(errorlevel)-1) + ansi.clear)
        sys.exit(254)

    logging.basicConfig(level=errorlevel)
    ##

    return args.puppetfile, args.module_destination, args.action, args.flags_append

if __name__ == "__main__":
    """ Run """
    puppetfile, module_destination, action, flags_append = parse_arguements()
    execute_r10k(puppetfile=puppetfile,modules_directory=module_destination, action=action, r10k_append_flags=flags_append)

