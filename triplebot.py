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
from os import execv, system as terminal
from sys import argv, executable

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
ADMIN_ID = [354215919318466561] # Discord user: royalmo#5186


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
        print("Table Sounds not found, creating one.")
        conn_cursor.execute("CREATE TABLE Sounds(id integer PRIMARY KEY, name text, times_played integer, added_at integer, last_played integer)")

    # Creates table if Users doesn't exist
    if 'Users' not in tables:
        print("Table Users not found, creating one.")
        conn_cursor.execute("CREATE TABLE Users(user_id integer PRIMARY KEY, name text, sounds_played integer, added_at integer, last_played integer)")

    # Creates table if Guilds doesn't exist
    if 'Guilds' not in tables:
        print("Table Guilds not found, creating one.")
        conn_cursor.execute("CREATE TABLE Guilds(guild_id integer PRIMARY KEY,  sounds_played integer, added_at integer, last_played integer)")

    # Get current commands
    conn_cursor.execute("SELECT name from Sounds")
    sql_commands = [c[0] for c in conn_cursor.fetchall()]

    # Add new commands if found
    seconds = time.time()
    for command in COMMAND_LIST + ['code']:
        if command not in sql_commands:
            print("Adding command: " + command)
            conn_cursor.execute("INSERT INTO Sounds(name, times_played, added_at, last_played) VALUES('" + command + "', 0, " + str(int(seconds)) + ", 0)")
    
    conn.commit()
    conn.close()

def db_get_song_stats(commandname):
    """
    Returns all database information (except ID) of a specific command.
    If the command is not found, nothing is returned, so it may cause an IndexError somewhere else.

    Ironic example of `db_get_song_stats('triple')`

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

def db_get_user_stats(user_id):
    """
    Returns all database information of a specific user.
    If the command is not found, `None` is returned, so it may cause an IndexError somewhere else.

    Ironic example of `db_get_user_stats(23592385987235239)`

    `[23592385987235239, 10, 94385734, 18907465]`

    Remember that timestamps are on Epoch seconds.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    conn_cursor = conn.cursor()

    # db request
    conn_cursor.execute("SELECT user_id, sounds_played, added_at, last_played FROM Users WHERE user_id=" + str(user_id) )
    db_output = conn_cursor.fetchall()

    # Close the database connection
    conn.close()

    # Check if user is found
    if len(db_output)==1:

        # Returns that user
        return db_output[0]

    # If user is not found, return None
    return None

def db_get_guild_stats(guild_id):
    """
    Returns all database information of a specific guild.
    If the command is not found, `None` is returned, so it may cause an IndexError somewhere else.

    Ironic example of `db_get_guild_stats(23592385987235239)`

    `[23592385987235239, 10, 94385734, 18907465]`

    Remember that timestamps are on Epoch seconds.
    """
    # Connect to the database
    conn = sqlite3.connect(DB_PATH)
    conn_cursor = conn.cursor()

    # db request
    conn_cursor.execute("SELECT * FROM Guilds WHERE guild_id=" + str(guild_id) )
    db_output = conn_cursor.fetchall()

    # Close the database connection
    conn.close()

    # Check if user is found
    if len(db_output)==1:

        # Returns that user
        return db_output[0]

    # If user is not found, return None
    return None

def db_get_best_users():
    """
    This function returns a list of the 10 users that used the bot. Example:

    `(['royalmo', 29], ['Syndria', 27], ...)`
    """
    # Database settings
    conn = sqlite3.connect(DB_PATH)
    conn_cursor = conn.cursor()

    # Get current commands
    conn_cursor.execute("SELECT name, sounds_played FROM Users ORDER BY sounds_played DESC LIMIT 10")
    response = conn_cursor.fetchall()

    # Close the connection
    conn.close()

    return response

def db_get_best_guilds():
    """
    This function returns a list of the 10 guilds that used the bot. Example:

    `([658587878484, 29], [467846787864784, 27], ...)`
    """
    # Database settings
    conn = sqlite3.connect(DB_PATH)
    conn_cursor = conn.cursor()

    # Get current commands
    conn_cursor.execute("SELECT guild_id, sounds_played FROM Guilds ORDER BY sounds_played DESC LIMIT 10")
    response = conn_cursor.fetchall()

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

def db_sound_played(params, user_id=None, user_name=None, guild_id=None):
    """
    This function is called after every sound is played. It adds on the database the time it has been played and updates the count.

    Comandname sould be a string with the comand. If the command doesn't exist, an IndexError will be thrown.
    """
    # Database settings
    conn = sqlite3.connect(DB_PATH)
    conn_cursor = conn.cursor()

    # If command was a code, we change it
    if type(params) != type(''):
        params = 'code'

    # Get current commands
    conn_cursor.execute("SELECT times_played FROM Sounds WHERE name='" + params + "'")
    times_played = int(conn_cursor.fetchall()[0][0]) + 1

    # Update the command
    conn_cursor.execute("UPDATE Sounds SET times_played=" + str(times_played) + ", last_played=" + str(int(time.time())) + " WHERE name='" + params + "'")

    if user_id != None and user_name != None:
        # Get current user
        conn_cursor.execute("SELECT sounds_played FROM Users WHERE user_id=" + str(user_id) )
        db_output = conn_cursor.fetchall()

        # Check if user exists
        if len(db_output)==1:

            # Adds one to the sound player
            times_user = int(db_output[0][0]) + 1

            # Update current user
            conn_cursor.execute("UPDATE Users SET sounds_played=" + str(times_user) + ", last_played=" + str(int(time.time())) + " WHERE user_id=" + str(user_id))

        else:
            print("User", user_id, "not found in the database. Adding it.")
            # Creates new user with one sound played
            conn_cursor.execute("INSERT INTO Users(user_id, name, sounds_played, added_at, last_played) VALUES(" + str(user_id) + ", '" + user_name + "', 1, " + str(int(time.time())) + ", " + str(int(time.time())) + ")")

    if guild_id != None:
        # Get current guild
        conn_cursor.execute("SELECT sounds_played FROM Guilds WHERE guild_id=" + str(guild_id) )
        db_output = conn_cursor.fetchall()

        # Check if guild exists
        if len(db_output)==1:

            # Adds one to the sound player
            times_guild = int(db_output[0][0]) + 1

            # Update current guild
            conn_cursor.execute("UPDATE Guilds SET sounds_played=" + str(times_guild) + ", last_played=" + str(int(time.time())) + " WHERE guild_id=" + str(guild_id))

        else:
            print("Guild", guild_id, "not found in the database. Adding it.")
            # Creates new guild with one sound played
            conn_cursor.execute("INSERT INTO Guilds(guild_id, sounds_played, added_at, last_played) VALUES(" + str(guild_id) + ", 1, " + str(int(time.time())) + ", " + str(int(time.time())) + ")")

    # Commit changes
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
    This function is called on `!triple fetch` and `!triple fetch restart`.
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
    def __init__(self, token):
        """
        Runs the bot with the given token.
        """
        super().__init__()
        self.run(token)

    async def on_ready(self):
        """
        This function is executed when the bot just connected to Discord.
        """
        # Print info message.
        print(f'Connected to Discord!\n\nBot username: {self.user}\n')

        # Setting Watching status
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="impostors"))

        self.playing_on = []
        self.shutup_at = []
        self.last_code = {}
        self.user_cmds = {}

    def user_new_sound(self, user_id):
        """
        Given a `user_id [int]` and using `self.user_cmds [dict]`, this function will return `True` or `False` depending on if the user can start a sound command or not.

        If return is `True`, a command will be added to the user list.

        Maximum number of messages in every case:
        - 2 sounds every 30 secs.
        - 15 sounds every 10 mins (600 secs).
        - 30 sounds every 30 mins (1800 secs).
        """
        # First, we whitelist the admin xD
        # If this is commented, it's because I am debugging timeouts.
        if int(user_id) in ADMIN_ID:
            return True

        # Gets the time of the request in seconds
        current_time = int(time.time())

        # Then, if we don't find the user in the dict, we add it and we return
        if user_id not in self.user_cmds:
            print("User not in timeout dict. Allowed to play.")
            self.user_cmds[user_id] = [current_time]
            return True

        # If we find it, we get all the timings.
        timings = self.user_cmds[user_id]

        # We remove all sounds that are 1800 seconds older than current time
        # They dont affect timeouts and will save us lots of ram.
        counters = [0, 0, 0]
        limits = [2, 15, 30]
        new_timings = []

        # We do this for each time
        for stime in timings:
            diff  = current_time-stime
            if diff < 1800:
                new_timings.append(stime)
                counters[2] += 1
            if diff < 600:
                counters[1] += 1
            if diff < 30:
                counters[0] += 1

        # Print for debugging
        print("Got counters:", counters, "\nLimits are:", limits)

        # Then we check if the user is in the range
        if max([counters[i]-limits[i] for i in range(len(counters))]) < 0:
            # Update dict and return True
            new_timings.append(current_time)
            self.user_cmds[user_id] = new_timings
            return True

        # Update dict and return False
        self.user_cmds[user_id] = new_timings
        return False

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

    async def play_sound(self, audio_path, voice_channel, guild_id=None):
        """
        This function will play a sound on a voice channel, and will wait for it to stop.

        `voice_channel`: A VoiceChannel object where the bot is connected to.

        `audio_path`: A string with the absolute path of the mp3 file.
        """
        # Print something to log.
        print(" - Playing", audio_path)

        # If we are on Windows, we want to specify the path of ffmpeg.
        if THISOS=="Windows":
                    voice_channel.play(discord.FFmpegPCMAudio(executable=WINDOWS_FFMPEG_PATH, source=audio_path))
        else:
            voice_channel.play(discord.FFmpegPCMAudio(source=audio_path))

        # We wait until we are done.
        while voice_channel.is_playing():
            if guild_id in self.shutup_at:
                voice_channel.stop()
                self.shutup_at.remove(guild_id)
                return True
            else:
                await asyncio.sleep(.1)

        return False

    async def play_code(self, code, voice_channel, times=1, guild_id=None):
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

                    # Play the audio file, and get the return.
                    # If return is true, it means that shutup has been activated.
                    # If not, the bot can continue playing.
                    if await self.play_sound(audiopath, voice_channel,guild_id):
                        return

            if times > 0: #Play 'permitame repetir'
                await self.play_sound(MP3_PERMITAME_PATH, voice_channel)

    async def join_n_leave(self, guild_id, user_id, auth_vc, channel, is_sound, params):
        """
        This function manages all the audio stuff, it has been made so there isn't that many stuff going on and to prevent spaguetti code.

        `guild_id [int]`: The guild the bot is playing to.

        `auth_vc [VoiceChannel]`: The voice channel where to play.

        `channel [TextChannel]`: The text channel where to answer.

        `is_sound [bool]`: Whether if it's a sound or a code. This will depend for `params`. When `is_sound` is...

        - True: `params [string]`: the command to be played
        - False: `params [ code[int], repeat[int] ]`
        """
        # Only play music if user is in a voice channel and bot is not already in a vc on the same guild
        if auth_vc != None and guild_id not in self.playing_on:

            # Adding guild id into list of guilds in use and connecting to vc.
            self.playing_on.append(guild_id)
            vc = await auth_vc.channel.connect()
            print("Joined a VC on guild id", guild_id)
            
            # Playing sound of code depending of is_sound
            if is_sound:
                # Getting file path and playing.
                audiopath = PYPATH + 'sounds/' + params + '_sound.mp3'
                await self.play_sound(audiopath, vc, guild_id)

            else:
                # If params is none, it means that cmd is !repetir
                if params[0]==None:
                    params[0] = self.last_code[str(guild_id)]
                await self.play_code(params[0], vc, params[1], guild_id)

            # Adding to database for stats.
            username = self.get_user(user_id)
            if username != None:
                username = username.name
            db_sound_played(params, user_id, username, guild_id)

            # Disconnecting of vc and removing guild id from the list.
            await vc.disconnect()
            self.playing_on.remove(guild_id)
            print("Left a VC on guild id", guild_id)

        # Sending user error messages if needed.
        elif guild_id in self.playing_on:
            await self.send_to_ch(channel, 'I\'m already playing a sound!', 5)

        else:
            await self.send_to_ch(channel, 'User is not in a channel.', 5)


    async def on_message(self, message):
        """
        This function is executed everytime a message is received from anyone and from any channel.
        """

        # Checks if message isn't from the bot itself and it is plain text. 
        if message.author == self.user or message.type != discord.MessageType.default or len(message.content)<2:
            return

        # As all the commands use ! at the beggining, we can forget about all the other messages.
        if message.content[0] != '!':
            return

        # Defining some temp constants
        content = message.content.lower()[1:]
        channel = message.channel
        auth_id = message.author.id
        auth_vc = message.author.voice
        guild_id = message.guild.id
        mentions = message.mentions

        # Pring for degugging
        print("Got message candidate:", content, "from user id:", auth_id, "at:", time.ctime())

        # Now that we have all the things, we can remove the message:
        # We don't remove it in code commands as we want to see them on chat.
        if content.split()[0] in COMMAND_LIST:
            await message.delete()
            msg_got_deleted = True
        else:
            msg_got_deleted = False

        # Single commands: !triple help
        if content in ['triple help', 'triple help keep']:
            await self.send_to_ch(channel, HELP_TEXT, None if 'keep' in content else 25)
            return

        # Reloads commands, databases and the help menu
        if content == "triple reload":
            fetch_repo(download=False)
            await self.send_to_ch(channel, 'Reloaded successfully!', 5)
            return

        # Single commands: !triple fetch (restart is for admin only)
        if content in ["triple fetch", "triple fetch restart"]:
            # Fetch and pull from repository
            fetch_repo()

            # Shows a message
            await self.send_to_ch(channel, 'Fetched!' + ('\nRestarting...' if 'restart' in content else ''), 5)

            # Restart if requester is admin.
            if 'restart' in content:
                if auth_id in ADMIN_ID:

                    await self.close() # Close the Discord connection
                    # Restarts the python application
                    execv(executable, [executable, __file__] + [argv[0], 'fast'])

                else:
                    await self.send_to_ch(channel, 'Can\'t restart!\nNo permmissions.', 5)
            return

        # Triple ranks: shows top 10 audios
        if content == "triple ranks":

            # Checking database
            db_response = db_get_most_times_played()
            print("DB response:", db_response)

            # Sending response
            await self.send_to_ch(channel, '**TripleBot Ranks** - *Top 10 sounds.*\n' + ''.join(['\n**{0}**: has been played {1} times.'.format(command.upper(), times) for command, times in db_response]), 15)
            return

        if content == "triple ranks users":

            # Checking database
            db_response = db_get_best_users()
            print("DB response:", db_response)

            # Sending response
            await self.send_to_ch(channel, '**TripleBot Ranks** - *Top 10 users.*\n' + ''.join(['\n**{0}**: has played {1} sounds.'.format( user_name, times) for user_name, times in db_response]), 15)
            return

        # Triple stop (admin only). Stops the bot
        if content == 'triple stop' and auth_id in ADMIN_ID:

            await self.send_to_ch(channel, "Stopping bot...", 2)
            await self.close() # Close the Discord connection
            return

        # Triple calla. Stops any sound and leaves voice_channels
        if content == 'triple calla':
            if guild_id in self.playing_on:
                self.shutup_at.append(guild_id)
                await self.send_to_ch(channel, "Nooo please! Why have you done that, {0}?".format(self.get_user(auth_id).mention), 5)
            else:
                await self.send_to_ch(channel, "I'm already quiet u bastard", 5)
            return

        # Triple guilds (admin only): shows all guilds the bot is in.
        if content == "triple guilds" and auth_id in ADMIN_ID:

            # Shows response
            await self.send_to_ch(channel, "**GUILDS WHERE I AM:**" + ''.join(['\n{0} - *Id: {1}*'.format(cguild.name, cguild.id) for cguild in self.guilds] ), 15)
            return

        # Triple guilds (admin only): shows all guilds the bot is in.
        if content == "triple guilds this" and auth_id in ADMIN_ID:

            # Check database
            db_response = db_get_guild_stats(guild_id)
            print("DB response:", db_response)

            if db_response != None:
                # Guild found in database
                await self.send_to_ch(channel, "**STATS FOR {0}**\n\nThis guild has played {1} sounds.\nGuild in database since {2}.\nLast sound played at {3}.".format(self.get_guild(guild_id).name, db_response[1], time.ctime(int(db_response[2])), time.ctime(int(db_response[3]))), 15)

            else:
                # Guild not found in database
                await self.send_to_ch(channel, "Guild {0} not found in our database.\nThis means that this guild hasn't played any sound with TripleBot.".format(self.get_guild(guild_id).name), 5)

            return

        # Triple guilds (admin only): shows all guilds the bot is in.
        if content == "triple guilds ranks" and auth_id in ADMIN_ID:

            # Checking database
            db_response = db_get_best_guilds()
            print("DB response:", db_response)

            # Sending response
            await self.send_to_ch(channel, '**TripleBot Ranks** - *Top 10 guilds.*\n' + ''.join(['\n**{0}**: has played {1} sounds.'.format(self.get_guild(command).name, times) for command, times in db_response]), 15)
            return

        # Triple stats [command]: shows all information of a sound
        if len(content)>13:
            if content[:13] == 'triple stats ' and content[13:] in COMMAND_LIST:

                # Checks database
                db_response = db_get_song_stats(content.split()[2])
                print("DB response:", db_response)

                # Sends response
                await self.send_to_ch(channel, '**TripleBot Command Stats**: *{0}*\nHas been played {1} times.\nTripleBot is keeping track of this sound since *{2}*\nLast time played: *{3}*'.format(db_response[0], db_response[1], time.ctime(int(db_response[2])), time.ctime(int(db_response[3])) if int(db_response[3]) != 0 else "Hasn't been played yet."  ), 15 )

                return

        # Triple stats and triple stats [user]: shows all info about that person.
        if len(content) >= 12:
            if content[:12] == 'triple stats':
                
                # Depending of a !triple stats or !triple stats @someone,
                # We have to get the mention and the id differently.
                if len(mentions) != 0:
                    stats_id = mentions[0].id
                    mentionstr = mentions[0].mention
                else:
                    stats_id = auth_id
                    mentionstr = self.get_user(auth_id).mention

                # Check database
                db_response = db_get_user_stats(stats_id)
                print("DB response:", db_response)

                if db_response != None:
                    # User found in database
                    await self.send_to_ch(channel, "**STATS FOR {0}**\n\nThis user has played {1} sounds.\nUser in database since {2}.\nLast sound played at {3}.".format(mentionstr, db_response[1], time.ctime(int(db_response[2])), time.ctime(int(db_response[3]))), 15)

                else:
                    # User not found in database
                    await self.send_to_ch(channel, "User {0} not found in our database.\nThis means that this user hasn't played any sound with TripleBot.".format(mentionstr), 5)

                return

        # FROM NOW ON MUSIC WILL BE PLAYED
        # So we need to check if the user
        # First we will return all commands that don't make sounds
        if not( "cod" in content or content in COMMAND_LIST):
            return

        # Then we can check if the user can play a sound.
        if not self.user_new_sound(str(auth_id)):
            await self.send_to_ch(channel, "Slow down dude, ur on cooldown!", 5)
            return # if not we return

        # Sound commands
        if content in COMMAND_LIST:
            await self.join_n_leave(guild_id, auth_id, auth_vc, channel, is_sound=True, params=content)
            return

        # Code commands
        if len(content) > 5:
            if content[:5] in ["codi ", "code "]:
                splitted = content.split()

                if len(splitted) not in [2, 3]:
                    return

                # Checking if number is valid and setting it
                if len(splitted) == 3:
                    if splitted[2] in ["1", "2", "3", "4", "5"]:
                        times = int(splitted[2])
                    else:
                        await self.send_to_ch( channel, splitted[2] + " is not a number between 1 and 5.", 5 )
                        return
                else:
                    times = 1

                # Saying code
                await self.join_n_leave(guild_id, auth_id, auth_vc, channel, is_sound=False, params=[splitted[1], times])
                return

        # !repetir last code.
        if content == "repetir":
            if str(guild_id) in self.last_code:
                await self.join_n_leave(guild_id, auth_id, auth_vc, channel, is_sound=False, params=[None, 1])

            else:
                await self.send_to_ch(channel, 'I don\'t have anything to repeat!', 5)
            return

        await self.send_to_ch(channel, 'Command not found, try another.', 5)


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
        if "fast" not in argv:
            print("Sleeping 30 secs. If you type 'fast' after the .py, this step will be skipped.")
            sleep(30)

    # Starting the bot
    mainbot = TripleBot(DISCORD_TOKEN)
