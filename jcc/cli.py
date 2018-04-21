import argparse
import os
import sys

from .client import JupyterContentsClient
from . import __version__

def main():
    version = '%(prog)s ' + __version__
    env_url = os.environ.get('JCC_URL')
    env_token = os.environ.get('JCC_TOKEN')

    parser = argparse.ArgumentParser(
        description='Jupyter Contents Client command line interface')

    parser.add_argument('VERB', choices=['GET', 'PUT'], type=str.upper,
                        help='specify which action to perform')

    parser.add_argument('FILE', nargs='*',
                        help='list of files or directories to transfer')

    parser.add_argument('--url', nargs='?', default=env_url,
                        help='defaults to the JCC_URL environment variable')

    parser.add_argument('--token', nargs='?', default=env_token,
                        help='defaults to the JCC_TOKEN environment variable')

    parser.add_argument('--prefix', nargs='?', default='',
                        help='set upload or download path prefix')

    parser.add_argument('-s', '--silent', action='store_true',
                        help='do not show progress bars')

    parser.add_argument('-v', '--version', action='version', version=version)

    args = vars(parser.parse_args())

    url, token = args['url'], args['token']
    if not url or not token:
        print('Both URL and TOKEN are mandatory.')
        sys.exit(1)

    jcc = JupyterContentsClient(url, token, show_progress=not args['silent'])
    action = dict(GET=jcc.download, PUT=jcc.upload)[args['VERB']]

    for f in args['FILE']:
        action(f, args['prefix'])
