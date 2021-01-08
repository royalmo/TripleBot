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
from platform import system
from os import system as terminal

PYPATH = str(Path(__file__).parent.absolute()) + "/"
THISOS = system()
WINDOWS_FFMPEG_PATH = "C:/ffmpeg/bin/ffmpeg.exe"

# The admin id is the only discord user that can restart the hosted pc (this will only work in ubuntu)
ADMIN_ID = 354215919318466561

# Loads settings
with open(PYPATH + 'bot_token.json', 'r') as json_token:
    filein = json.loads(json_token.read())
    DISCORD_TOKEN = filein['token']

# Load commands
with open(PYPATH + 'bot_settings.json', 'r') as json_token:
    filein = json.loads(json_token.read())
    COMMAND_LIST = filein['cmds']

def update_db_cmds():
    # Database settings
    conn = sqlite3.connect(PYPATH + "db/stats.db")
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
    # Database settings
    conn = sqlite3.connect(PYPATH + "db/stats.db")
    conn_cursor = conn.cursor()

    # Get current commands
    conn_cursor.execute("SELECT name, times_played, added_at, last_played FROM Sounds WHERE name='" + commandname + "'")
    response = conn_cursor.fetchall()[0]

    # Close the connection
    conn.close()

    return response

def db_get_times_played():
    # Database settings
    conn = sqlite3.connect(PYPATH + "db/stats.db")
    conn_cursor = conn.cursor()

    # Get current commands
    conn_cursor.execute("SELECT name, times_played FROM Sounds")
    response = conn_cursor.fetchall()

    # Close the connection
    conn.close()

    return response

def db_command_played(commandname):
    # Database settings
    conn = sqlite3.connect(PYPATH + "db/stats.db")

    conn_cursor = conn.cursor()

    # Get current commands
    conn_cursor.execute("SELECT times_played FROM Sounds WHERE name='" + commandname + "'")
    times_played = int(conn_cursor.fetchall()[0][0]) + 1

    conn_cursor.execute("UPDATE Sounds SET times_played=" + str(times_played) + ", last_played=" + str(int(time.time())) + " WHERE name='" + commandname + "'")
    conn.commit()

    # Close the connection
    conn.close()


def reload_cmds():
    global COMMAND_LIST
    with open(PYPATH + 'bot_settings.json', 'r') as json_token:
        filein = json.loads(json_token.read())
        COMMAND_LIST = filein['cmds']

    update_db_cmds()

class TskBot(discord.Client):
    async def on_ready(self):
        # Print info message.
        print(f'Connected to Discord!\n\nBot username: {self.user}\n')

        # Setting Watching status
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="impostors"))

        self.is_playing = False
        self.last_code = {}

    async def on_message(self, message):

        # Checks if message isn't from the bot itself and it is plain text. 
        if message.author == self.user or message.type != discord.MessageType.default:
            return

        content = message.content

        if content in ['!' + comm for comm in COMMAND_LIST]:

            voice_channel = message.author.voice

            # Only play music if user is in a voice channel
            if voice_channel!= None and not self.is_playing:

                # Set playing status
                self.is_playing = True

                # Create StreamPlayer
                vc = await voice_channel.channel.connect()

                audiopath = PYPATH + 'sounds/' + content[1:] + '_sound.mp3'

                # Play the audio file
                if THISOS=="Windows":
                    vc.play(discord.FFmpegPCMAudio(executable=WINDOWS_FFMPEG_PATH, source=audiopath))
                else:
                    vc.play(discord.FFmpegPCMAudio(source=audiopath))

                db_command_played(content[1:])
                while vc.is_playing():
                    await asyncio.sleep(.1)

                # Disconnect after the player has finished
                await vc.disconnect()

                # Set playing status
                self.is_playing = False

            elif self.is_playing:
                msg = await message.channel.send('I am already playing a sound!')
                await msg.delete(delay=5)

            else:
                msg = await message.channel.send('User is not in a channel.')
                await msg.delete(delay=5)

            await message.delete()
            return

        if content in ["!triple fetch", "!triple fetch reboot"]:
            auth_id = message.author.id
            tchannel = message.channel
            await message.delete()
            
            terminal("cd " + PYPATH + " && git fetch && git pull")
            reload_cmds()

            msg = await tchannel.send('Fetched!')
            await msg.delete(delay=5)

            if content == "!triple fetch reboot":
                if auth_id==ADMIN_ID and THISOS=="Linux":
                    msg = await tchannel.send('Rebooting in 5 seconds!')
                    await msg.delete(delay=4)
                    asyncio.sleep(5)
                    terminal("sudo reboot")
                else:
                    msg = await tchannel.send('Can\'t reboot!')
                    await msg.delete(delay=5)

        if content == "!triple stats":
            tchannel = message.channel
            db_response = db_get_times_played()
            msg = await tchannel.send('**TRIPLE STATS**' + ''.join(['\n*{0}* has been played {1} times.'.format(command, times) for command, times in db_response]))
            await msg.delete(delay=15)
            await message.delete()

        if content in ['!triple stats ' + comm for comm in COMMAND_LIST]:
            tchannel = message.channel
            db_response = db_get_single_info(''.join(content.split()[2:]))
            msg = await tchannel.send('**TRIPLE STATS**: *{0}*\nHas been played {1} times.\nKeeping track of since *{2}*\nLast played: *{3}*'.format(db_response[0], db_response[1], time.ctime(int(db_response[2])), time.ctime(int(db_response[3])) if int(db_response[3]) != 0 else "Hasn't been played."  ) )
            await msg.delete(delay=15)
            await message.delete()

        if content == "!repetir" and str(message.guild.id) in self.last_code:
            code = self.last_code[str(message.guild.id)]

            voice_channel = message.author.voice

            # Only play if user is in a voice channel
            if voice_channel!= None and not self.is_playing:

                # Set playing status
                self.is_playing = True

                # Create StreamPlayer
                vc = await voice_channel.channel.connect()

                # Play the audio file
                audiopath = PYPATH + 'sounds/elcodigoes.mp3'
                if THISOS=="Windows":
                    vc.play(discord.FFmpegPCMAudio(executable=WINDOWS_FFMPEG_PATH, source=audiopath))
                else:
                    vc.play(discord.FFmpegPCMAudio(source=audiopath))

                while vc.is_playing():
                    await asyncio.sleep(.1)

                for letter in code:

                    if letter in ascii_lowercase:
                        audiopath = PYPATH + 'alphabet/' + letter + '.mp3'

                        if letter == 'w':
                            audiopath = PYPATH + 'alphabet/' + letter + choice(['1', '2']) + '.mp3'

                        # Play the audio file
                        if THISOS=="Windows":
                            vc.play(discord.FFmpegPCMAudio(executable=WINDOWS_FFMPEG_PATH, source=audiopath))
                        else:
                            vc.play(discord.FFmpegPCMAudio(source=audiopath))

                        while vc.is_playing():
                            await asyncio.sleep(.1)

                # Disconnect after the player has finished
                await vc.disconnect()

                # Set playing status
                self.is_playing = False

            elif self.is_playing:
                msg = await message.channel.send('I am already playing a sound!')
                await msg.delete(delay=5)

            else:
                msg = await message.channel.send('User is not in a channel.')
                await msg.delete(delay=5)

            # I don't delete de msg cuz i want to keep the code on the chat.
            await message.delete()
            return

        if len(content.split())==2:
            if content.split()[0] in ["!codi", "!code"]:
                code = content.split()[1].lower()
                self.last_code[str(message.guild.id)] = code

                voice_channel = message.author.voice

                # Only play if user is in a voice channel
                if voice_channel!= None and not self.is_playing:

                    # Set playing status
                    self.is_playing = True

                    # Create StreamPlayer
                    vc = await voice_channel.channel.connect()

                    # Play the audio file
                    audiopath = PYPATH + 'sounds/elcodigoes.mp3'
                    if THISOS=="Windows":
                        vc.play(discord.FFmpegPCMAudio(executable=WINDOWS_FFMPEG_PATH, source=audiopath))
                    else:
                        vc.play(discord.FFmpegPCMAudio(source=audiopath))

                    while vc.is_playing():
                        await asyncio.sleep(.1)

                    for letter in code:

                        if letter in ascii_lowercase:
                            audiopath = PYPATH + 'alphabet/' + letter + '.mp3'

                            if letter == 'w':
                                audiopath = PYPATH + 'alphabet/' + letter + choice(['1', '2']) + '.mp3'

                            # Play the audio file
                            if THISOS=="Windows":
                                vc.play(discord.FFmpegPCMAudio(executable=WINDOWS_FFMPEG_PATH, source=audiopath))
                            else:
                                vc.play(discord.FFmpegPCMAudio(source=audiopath))

                            while vc.is_playing():
                                await asyncio.sleep(.1)

                    # Disconnect after the player has finished
                    await vc.disconnect()

                    # Set playing status
                    self.is_playing = False

                elif self.is_playing:
                    msg = await message.channel.send('I am already playing a sound!')
                    await msg.delete(delay=5)

                else:
                    msg = await message.channel.send('User is not in a channel.')
                    await msg.delete(delay=5)

                # I don't delete de msg cuz i want to keep the code on the chat.
                # await message.delete()
                return

        if content in ['!triple help', '!triple help keep']:
            msg = await message.channel.send('**COMMANDS:**\n`!triple fetch`: Syncs the project folder with the repository.\n`!codi XXxXXx` or `!code YyYYyyY`: Speak in cursed catalan an ascii-letters code.\n`!repetir`: Repeats last saved code.\n`!triple stats`: Shows some information about the popularity of each audio.\n`!triple stats X`: Shows all statistics about soundbox *X*.\n`!triple help`: Shows this updated menu.\n`!triple help keep`: Shows and doesn\'t delete this menu.\n\n*Current soundbox commands:*\n`!' + '`, `!'.join(COMMAND_LIST) + '`.\n\n*Made by royalmo:* https://github.com/royalmo/TripleBot')
            if content != '!triple help keep':
                await msg.delete(delay=25)
            await message.delete()
            return


if __name__ == "__main__":

    # Welcome message
    print("*"*55 + "\n" + " "*9 + "Triple BOT - Discord server manager\n" + "*"*55 + "\n\nUpdating database...")
    update_db_cmds()
    
    print("Database updated!\nLoading settings and connecting to Discord...")

    # Runs bot after 30 seconds of delay. Why we do this? Because when raspi boots, network is ready some seconds after rc.local is executed, so if we don't wait the program crashes.
    sleep(30)

    # Starting the bot
    mainbot = TskBot()
    mainbot.run(DISCORD_TOKEN)