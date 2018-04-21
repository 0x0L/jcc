# jcc : Jupyter Contents Client

Easy download/upload files or directories from/to Jupyter instances.

## Command line

```shell
$ export JCC_URL="http://myremote.aws.server.com:8888/"
$ export JCC_TOKEN="72f1d23029232d6866ac3add99f8a65d1ffadb40ffd489bd"

$ jcc get folder/notebook.ipynb
$ jcc get folder

$ jcc put ~/data/work.csv
$ jcc put ~/data

$ jcc -h
```

## Python

```python
url = 'http://myremote.aws.server.com:8888/'
token = '72f1d23029232d6866ac3add99f8a65d1ffadb40ffd489bd'

from jcc import JupyterContentsClient
client = JupyterContentsClient(url, token)

client.download('folder/notebook.ipynb')
client.download('folder')

client.upload('/home/user/data/work.csv')
client.upload('/home/user/data)
```
