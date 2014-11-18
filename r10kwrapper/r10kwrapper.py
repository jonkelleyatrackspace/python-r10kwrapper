#!/usr/bin/python

import logging, subprocess, ConfigParser, argparse, sys, os

__author__  = 'Jonathan Kelley'

wrapper_conf = '/etc/r10k/wrapper.ini'

r10k_binary = os.environ.get('R10K_BINARY','/usr/bin/r10k')
r10k_module = 'puppetfile'

env = os.environ
if env.get('DISPLAY') or env.get('SSH_CLIENT') or env.get('FORCE_ANSI'):
    """ Enables ascii for invokation sources that support it.
        You can force color support by exporting FORCE_ANSI with any value.
    """
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
        attention = '\033[;4;5;34m'
        clear  = '\033[0m'
else:
    class ansi:
        """ ANSI colors """
        black  = ''
        blue   = ''
        green  = ''
        cyan   = ''
        red    = ''
        purple = ''
        brown  = ''
        gray   = ''
        attention = ''
        clear  = ''

def enable_logging(level):
    """ Enables logging at the level passed in. """
    # Plenty of error types for this sort of app huh?
    available_error_levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG ]
    available_err_names = [ 'error', 'warning', 'info', 'debug']
    fmt = (ansi.green + ' :::' + ansi.attention + '%(levelname)-8s' + ansi.red + 
        '::: ' + ansi.clear +' %(message)s')

    try:
        errorlevel = available_error_levels[level]
    except IndexError:
        # Logging failed so lets assume control.
        logging.basicConfig(level=logging.DEBUG,format=fmt)
        logging.critical(ansi.red + "Verbosity levels can only be 0-" + 
            str(len(available_error_levels)-1) + ' ' + str(available_err_names) + ansi.clear)
        sys.exit(254)
    logging.basicConfig(level=errorlevel,format=fmt)

def determine_path_load_method(puppetfile,module_destination,configsection):
    """ Split logic to ensure either dest&configsection defined
        OR configsection defined as config load option. Exit if requirement
        not met.

        If that failure mode is not detected, ELIF statements determine the puppetfile
        and module_destination paths based on the chosen method via argparse."""
    if (configsection == None and module_destination == None or
        configsection == None and puppetfile == None):
        # User didn't provide a way for r10k to know puppetfile and modulepaths.
        # Throw error to user and exit. Either be explicit or load from config.
        logging.critical("You must provide the " + ansi.cyan + "-c" + ansi.clear + 
            " parameter to load from config, \n" +  "\t\tor the " + ansi.cyan + 
            " -p " + ansi.clear +  "and " + ansi.cyan + "-d " + ansi.clear + 
            "parameters to statically reference your r10k configuration.\n" +
            "\t\tUse " + ansi.cyan + "-h " + ansi.clear + "for more information.")
        sys.exit(253)

    elif configsection != None:
        return retrieve_config_sections_from_disk(sections=configsection)

    elif module_destination != None and puppetfile != None:
        return [(puppetfile,module_destination),]

def retrieve_config_sections_from_disk(inifile=wrapper_conf,sections=[]):
    """ Parses the inifile and returns the desired configuration sections.
    """
    config = ConfigParser.RawConfigParser()
    config.read(inifile)

    batch_result = []
    if 'all' in sections:
        for module, envvars in config._sections.items():
            logging.debug(ansi.cyan + 'Found ' + ansi.green + module + ansi.cyan + 
                " within ini file." + ansi.clear )

            puppetfile = envvars['puppetfile']
            module_destination = envvars['moduledest']

            batch_result.append((puppetfile,module_destination))

    else:
        for section in sections:
            puppetfile = config.items(section)[0][1]
            module_destination = config.items(section)[1][1]

            batch_result.append((puppetfile,module_destination))

    return batch_result

def execute_r10k(puppetfile=None,modules_directory=None,action="check",r10k_append_flags=''):
    """ Wraps some magic around the r10k command """

    if not action == "check":
        # We really force check everything.
        execute_r10k(puppetfile=puppetfile,modules_directory=modules_directory,action="check",
            r10k_append_flags=r10k_append_flags)

    command = str(r10k_binary) + " " + str(r10k_module) + " " + str(action) + " " + str(r10k_append_flags)
    env_vars = { 'PATH' : '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                 'PUPPETFILE': puppetfile, 'PUPPETFILE_DIR': modules_directory}

    logging.debug(ansi.brown + "ENV_VARS: " + str(env_vars) + ansi.clear)
    logging.debug(ansi.brown + "SHELLEXEC: " + str(command) + ansi.clear)
    process  = subprocess.Popen(command.split(), stdout=subprocess.PIPE, env=env_vars)
    output   = process.communicate()[0]

    logging.debug(ansi.brown + "STAT: " + str(process.returncode) + ansi.brown + " --- " +
        "STDOUT: " + str(output) + ansi.clear)

    if process.returncode > 0:
        logging.critical( ansi.red + ': r10k execution failed.' + ansi.clear)
        sys.exit(1)

def parse_arguements():
    """ Parses and returns arguements defined by the user. """
    # Assign description to the help doc
    parser = argparse.ArgumentParser(
        description='Wrapper for r10k to ease management of the Rackspace Puppet ' +
        'r10k structure.')

    parser.add_argument(
        '-p', '--puppetfile', type=str, help='Path to Puppetfile holding module ' + 
        'dependecies.', required=False, default=None)
    parser.add_argument(
        '-d', '--dest', type=str, help='Path to deploy Puppetfile modules to.',
        required=False, default=None)
    parser.add_argument(
        '-c', '--configsection', type=str, help='Loads r10k settings from a ini ' + 
        'section. This arguement can be supplied multiple times. If ALL is supplied' +
        ', all sections will be executed. (ex -i modules -i profiles -i signup -i ' + 
        'cloudfeeds)', required=False, action='append', default=None)
    parser.add_argument(
        '-C', '--configfile', type=str, help='Defines the ini file to load. Otherwise ' +
        'it assumes /etc/r10k/wrapper.conf', required=False, default='/etc/r10k/wrapper.conf')
    parser.add_argument(
        '-x', '--action', type=str, help='Action to perform with Puppetfile ' + 
        '(check,install,purge) supported.', required=True, default="check")
    parser.add_argument(
        '-v', '--verbosity', type=int, help='Log level (0 = error, 1 = warn, ' + 
            '2 = info, 3 = debug) (Default: 3)', required=False, default=3)
    parser.add_argument(
        '-f', '--flags_append', type=str, help='Pass trailing arguements to r10k' + 
        ' command, (ex. -v debug)', required=False, default='')

    args = parser.parse_args()

    enable_logging(args.verbosity) # init logging
    r10k_batch_list = determine_path_load_method(puppetfile=args.puppetfile,
        module_destination=args.dest,
        configsection=args.configsection)

    return r10k_batch_list, args.action, args.flags_append

def main():
    """ Triggers everythingggg """
    r10k_action_batch, action, flags_append = parse_arguements()

    num_actions = str(len(r10k_action_batch))
    logging.info(ansi.cyan + ansi.green +  num_actions +
     ansi.cyan + " batch actions gathered for execution" + ansi.clear )

    statuscount = 0
    for puppetfile, module_destination in r10k_action_batch:
        statuscount += 1
        logging.info( ansi.cyan + "Action " + ansi.green + str(statuscount) +
            " of " + num_actions + ansi.brown + " -> " + ansi.cyan + 
            "R10K ACTION=" + ansi.green + str(action) + " " + ansi.cyan +
            "PUPPETFILE=" + ansi.green + puppetfile + ansi.cyan + 
            " PUPPETFILE_DIR=" + ansi.green + module_destination + ansi.clear)

        execute_r10k(puppetfile=puppetfile,
            modules_directory=module_destination, 
            action=action,
            r10k_append_flags=flags_append)

if __name__ == "__main__":
    main()
