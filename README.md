# TripleBot

Summary:
- [What is it?](#what-is-it)
- [How do I add it on my Discord Server?](#how-do-i-add-it-on-my-discord-server)
- [How do Install it on my own device?](#how-do-i-install-it)
- [How do I add sounds?](#how-do-i-add-sounds)

*Made by royalmo*

## What is it?

This Discord bot will play custom sounds by just typing some `!commands` in a text channel. You can add, remove and modify any custom sound.

The bot has also the function of *speak a code*, that will pronounce all the ascii letters with catalan accent (or yours, if you change the sound files). If you type `!repetir`, it will repeat last code said on that Discord server.

### Commands
*This is the help message that the bot will show to us if we type `!triple help` or `!triple help keep`*

**TRIPLEBOT COMMANDS:**

`!triple ranks`: Shows the top 10 sounds, like a ranking.

`!triple ranks users`: Shows the top 10 users, like a ranking.


`!triple calla`: Please, don't do this, be nice with the bot :(

`!triple reload`: Reoads this menu and all the comands and databases.

`!triple fetch`: Syncs the project folder with the repository.


`!code YyYYyyY`: Speak in cursed catalan a letters-only code.

`!code XXXXXX 3`: Speak the code 3 times (must be a number between 1 and 5)

`!repetir`: Repeats last saved code.


`!triple stats`: Shows your stats.

`!triple stats X`: Shows all statistics about soundbox *X*.

`!triple stats @someone`: Shows statistics about @someone.


`!triple help`: Shows this updated menu.

`!triple <command> keep`: Does the <command> and doesn't delete the response.


*Current soundbox commands:*
`!triple`, `!letsgo`, `!rot`, ... (It will depend of the sounds you have, or are on the server at that moment)


**Max. sounds before timeout:** 2 sounds every 30 secs, 15 sounds every 10 mins or 30 sounds every 30 mins.


## How do I add it on my Discord Server?

If you are an Admin of a Discord Server, you can add your bot by going to [ericroy.net/add-triplebot](https://ericroy.net/add-triplebot "ericroy.net/add-triplebot").

Then, you can start using the bot by typing commands (see all commands in `!triple help keep`). Be sure to be in a voice channel so you can listen the sounds!

## How do Install it?

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

You may also want the python file to always run when the PC is started. If you are on linux, you can do the following:
```
sudo nano /etc/rc.local
```
And add a line just before the `exit 0`:
```
sudo python3 /path/to/your/TripleBot/triplebot.py &
```

Now, everytime you reboot your system, the bot will launch itself.

### 2. Server & permissions
Invite the bot in one (or many) Discord servers. The bot will need the permissions to join and talk on voice channels, see and send messages, delete messages from any server member.

The permissions number is `3288320`, but you can also generete it by yourself on the Discord developper website.

### 3. Be in a voice chat
Once you are in a voice chat, type a command (type `!triple help` to see the list of commands). The bot will come to your voice chat and play the requested sound.

The bot can **only play a sound request at once**, so if you invite him in multiple servers, it may work slower than expected.

As you are hosting your own bot, you can change the `ADMIN_ID`, so you can run hidden commands, such as `!triple fetch restart` (fetch and restart the python file), `!triple guilds` (a list of all the guilds the bot is in), or `!triple guilds ranks` (the top 10 guilds that played the most sounds).


## How do I add sounds?

*If you are not hosting the bot, you can open a Pull Request with these changes (you'll need to Fork the repository first), and I'll be glad to apply them. If you are hosting the bot, just ignore this line.*

If you want to add the `cow` sound, for example, you will need to do some steps:

### 1. Add the .mp3 sound
Rename the **.mp3 file sound** as `cow_sound.mp3`, and place it into the `sounds` folder.

### 2. Add the command
Go to `bot_settings.json`, and add `"cow"` at the end of the list. Make sure to leave a comma at the end of each element, except the last one.

### 3. Apply changes
Restart your bot, or send `!triple reload` through a text channel. You will then be able to listen to your fresh and new sound!