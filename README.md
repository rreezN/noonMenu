# noonMenu
Get the noon menu for today - https://www.nooncph.dk/ugens-menuer
* Currently it only supports MacOS, as it uses Apple Script.

# Arguments
The code can be ran with a simple `python3 menu.py` statement, or you can add an additional argument:  
* `day`: specifies which day to download the menu from. Defaults to `today` if not specified, otherwise (`today`,`tomorrow`, `monday-friday`)
* `--buffer-time`: The time between opening the menu and automatically closing it if not closed by user. Defaults to `30` seconds.
```
python3 menu.py today --buffer-time 30
```

# Nice to know
The scripts automatically creates a `download` directory in your root folder. Within this folder, a subfolder called `week_x` will be created, where ´x´ corresponds to the week number from which the menu was downloaded from. The pdf file will be downloaded to this directory, and kept there until a new week is started. 

This is to ensure that you do not have to wait for the file to be downloaded everytime.

**NOTE**: As a "house-keeping" feature, any sub-directories with week numbers < the current week will be deleted as it contains old data.
