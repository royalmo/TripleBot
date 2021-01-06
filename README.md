# TripleBot

*Made by royalmo*

## What is it?

This Discord bot will play custom sounds by just typing some `!commands` in a text channel. You can add, remove and modify any custom sound.

The bot has also the function of *speak a code*, that will pronounce all the ascii letters with catalan accent (or yours, if you change the sound files). If you type `!repetir`, it will repeat last code said on that Discord server.

### Commands
*This is the help message that the bot will show to us if we type `!triple help` or `!triple help keep`*

`!codi XXxXXx` or `!code YyYYyyY`: Speak in cursed catalan an ascii-letters code.
`!repetir`: Repeats last saved code.

`!triple help`: Shows this updated menu.
`!triple help keep`: Shows and doesn't delete this menu.

*Current soundbox commands:*
`!triple`, `!letsgo`, `!rot`, ... (It will depend of the sounds you have)


## How do I use it?

To use the bot, you need to do the following steps:

### 1. Token
Get yourself a Discord bot token, and place it in `bot_token.json`.

### 2. Server & permissions
Invite the bot in one (or many) Discord servers. The bot will need the permissions to join and talk on voice channels, see and send messages, delete messages from any server member.

The permissions number is `3288320`, but you can also generete it by yourself on the Discord developper website.

### 3. Be in a voice chat
Once you are in a voice chat, type a command (type `!triple help` to see the list of commands). The bot will come to your voice chat and play the requested sound.

The bot can **only play a sound request at once**, so if you invite him in multiple servers, it may work slower than expected.


## How do I add sounds?
If you want to add the `cow` sound, for example, you will need to do some steps:

### Add the .mp3 sound.
Rename the **.mp3 file sound** as `cow_sound.mp3`, and place it into the `sounds` folder.

### Add the command.
Go to `bot_settings.json`, and add `"cow"` at the end of the list. Make sure to leave a comma at the end of each element, except the last one.

### Apply changes.
Restart your bot, or send `!triple reload` through a text channel. You will then be able to listen to your fresh and new sound!