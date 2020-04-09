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
4. Run  
```
    python main.py --tenhou_convlog --year 20XX
``` 
## Used materials

Images : https://majandofu.com/mahjong-images