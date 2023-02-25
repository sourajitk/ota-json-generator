#!/usr/bin/env python3

from datetime import datetime
from time import mktime, time
import hashlib
import json
import os
import pyinotify
import sys
import zipfile

# statix_mata-20210209-1529-11-v4.1-SNOWCONE.zip

HOME_DIR = os.path.expanduser('~')
BLOCKSIZE = 65536

class EventHandler(pyinotify.ProcessEvent):
    def process_IN_CLOSE_WRITE(self, event):
        path = os.path.join(event.path, event.name)
        print(path + " detected, generating json")
        if "img" in path or "OFFICIAL" not in path:
            print(path + "ignored")
        device = event.name.split('-')[0].split('_')[1]
        gen_json(path, device)
        return


def main():
    wm = pyinotify.WatchManager()
    dirmask = pyinotify.IN_CREATE
    dir = sys.argv[1]
    notifier = pyinotify.Notifier(wm, EventHandler())
    wm.add_watch(dir, dirmask, rec=True)
    print("set up watch on " + dir)
    while True:
        try:
            notifier.process_events()
            if notifier.check_events():
                notifier.read_events()
        except KeyboardInterrupt:
            break
    # cleanup: stop the inotify, and close the file handle:
    notifier.stop()

def gen_json(incoming_file, device):
    parent_dir = "/".join(incoming_file.split("/")[0:-1])
    parent_dir_bare = incoming_file.split("/")[-3]
    contents = []
    for incoming_file in os.listdir(parent_dir):
        download_base_url = "https://downloads.statixos.com/{}/{}/".format(parent_dir_bare, device)
        rom = {}
        rom['filepath'] = incoming_file
        zip_file = incoming_file[:-4]
        rom['type'] = zip_file.split("-")[-1]
        builddate = "".join(zip_file.split("-")[1:3])
        try:
            with zipfile.ZipFile('{}/{}'.format(parent_dir, incoming_file), 'r') as update_zip:
                build_prop = update_zip.read('system/build.prop').decode('utf-8')
                timestamp = int(re.findall('ro.build.date.utc=([0-9]+)', build_prop)[0])
        except IsADirectoryError:
            continue
        except:
            timestamp = int(mktime(datetime.strptime(builddate, '%Y%m%d%H%M').timetuple()))

        rom['datetime'] = timestamp
        rom['version'] = zip_file.split("-")[-2][1:]
        rom['filename'] = zip_file + ".zip"
        rom['size'] = os.path.getsize("{}/{}".format(parent_dir, incoming_file))
        hasher = hashlib.md5()
        with open("{}/{}".format(parent_dir, incoming_file), 'rb') as afile:
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
        contents += [res]

    print(json.dumps({"response": [contents]}, indent=4))
    with open('{}/json/{}.json'.format(HOME_DIR, device), 'w') as f:
        print(json.dumps({"response": [contents]}, indent=4), file=f)

if __name__ == '__main__':
    main()
