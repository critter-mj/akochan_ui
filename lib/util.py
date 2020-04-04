import json

def read_log_json(file_path):
    ret = []
    with open(file_path, encoding="utf-8") as f:
        # to do error handle
        l = f.readlines()
        for i in range(len(l)):
            ret.append(json.loads(l[i]))
    return ret