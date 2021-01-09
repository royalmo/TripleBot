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

# Load help text
with open(PYPATH + 'triple_help.txt', 'r') as helpin:
    HELP_TEXT = helpin.read()

# funcio de merda que transforma string a int: https://stackoverflow.com/questions/1265665/how-can-i-check-if-a-string-represents-an-int-without-using-try-except
def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

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

    # Reload help text
    with open(PYPATH + 'triple_help.txt', 'r') as helpin:
        HELP_TEXT = helpin.read()

    update_db_cmds()

class TripleBot(discord.Client):
    async def on_ready(self):
        """
        This function is executed when the bot just connected to Discord.
        """
        # Print info message.
        print(f'Connected to Discord!\n\nBot username: {self.user}\n')

        # Setting Watching status
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="impostors"))

        self.is_playing = False
        self.last_code = {}

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

    async def on_message(self, message):
        """
        This function is executed everytime a message is received from anyone and from any channel.
        """

        # Checks if message isn't from the bot itself and it is plain text. 
        if message.author == self.user or message.type != discord.MessageType.default:
            return

        # Defining some constants
        content = message.content
        channel = message.channel
        auth_id = message.author.id
        auth_vc = message.author.voice

        if content in ['!' + comm for comm in COMMAND_LIST]:

            # Only play music if user is in a voice channel
            if auth_vc != None and not self.is_playing:

                # Set playing status
                self.is_playing = True

                # Create StreamPlayer
                vc = await auth_vc.channel.connect()

                audiopath = PYPATH + 'sounds/' + content[1:] + '_sound.mp3'

                await self.play_sound(audiopath, vc)
                db_command_played(content[1:])

                # Disconnect after the player has finished
                await vc.disconnect()

                # Set playing status
                self.is_playing = False

            elif self.is_playing:
                msg = await channel.send('I am already playing a sound!')
                await msg.delete(delay=5)

            else:
                msg = await channel.send('User is not in a channel.')
                await msg.delete(delay=5)

            await message.delete()
            return

        if content in ["!triple fetch", "!triple fetch reboot"]:

            # Delete the message to let the user see something is happening.
            await message.delete()
            
            # Fetch and pull from repository
            terminal("cd " + PYPATH + " && git fetch && git pull")
            reload_cmds()

            # Shows a message
            msg = await channel.send('Fetched!')
            await msg.delete(delay=5)

            # Reboot if in linux and if requester is admin.
            if content == "!triple fetch reboot":
                if auth_id==ADMIN_ID and THISOS=="Linux":

                    msg = await channel.send('Rebooting in 5 seconds!')
                    await msg.delete(delay=4)
                    asyncio.sleep(5)
                    await self.close() # Close the Discord connection
                    terminal("sudo reboot")

                else:
                    msg = await channel.send('Can\'t reboot!')
                    await msg.delete(delay=5)

        if content == "!triple stats":

            db_response = db_get_times_played()
            msg = await channel.send('**TRIPLE STATS**' + ''.join(['\n*{0}* has been played {1} times.'.format(command, times) for command, times in db_response]))
            await msg.delete(delay=15)
            await message.delete()

        if content == '!triple stop' and auth_id == ADMIN_ID:

            msg = await channel.send("Stopping bot...")
            await msg.delete(delay=2)
            await message.delete()
            await self.close()

        if content == '!triple calla':
            pass

        if content == "!triple guilds" and auth_id == ADMIN_ID:

            msg = await channel.send("**GUILDS WHERE I AM:**" + ''.join(['\n{0} - *Id: {1}*'.format(cguild.name, cguild.id) for cguild in self.guilds] ))
            await msg.delete(delay=15)
            await message.delete()

        if content in ['!triple stats ' + comm for comm in COMMAND_LIST]:

            db_response = db_get_single_info(''.join(content.split()[2:]))
            msg = await channel.send('**TRIPLE STATS**: *{0}*\nHas been played {1} times.\nTripleBot is keeping track of this sound since *{2}*\nLast time played: *{3}*'.format(db_response[0], db_response[1], time.ctime(int(db_response[2])), time.ctime(int(db_response[3])) if int(db_response[3]) != 0 else "Hasn't been played."  ) )
            await msg.delete(delay=15)
            await message.delete()

        if content == "!repetir":
            if str(message.guild.id) in self.last_code:
                code = self.last_code[str(message.guild.id)]

                # Only play if user is in a voice channel
                if auth_vc!= None and not self.is_playing:

                    # Set playing status
                    self.is_playing = True

                    # Create StreamPlayer
                    vc = await auth_vc.channel.connect()

                    # Play the audio file
                    audiopath = PYPATH + 'sounds/elcodigoes.mp3'

                    await self.play_sound(audiopath, vc)

                    for letter in code:

                        if letter in ascii_lowercase:
                            audiopath = PYPATH + 'alphabet/' + letter + '.mp3'

                            if letter == 'w':
                                audiopath = PYPATH + 'alphabet/' + letter + choice(['1', '2']) + '.mp3'

                            # Play the audio file
                            await self.play_sound(audiopath, vc)

                    # Disconnect after the player has finished
                    await vc.disconnect()

                    # Set playing status
                    self.is_playing = False

                elif self.is_playing:
                    msg = await channel.send('I am already playing a sound!')
                    await msg.delete(delay=5)

                else:
                    msg = await channel.send('User is not in a channel.')
                    await msg.delete(delay=5)

                # I don't delete de msg cuz i want to keep the code on the chat.
                await message.delete()
                return

            else:
                msg = await channel.send('I don\'t have anything to repeat!')
                await msg.delete(delay=5)
                await message.delete()
                return

        if len(content.split())==2:
            if content.split()[0] in ["!codi", "!code"]:
                code = content.split()[1].lower()
                self.last_code[str(message.guild.id)] = code

                # Only play if user is in a voice channel
                if auth_vc != None and not self.is_playing:

                    # Set playing status
                    self.is_playing = True

                    # Create StreamPlayer
                    vc = await auth_vc.channel.connect()

                    # Play the audio file
                    audiopath = PYPATH + 'sounds/elcodigoes.mp3'
                    
                    await self.play_sound(audiopath, vc)

                    for letter in code:

                        if letter in ascii_lowercase:
                            audiopath = PYPATH + 'alphabet/' + letter + '.mp3'

                            if letter == 'w':
                                audiopath = PYPATH + 'alphabet/' + letter + choice(['1', '2']) + '.mp3'

                            # Play the audio file
                            await self.play_sound(audiopath, vc)

                    # Disconnect after the player has finished
                    await vc.disconnect()

                    # Set playing status
                    self.is_playing = False

                elif self.is_playing:
                    msg = await channel.send('I am already playing a sound!')
                    await msg.delete(delay=5)

                else:
                    msg = await channel.send('User is not in a channel.')
                    await msg.delete(delay=5)

                # I don't delete de msg cuz i want to keep the code on the chat.
                # await message.delete()
                return
        if len(content.split())==3:
            splitted = content.split()
            if splitted[0] in ["!codi", "!code"]:
                code = splitted[1].lower()
                times = splitted[2]

                if isInt(times):
                    timesInt = int(times)
                    if timesInt < 1 or timesInt > 5 : # Si, limit 5 que tampoc es plan de quedarnos sords.
                        msg = await channel.send(str(times) + " is not a decent number.")
                        await msg.delete(delay=5)
                        return
                else:
                    msg = await channel.send(str(times) + " is not a number.")
                    await msg.delete(delay=5)
                    return

                self.last_code[str(message.guild.id)] = code

                # Only play if user is in a voice channel
                if auth_vc != None and not self.is_playing:

                    # Set playing status
                    self.is_playing = True

                    # Create StreamPlayer
                    vc = await auth_vc.channel.connect()

                    # Play the audio file
                    audiopath = PYPATH + 'sounds/elcodigoes.mp3'
                    repeatpath = PYPATH + 'sounds/repeatcode.mp3'
                    
                    await self.play_sound(audiopath, vc)

                    while timesInt != 0:
                        timesInt -= 1

                        for letter in code:

                            if letter in ascii_lowercase:
                                audiopath = PYPATH + 'alphabet/' + letter + '.mp3'

                                if letter == 'w':
                                    audiopath = PYPATH + 'alphabet/' + letter + choice(['1', '2']) + '.mp3'

                                # Play the audio file
                                await self.play_sound(audiopath, vc)

                        if timesInt > 0: #Play 'permitame repetir'
                            await self.play_sound(repeatpath, vc)

                    # Disconnect after the player has finished
                    await vc.disconnect()

                    # Set playing status
                    self.is_playing = False

                elif self.is_playing:
                    msg = await channel.send('I am already playing a sound!')
                    await msg.delete(delay=5)

                else:
                    msg = await channel.send('User is not in a channel.')
                    await msg.delete(delay=5)

        if content in ['!triple help', '!triple help keep']:
            commandhelps = '`!' + '`, `!'.join(COMMAND_LIST) + '`.'
            msg = await channel.send(HELP_TEXT.format(commandhelps))

            # Deletes de msg if needed only
            if content != '!triple help keep':
                await msg.delete(delay=25)
            await message.delete()
            return


if __name__ == "__main__":

    # Welcome message
    print("*"*55 + "\n" + " "*9 + "Triple BOT - Discord server manager\n" + "*"*55 + "\n\nUpdating database...")
    update_db_cmds()
    
    print("Database updated!\nLoading settings and connecting to Discord...")

    # Runs bot after 30 seconds of delay.
    # Why we do this? Because when raspi boots, network becomes ready onnly some seconds after rc.local is executed, so if we don't wait the program crashes.
    sleep(30)

    # Starting the bot
    mainbot = TripleBot()
    mainbot.run(DISCORD_TOKEN)
