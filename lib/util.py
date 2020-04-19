import json
import chardet

def chardet_file(file_path):
    with open(file_path, 'rb') as f:
        b = f.read()
    return chardet.detect(b)['encoding']

def read_log_json(file_path):
    ret = []
    with open(file_path, encoding=chardet_file(file_path)) as f:
        # to do error handle
        l = f.readlines()
        for i in range(len(l)):
            ret.append(json.loads(l[i]))
    return ret