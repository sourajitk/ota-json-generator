from datetime import datetime
from time import mktime, time
import hashlib
import json
import os
import re
import sys
import zipfile

HOME_DIR = os.path.expanduser('~')
BLOCKSIZE = 65536

def gen_json(incoming_file, device):
    parent_dir = "/".join(incoming_file.split("/")[0:-1])
    parent_dir_bare = incoming_file.split("/")[-3]
    target_file = '{}/json/{}.json'.format(HOME_DIR, device)
    with open(target_file, 'r') as f:
        contents = json.load(f)['response']
        print(contents)
        download_base_url = "https://downloads.statixos.com/{}/{}/".format(parent_dir_bare, device)
        rom = {}
        rom['filepath'] = incoming_file.split("/")[-1]
        zip_file = incoming_file.split("/")[-1][:-4]
        rom['type'] = zip_file.split("-")[-1]
        builddate = "".join(zip_file.split("-")[1:3])
        try:
            with zipfile.ZipFile(incoming_file, 'r') as update_zip:
                metadata = update_zip.read('META-INF/com/android/metadata').decode('utf-8')
                timestamp = int(re.findall('post-timestamp=([0-9]+)', metadata)[0])
        except IsADirectoryError:
            return
        except:
            timestamp = int(mktime(datetime.strptime(builddate, '%Y%m%d%H%M').timetuple()))

        rom['datetime'] = timestamp
        rom['version'] = zip_file.split("-")[-2][1:]
        rom['filename'] = zip_file + ".zip"
        rom['size'] = os.path.getsize(incoming_file)
        hasher = hashlib.md5()
        with open(incoming_file, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        rom['id'] = hasher.hexdigest()
        res ={
            "url": '{}{}'.format(download_base_url, rom['filepath']),
            "romtype": rom['type'],
            "datetime": rom['datetime'],
            "version": rom['version'],
            "filename": rom['filename'],
            "size": rom['size'],
            "id": rom['id'],
        }
        contents[0] += [res]

    print(json.dumps({"response": contents}, indent=4))
    with open('{}/json/{}.json'.format(HOME_DIR, device), 'w') as f:
        print(json.dumps({"response": contents}, indent=4), file=f)
