## Execute
Execute main.py

```$ python main.py```

## Read an mjai-log
You can read an mjai-log in log directory by

```File > Open```

## Play a game
You need to copy following from akochan(https://github.com/critter-mj/akochan)

ai.dll (windows)  
libai.so (linux)  
system.exe  
setup_mjai.json  
params  

Then you can play a game by

```AI > Start Game```

and input random seed (non-negative integer).

## Convert Tenhou-log to mjai-log

1. Create a directory named 'tenhou_rawlog'  
2. download scraw20XX.zip from https://tenhou.net/sc/raw/ and put extracted directory('scraw20XX') in 'tenhou_rawlog' directory  
3. Clone and build akochan-reviewer in root directory  
```
    git clone https://github.com/Equim-chan/akochan-reviewer.git
    cd akochan-reviewer
    cargo build
```
4. Run. Output will be saved in tenhou_mjailog directory.
```
    python main.py --tenhou_convlog --year 20XX
```

## Dump feature for supervised learning
```
    python main.py --dump_feature --input_logdir logdir --input_regex log*.json --output_npzdir outdir
```
Note that system.exe from akochan is required.
This command assumes that logfiles log001.json, log002.json, ... are in directory logdir.
Output files are saved in directory outdir.

## Check supervised model
```
    python main.py --check_model --log_line XX
```
Supervised model shows probability of each action at line XX(1-indexed) of log/haifu_log_1001_0.json.

```
    python main.py --check_model --log_line XX --player_id P
```
A player P(one of 0,1,2,3), chooses action at line XX of log/haifu_log_1001_0.json.


## Input arguments from text file
The argument '--argfile xx.txt' is expanded with the contents of xx.txt.
That is, the command
```
    python main.py --dump_feature --input_logdir logdir --input_regex log*.json --output_npzdir outdir
```
is equivalent with
```
    python main.py --dump_feature --argfile xx.txt --output_npzdir outdir
```
when the contents of xx.txt is the following.
```
--input_logdir logdir
--input_regex log*.json
```
Note that '--dump_feature' and '--output_npzdir outdir' can be included in xx.txt.

## Used materials

Images : https://majandofu.com/mahjong-images