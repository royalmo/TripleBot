# TripleBot

*Made by royalmo*

## What is it?

This Discord bot will play custom sounds by just typing some `!commands` in a text channel. You can add, remove and modify any custom sound.

The bot has also the function of *speak a code*, that will pronounce all the ascii letters with catalan accent (or yours, if you change the sound files). If you type `!repetir`, it will repeat last code said on that Discord server.

### Commands
*This is the help message that the bot will show to us if we type `!triple help` or `!triple help keep`*


`!codi XXxXXx` or `!code YyYYyyY`: Speak in cursed catalan an ascii-letters code.

`!repetir`: Repeats last saved code.

`!triple stats`: Shows some information about the popularity of each audio.

`!triple stats X`: Shows all statistics about soundbox X.

`!triple help`: Shows this updated menu.

`!triple help keep`: Shows and doesn't delete this menu.

*Current soundbox commands:*
`!triple`, `!letsgo`, `!rot`, ... (It will depend of the sounds you have)


## How do I use it?

To use the bot, you need to do the following steps:

### 1. Token & Settings
Clone this repository and install the requeriments.

```
git clone https://github.com/royalmo/TripleBot.git
cd TripleBot
pip install discord.py
pip install PyNaCl
```

You will then need to install ffmpeg, in order to play audio files through Discord. If you are working on Windows, make sure the `ffmpeg.exe` is on the same path as the one mentionned in `triplebot.py`.

If you use a linux-based OS, you might want to install the dependencies with `sudo`. You will maybe need to work with pip3 and python3 commands.

Get yourself a Discord bot token, and place it in `bot_token.json`.

Now try to run the bot. Everything should be working. This bot takes a minute to load.
```
python triplebot.py
```
If you type `python triplebot.py fast` instead (and you are on Linux, on Windows it's done automaticly), you will skip a useless timeout i placed.

To be able to run `!triple fetch restart`, you will need to be on Linux, and then you will need to have screen installed.
```
sudo apt-get install screen
```

You may also want the python file to always run when the PC is started. If you are on linux, you can do the following:
```
sudo nano /etc/rc.local
```
And add a line just before the `exit 0`:
```
sudo screen -dmS triplebot -X stuff "python3 /path/to/your/TripleBot/triplebot.py"
```

Now, everytime you reboot your system, the bot will launch itself.

### 2. Server & permissions
Invite the bot in one (or many) Discord servers. The bot will need the permissions to join and talk on voice channels, see and send messages, delete messages from any server member.

The permissions number is `3288320`, but you can also generete it by yourself on the Discord developper website.

### 3. Be in a voice chat
Once you are in a voice chat, type a command (type `!triple help` to see the list of commands). The bot will come to your voice chat and play the requested sound.

The bot can **only play a sound request at once**, so if you invite him in multiple servers, it may work slower than expected.


## How do I add sounds?
If you want to add the `cow` sound, for example, you will need to do some steps:

### 1. Add the .mp3 sound
Rename the **.mp3 file sound** as `cow_sound.mp3`, and place it into the `sounds` folder.

### 2. Add the command
Go to `bot_settings.json`, and add `"cow"` at the end of the list. Make sure to leave a comma at the end of each element, except the last one.

### 3. Apply changes
Restart your bot, or send `!triple reload` through a text channel. You will then be able to listen to your fresh and new sound!