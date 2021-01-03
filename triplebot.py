# TO BE RUNNED ON PYTHON3.8
# MADE BY ERIC ROY (github/royalmo)

# Read README.md first, and be sure to enter your TOKEN and GUILD ID

# Importing stuff
import json
import discord
import asyncio
from pathlib import Path
from time import sleep

PYPATH = str(Path(__file__).parent.absolute()) + "/"
COMMAND_LIST = ['!triple', '!letsgo', '!gay']

class TskBot(discord.Client):
    async def on_ready(self):
        # Print info message.
        print(f'Connected to Discord!\n\nBot username: {self.user}\n')

        # Setting Watching status
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="impostors"))

        self.is_playing = False

    async def on_message(self, message):

        # Checks if message isn't from the bot itself and it is plain text. 
        if message.author == self.user or message.type != discord.MessageType.default:
            return

        if message.content in COMMAND_LIST:

            voice_channel = message.author.voice.channel

            # Only play music if user is in a voice channel
            if voice_channel!= None and not self.is_playing:

                # Set playing status
                self.is_playing = True

                # Create StreamPlayer
                vc = await voice_channel.connect()

                # Play the audio file
                vc.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source='sounds/'+message.content[1:]+'_sound.mp3'))

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

if __name__ == "__main__":

    # Welcome message
    print("*"*55 + "\n" + " "*11 + "TSK BOT - Discord server manager\n" + "*"*55 + "\n\nLoading settings and connecting to Discord...")

    # Loads settings
    with open(PYPATH + 'bot_settings_2.json', 'r') as json_token:
        filein = json.loads(json_token.read())
        DISCORD_TOKEN = filein['token']
        # DISCORD_GUILD = filein['guild']

    # Runs bot after 30 seconds of delay. Why we do this? Because when raspi boots, network is ready some seconds after rc.local is executed, so if we don't wait the program crashes.
    # sleep(30)

    # Starting the bot
    mainbot = TskBot()
    mainbot.run(DISCORD_TOKEN)