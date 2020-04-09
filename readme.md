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
    python main.py --dump_feature_tenhou --prefix <prefix_str>
```
<prefix_str> is prefix of json filename in tenhou_mjailog (for example 2018, 20180104, 2018010400gm-00a9).
Note that system.exe from akochan, and converted mjai-log of Tenhou is required.
When you run with option --update, old output is updated.
Output files are saved in tenhou_npz directory.

## Used materials

Images : https://majandofu.com/mahjong-images