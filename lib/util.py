import json
import chardet
import pathlib

def try_mkdir(dir_pathstr):
    dir_path = pathlib.Path(dir_pathstr)
    if not dir_path.is_dir():
        try:
            # mkdir may causes error when the process is parallelized
            dir_path.mkdir(parents=True)
        except FileExistsError as e:
            pass

def chardet_file(file_path):
    with open(file_path, 'rb') as f:
        b = f.read()
    return chardet.detect(b)['encoding']

def read_log_json(file_path):
    ret = []
    try:
        with open(file_path, encoding=chardet_file(file_path)) as f:
            l = f.readlines()
            for i in range(len(l)):
                ret.append(json.loads(l[i]))
    except UnicodeDecodeError as e:
        print('read_log_json: UnicodeDecodeError exception')
        with open(file_path, encoding='utf-8') as f:
            l = f.readlines()
            for i in range(len(l)):
                ret.append(json.loads(l[i]))
        
    return ret