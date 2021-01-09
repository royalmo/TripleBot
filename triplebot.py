# TO BE RUNNED ON PYTHON3.8
# MADE BY ERIC ROY (github/royalmo)

# Read README.md first, and be sure to enter your TOKEN
# MAKE SURE YOU HAVE FFmpeg, discord.py and PyNaCl installed.

# Importing stuff
import json
import discord
import asyncio
import sqlite3
import time
from pathlib import Path
from time import sleep
from random import choice
from string import ascii_lowercase
from platform import system as operative_system
from os import system as terminal

# Defining some constants
PYPATH = str(Path(__file__).parent.absolute()) + "/"
THISOS = operative_system()
WINDOWS_FFMPEG_PATH = "C:/ffmpeg/bin/ffmpeg.exe"
MP3_ELCODIGO_PATH = PYPATH + 'sounds/elcodigoes.mp3'
MP3_PERMITAME_PATH = PYPATH + 'sounds/repeatcode.mp3'
DB_PATH = PYPATH + "db/stats.db"

# Putting placeholders for COMMAND_LIST and HELP_TEXT.
# We will set them to the correct values later
COMMAND_LIST, HELP_TEXT = '', ''

# The admin id is the only discord user that can restart the hosted pc
# (this will only work in THISOS=='Linux' systems)
ADMIN_ID = 354215919318466561 # Discord user: royalmo#5186


## DATABASE RELATED FUNCTIONS ##

def update_db_cmds():
    """
    This function is runned on every fetch and at the start of the program.
    It creates the database and the table if they don't exist.
    It adds all the current commands that aren't already on the db.
    """
    # Database settings
    conn = sqlite3.connect(DB_PATH)
    conn_cursor = conn.cursor()
    conn_cursor.execute('SELECT name from sqlite_master where type= "table"')
    tables = [t[0] for t in conn_cursor.fetchall()]

    # Creates table if Sounds doesn't exist
    if 'Sounds' not in tables:
        print("Table not found, creating one.")
        conn_cursor.execute("CREATE TABLE Sounds(id integer PRIMARY KEY, name text, times_played integer, added_at integer, last_played integer)")
        conn.commit()

    # Get current commands
    conn_cursor.execute("SELECT name from Sounds")
    sql_commands = [c[0] for c in conn_cursor.fetchall()]

    # Add new commands if found
    seconds = time.time()
    for command in COMMAND_LIST:
        if command not in sql_commands:
            print("Adding command: " + command)
            conn_cursor.execute("INSERT INTO Sounds(name, times_played, added_at, last_played) VALUES('" + command + "', 0, " + str(int(seconds)) + ", 0)")
            conn.commit()

    conn.close()

def db_get_single_info(commandname):
    """
    Returns all database information (except ID) of a specific command.
    If the command is not found, nothing is returned, so it may cause an IndexError somewhere else.

    Ironic example of `db_get_single_info('triple')`

    `['triple', 10, 94385734, 18907465]`

    Remember that timestamps are on Epoch seconds.
    """
    # Database settings
    conn = sqlite3.connect(DB_PATH)
    conn_cursor = conn.cursor()

    # Get current commands
    conn_cursor.execute("SELECT name, times_played, added_at, last_played FROM Sounds WHERE name='" + commandname + "'")

    # As the '[0]' could cause an index error, we will do it safely
    response = conn_cursor.fetchall()
    if len(response)>0:
        response = response[0]
    else:
        # We create a random return so we see there is some error elsewhere
        # and there is no exceptions.
        response = ['IndexError', 0, 0, 0]

    # Close the connection
    conn.close()

    return response

def db_get_most_times_played():
    """
    This function returns a list of the 10 most played sounds. Example:

    `(['triple', 29], ['rot', 27], ...)`
    """
    # Database settings
    conn = sqlite3.connect(DB_PATH)
    conn_cursor = conn.cursor()

    # Get current commands
    conn_cursor.execute("SELECT name, times_played FROM Sounds ORDER BY times_played DESC LIMIT 10")
    response = conn_cursor.fetchall()

    # Close the connection
    conn.close()

    return response

def db_sound_played(commandname):
    """
    This function is called after every sound is played. It adds on the database the time it has been played and updates the count.

    Comandname sould be a string with the comand. If the command doesn't exist, an IndexError will be thrown.
    """
    # Database settings
    conn = sqlite3.connect(DB_PATH)
    conn_cursor = conn.cursor()

    # Get current commands
    conn_cursor.execute("SELECT times_played FROM Sounds WHERE name='" + commandname + "'")
    times_played = int(conn_cursor.fetchall()[0][0]) + 1

    conn_cursor.execute("UPDATE Sounds SET times_played=" + str(times_played) + ", last_played=" + str(int(time.time())) + " WHERE name='" + commandname + "'")
    conn.commit()

    # Close the connection
    conn.close()


## UPDATE RELATED FUNCTIONS ##

def update_cmd_list():
    """
    This function updates COMMAND_LIST, and it is executed in fetch_repo and at the start of the program.
    """
    global COMMAND_LIST
    with open(PYPATH + 'bot_settings.json', 'r') as json_token:
        filein = json.loads(json_token.read())
        COMMAND_LIST = filein['cmds']

def update_help_menu():
    """
    This function updates HELP_MENU, and it is executed in fetch_repo and at the start of the program.
    """
    global HELP_TEXT
    commandhelps = '`!' + '`, `!'.join(COMMAND_LIST) + '`.'
    with open(PYPATH + 'triple_help.txt', 'r') as helpin:
        HELP_TEXT = helpin.read().format(commandhelps)

def fetch_repo(download=True):
    """
    This function is called on `!triple fetch` and `!triple fetch reboot`.
    It downloads repository updates, and updates the command list, the help menu and the database.
    """
    # Get new files from GitHub if download is True
    if download:
        terminal("cd " + PYPATH + " && git fetch && git pull")

    # Update commands, help menu and database
    update_cmd_list()
    update_help_menu()
    update_db_cmds()


## DISCORD CLASS ##

class TripleBot(discord.Client):
    async def on_ready(self):
        """
        This function is executed when the bot just connected to Discord.
        """
        # Print info message.
        print(f'Connected to Discord!\n\nBot username: {self.user}\n')

        # Setting Watching status
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="impostors"))

        self.playing_on = []
        self.last_code = {}

    async def send_to_ch(self, channel, text, delete=None):
        """
        Sends a message to a `channel [TextChannel]` with the desired `text [str]`.
        
        If `delete != None`, it deletes the message after `delete [int]` seconds.
        """
        # Sends msg
        msg = await channel.send(text)

        # Deletes msg
        if delete != None:
            await msg.delete(delay=delete)

    async def play_sound(self, audio_path, voice_channel):
        """
        This function will play a sound on a voice channel, and will wait for it to stop.

        `voice_channel`: A VoiceChannel object where the bot is connected to.

        `audio_path`: A string with the absolute path of the mp3 file.
        """
        if THISOS=="Windows":
                    voice_channel.play(discord.FFmpegPCMAudio(executable=WINDOWS_FFMPEG_PATH, source=audio_path))
        else:
            voice_channel.play(discord.FFmpegPCMAudio(source=audio_path))

        while voice_channel.is_playing():
            await asyncio.sleep(.1)

    async def play_code(self, code, voice_channel, times=1):
        """
        This function will play a sound on a voice channel, and will wait for it to stop.

        `voice_channel`: A VoiceChannel object where the bot is connected to.

        `code`: The code it needs to play

        `times`: The times it needs to play that code (default: 1)
        """
        # First we play the sound 'el codigo es'
        await self.play_sound(MP3_ELCODIGO_PATH, voice_channel)

        # While for how many times we play the code
        while times>0:
            times -= 1

            for letter in code:

                if letter in ascii_lowercase:
                    audiopath = PYPATH + 'alphabet/' + letter + '.mp3'

                    if letter == 'w':
                        audiopath = PYPATH + 'alphabet/' + letter + choice(['1', '2']) + '.mp3'

                    # Play the audio file
                    await self.play_sound(audiopath, voice_channel)

            if times > 0: #Play 'permitame repetir'
                await self.play_sound(MP3_PERMITAME_PATH, voice_channel)

    async def on_message(self, message):
        """
        This function is executed everytime a message is received from anyone and from any channel.
        """

        # Checks if message isn't from the bot itself and it is plain text. 
        if message.author == self.user or message.type != discord.MessageType.default or len(message.content)<1:
            return

        # As all the commands use ! at the beggining, we can forget about all the other messages.
        if message.content[0] != '!':
            return

        # Defining some temp constants
        content = message.content.lower()
        channel = message.channel
        auth_id = message.author.id
        auth_vc = message.author.voice
        guild_id = message.guild.id

        # Single commands: !triple help
        if content in ['!triple help', '!triple help keep']:

            await self.send_to_ch(channel, HELP_TEXT, None if 'keep' in content else 25)

            await message.delete()
            return

        # Single commands: !triple fetch (reboot is for admin only)
        if content in ["!triple fetch", "!triple fetch reboot"]:

            # Delete the message to let the user see something is happening.
            await message.delete()
            
            # Fetch and pull from repository
            fetch_repo()

            # Shows a message
            await self.send_to_ch(channel, 'Fetched!' + ('\nRebooting...' if 'reboot' in content else ''), 5)

            # Reboot if in linux and if requester is admin.
            if 'reboot' in content:
                if auth_id==ADMIN_ID and THISOS=="Linux":

                    await self.close() # Close the Discord connection
                    terminal("sudo reboot")

                else:
                    await self.send_to_ch(channel, 'Can\'t reboot!\nNo permmissions or bad OS.', 5)

        # Triple ranks: shows top 10 audios
        if content == "!triple ranks":

            db_response = db_get_most_times_played()

            await self.send_to_ch(channel, '**TripleBot Ranks** - *Top 10 sounds.*' + ''.join(['\n**{0}**: has been played {1} times.'.format(command.upper(), times) for command, times in db_response]), 15)

            await message.delete()

        # Triple stop (admin only). Stops the bot
        if content == '!triple stop' and auth_id == ADMIN_ID:

            await self.send_to_ch(channel, "Stopping bot...", 2)

            await message.delete()
            await self.close()
            return

        # Triple calla. Stops any sound and leaves voice_channels
        if content == '!triple calla':
            await self.send_to_ch(channel, "This isn't ready yet!", 5)
            await message.delete()
            # TODO

        # Triple guilds (admin only): shows all guilds the bot is in.
        if content == "!triple guilds" and auth_id == ADMIN_ID:

            await self.send_to_ch(channel, "**GUILDS WHERE I AM:**" + ''.join(['\n{0} - *Id: {1}*'.format(cguild.name, cguild.id) for cguild in self.guilds] ), 15)
            await message.delete()

        # Triple stats [command]: shows all information of a sound
        if content in ['!triple stats ' + comm for comm in COMMAND_LIST]:

            db_response = db_get_single_info(content.split()[2])
            await self.send_to_ch(channel, '**TripleBot Command Stats**: *{0}*\nHas been played {1} times.\nTripleBot is keeping track of this sound since *{2}*\nLast time played: *{3}*'.format(db_response[0], db_response[1], time.ctime(int(db_response[2])), time.ctime(int(db_response[3])) if int(db_response[3]) != 0 else "Hasn't been played yet."  ), 15 )

            await message.delete()

        # Triple stats and triple stats [user]: shows all info about that person.
        # TODO

        # Sound commands
        if content in ['!' + comm for comm in COMMAND_LIST]:

            # Only play music if user is in a voice channel
            if auth_vc != None and guild_id not in self.playing_on:

                # Set playing status
                self.playing_on.append(guild_id)
                vc = await auth_vc.channel.connect()

                audiopath = PYPATH + 'sounds/' + content[1:] + '_sound.mp3'

                await self.play_sound(audiopath, vc)
                db_sound_played(content[1:])

                # Disconnect after the player has finished
                await vc.disconnect()
                self.playing_on.remove(guild_id)

            elif guild_id in self.playing_on:
                await self.send_to_ch(channel, 'I\'m already playing a sound!', 5)

            else:
                await self.send_to_ch(channel, 'User is not in a channel.', 5)

            await message.delete()
            return

        if content == "!repetir":
            if str(message.guild.id) in self.last_code:
                code = self.last_code[str(message.guild.id)]

                # Only play if user is in a voice channel
                if auth_vc!= None and guild_id not in self.playing_on:

                    # Set playing status
                    self.playing_on.append(guild_id)

                    # Create StreamPlayer
                    vc = await auth_vc.channel.connect()

                    self.play_code(code, vc)

                    # Disconnect after the player has finished
                    await vc.disconnect()

                    # Set playing status
                    self.playing_on.remove(guild_id)

                elif guild_id in self.playing_on:
                    await self.send_to_ch(channel, 'I\'m already playing a sound!', 5)

                else:
                    await self.send_to_ch(channel, 'User is not in a channel.', 5)

                # I don't delete de msg cuz i want to keep the code on the chat.
                await message.delete()
                return

            else:
                await self.send_to_ch(channel, 'I don\'t have anything to repeat!', 5)
                await message.delete()
                return

        if len(content.split())==2:
            if content.split()[0] in ["!codi", "!code"]:
                code = content.split()[1]
                self.last_code[str(message.guild.id)] = code

                # Only play if user is in a voice channel
                if auth_vc != None and guild_id not in self.playing_on:

                    # Set playing status
                    self.playing_on.append(guild_id)

                    # Create StreamPlayer
                    vc = await auth_vc.channel.connect()

                    self.play_code(code, vc)

                    # Disconnect after the player has finished
                    await vc.disconnect()

                    # Set playing status
                    self.playing_on.remove(guild_id)

                elif guild_id in self.playing_on:
                    await self.send_to_ch(channel, 'I\'m already playing a sound!', 5)

                else:
                    await self.send_to_ch(channel, 'User is not in a channel.', 5)

                # I don't delete de msg cuz i want to keep the code on the chat.
                # await message.delete()
                return

        if len(content.split())==3:
            splitted = content.split()
            if splitted[0] in ["!codi", "!code"]:
                code = splitted[1]
                times = splitted[2]

                if times in [1, 2, 3, 4, 5]:
                    timesInt = int(times)
                else:
                    await self.send_to_ch( channel, times + " is not a number between 1 and 5.", 5 )
                    return

                self.last_code[str(message.guild.id)] = code

                # Only play if user is in a voice channel
                if auth_vc != None and guild_id not in self.playing_on:

                    # Set playing status
                    self.playing_on.append(guild_id)

                    # Create StreamPlayer
                    vc = await auth_vc.channel.connect()

                    self.play_code(code, vc, timesInt)

                    # Disconnect after the player has finished
                    await vc.disconnect()

                    # Set playing status
                    self.playing_on.remove(guild_id)

                elif guild_id in self.playing_on:
                    await self.send_to_ch(channel, 'I\'m already playing a sound!', 5)

                else:
                    await self.send_to_ch(channel, 'User is not in a channel.', 5)

# Main program
if __name__ == "__main__":

    # Welcome message
    print("*"*55 + "\n" + " "*11 + "Triple BOT - Discord soundbox bot\n" + "*"*55 + "\n\nLoading token...")

    # Loading Discord token
    with open(PYPATH + 'bot_token.json', 'r') as json_token:
        filein = json.loads(json_token.read())
        DISCORD_TOKEN = filein['token']

    print("Token loaded!\nUpdating database...")

    fetch_repo(download=False)

    print("Database updated!\nLoading settings and connecting to Discord...")

    # Runs bot after 30 seconds of delay.
    # Why we do this? Because when raspi boots, network becomes ready onnly some seconds after rc.local is executed, so if we don't wait the program crashes.
    # So, we only need to do this when we are on linux.
    if THISOS == "Linux":
        sleep(30)

    # Starting the bot
    mainbot = TripleBot()
    mainbot.run(DISCORD_TOKEN)
