import os
import json
from base64 import b64encode, b64decode
from itertools import accumulate
from urllib.parse import urljoin

from requests import Session
from tqdm import tqdm

_BAR_CONFIG = {
    'bar_format': '{desc}: {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]',
    'unit': 'B',
    'unit_scale': True,
    'unit_divisor': 1024,
    'ncols': 80
}

class JupyterContentsClient(object):
    def __init__(self, url, token, show_progress=True, chunk_size=2**20):
        session = Session()
        session.get(url, params=dict(token=token))
        session.headers.update({'X-XSRFToken': session.cookies['_xsrf']})
        self._session = session

        self.api = urljoin(url, 'api/contents/')
        self.show_progress = show_progress
        self.chunk_size = chunk_size


    def make_dir(self, path):
        r = self._session.put(urljoin(self.api, path), json={'type': 'directory'})
        r.raise_for_status()


    def ensure_dirs(self, path):
        for c in accumulate(path.split('/'), lambda x, y: '/'.join([x, y])):
            self.make_dir(c)


    def upload_file(self, filepath, prefix=''):
        with open(filepath, 'rb') as fobj:
            fname = os.path.basename(filepath)
            fsize = os.path.getsize(filepath)

            pbar = None
            if self.show_progress and tqdm:
                desc = (fname[50:] and '...') + fname[-50:]
                pbar = tqdm(total=fsize, desc=desc, **_BAR_CONFIG)

            self.ensure_dirs(prefix)
            url = urljoin(self.api, os.path.join(prefix, fname))

            chunk = 0
            while chunk >= 0:
                data_chunk = fobj.read(self.chunk_size)
                # always do chunk=1 AND chunk=-1
                chunk = chunk + 1 if data_chunk or (chunk == 0) else -1

                payload = {
                    'chunk': chunk,
                    'content': b64encode(data_chunk).decode('ascii'),
                    'format': 'base64',
                    'type': 'file'
                }

                r = self._session.put(url, json=payload)
                r.raise_for_status()

                if pbar:
                    pbar.update(len(data_chunk))

            if pbar:
                pbar.close()


    def upload_dir(self, path, prefix=''):
        path = os.path.normpath(path)

        files = [
            os.path.join(t[0], f)
            for t in os.walk(path)
            for f in t[-1]
        ]
        files = [f for f in files if os.path.isfile(f)]

        s = os.path.split(path)
        n = len(path) - len(s[-1])

        paths = [os.path.split(f[n:])[0] for f in files]

        for f, p in zip(files, paths):
            self.upload_file(f, os.path.join(prefix, p))


    def upload(self, filepath, prefix=''):
        if os.path.isfile(filepath):
            self.upload_file(filepath, prefix)
        elif os.path.isdir(filepath):
            self.upload_dir(filepath, prefix)


    def download(self, filepath, prefix=''):
        r = self._session.get(urljoin(self.api, filepath))
        r.raise_for_status()

        info = r.json()

        if info['type'] in ['file', 'notebook']:
            fname = os.path.basename(filepath)
            fpath = os.path.join(prefix, fname)

            if prefix:
                os.makedirs(os.path.split(fpath)[0], exist_ok=True)

            if info['format'] == 'json':
                with open(fpath, 'w') as f:
                    json.dump(info['content'], f)
            elif info['format'] == 'text':
                with open(fpath, 'w') as f:
                    f.write(info['content'])
            elif info['format'] == 'base64':
                with open(fpath, 'wb') as f:
                    f.write(b64decode(info['content']))

        elif info['type'] == 'directory':
            for c in info['content']:
                self.download(os.path.join(filepath, c['name']),
                              os.path.join(prefix, filepath))
