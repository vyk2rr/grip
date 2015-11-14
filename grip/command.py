"""\
grip.command
~~~~~~~~~~~~

Implements the command-line interface for Grip.


Usage:
  grip [options] [<path>] [<address>]
  grip -V | --version
  grip -h | --help

Where:
  <path> is a file to render or a directory containing README.md (- for stdin)
  <address> is what to listen on, of the form <host>[:<port>], or just <port>

Options:
  --user-content    Render as user-content like comments or issues.
  --context=<repo>  The repository context, only taken into account
                    when using --user-content.
  --user=<username> A GitHub username for API authentication.
  --pass=<password> A GitHub password or auth token for API auth.
  --wide            Renders wide, i.e. when the side nav is collapsed.
  --clear           Clears the cached styles and assets and exits.
  --export          Exports to <path>.html or README.md instead of
                    serving, optionally using [<address>] as the out
                    file (- for stdout).
  -b --browser      Open a tab in the browser after the server starts.
  --api-url=<url>   Specify a different base URL for the github API,
                    for example that of a Github Enterprise instance.
                    Default is the public API: https://api.github.com
  --title=<title>   Manually sets the page's title.
                    The default is the filename.
  --noupdate        Do not automatically update the Readme content when
                    the file changes.
"""

from __future__ import print_function

import sys
from path_and_address import resolve, split_address
from docopt import docopt
from .server import clear_cache, serve
from .exporter import export
from . import __version__


usage = '\n\n\n'.join(__doc__.split('\n\n\n')[1:])
version = 'Grip ' + __version__


def main(argv=None, force_utf8=True):
    """
    The entry point of the application.
    """
    if force_utf8 and sys.version_info[0] == 2:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    if argv is None:
        argv = sys.argv[1:]

    # Show specific errors
    if '-a' in argv or '--address' in argv:
        print('Use grip [options] <path> <address> instead of -a')
        print('See grip -h for details')
        return 2
    if '-p' in argv or '--port' in argv:
        print('Use grip [options] [<path>] [<hostname>:]<port> instead of -p')
        print('See grip -h for details')
        return 2

    # Parse options
    args = docopt(usage, argv=argv, version=version)

    # Handle printing version with -V (docopt handles --version)
    if args['-V']:
        print(version)
        return 0

    # Clear the cache
    if args['--clear']:
        try:
            clear_cache()
            return 0
        except ValueError as ex:
            print('Error:', ex)
            return 1

    # Export to a file instead of running a server
    if args['--export']:
        try:
            export(args['<path>'], args['--user-content'], args['--context'],
                   args['--user'], args['--pass'], False, args['--wide'],
                   True, args['<address>'], args['--api-url'], args['--title'])
            return 0
        except ValueError as ex:
            print('Error:', ex)
            return 1

    # Parse arguments
    path, address = resolve(args['<path>'], args['<address>'])
    host, port = split_address(address)

    # Validate address
    if address and not host and not port:
        print('Error: Invalid address', repr(address))

    # Run server
    try:
        serve(path, host, port, args['--user-content'], args['--context'],
              args['--user'], args['--pass'], False, args['--wide'], False,
              args['--api-url'], args['--browser'], args['--title'],
              not args['--noupdate'])
        return 0
    except ValueError as ex:
        print('Error:', ex)
        return 1
