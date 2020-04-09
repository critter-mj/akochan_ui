import subprocess
import gzip
import codecs
import glob
import argparse
from pathlib import Path

def get_mjai_log(tenhou_id):
    cmd = "akochan-reviewer/target/debug/akochan-reviewer --no-review --tenhou-id " + tenhou_id + " --mjai-out -"
    try:
        output = subprocess.check_output(cmd.split())
        return output.decode('utf-8').rstrip()
    except:
        print("get_mjai_log failed:", tenhou_id)
        return "failure"

def get_id_list(gz_path):
    ret = []
    with gzip.open(gz_path, 'rb') as f:
        contents = codecs.getreader("utf-8")(f)
        for line in contents:
            segs = line.split('|')
            rule = segs[2].rstrip().lstrip()
            if rule.startswith("四鳳南喰赤"):
                tenhou_id = segs[3].split('"')[1].split('=')[1]
                ret.append(tenhou_id)
    return ret

def proc_gz(gz_path):
    date_str = gz_path.split('/')[-1].split('.')[0]
    id_list = get_id_list(gz_path)
    outdir_pathstr = "tenhou_mjailog/" + date_str[3:7] + "/" + date_str[3:]
    outdir = Path(outdir_pathstr)
    if not outdir.is_dir():
        outdir.mkdir(parents=True)

    for tenhou_id in id_list:
        outfile_pathstr = outdir_pathstr + "/" + tenhou_id + ".json"
        if Path(outfile_pathstr).is_file():
            continue
        mjai_log = get_mjai_log(tenhou_id)
        if mjai_log == "failure":
            continue
        with open(outfile_pathstr, "w") as f:
            f.write(mjai_log)

def proc_year(year):
    gz_list = glob.glob("tenhou_rawlog/scraw" + str(year) + "/" + str(year) + "/scc*.html.gz")
    for gz_path in gz_list:
        proc_gz(gz_path.replace("\\","/"))
    #print(gz_list)

