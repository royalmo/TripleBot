# TO BE RUNNED ON PYTHON3.8
# MADE BY ERIC ROY (github/royalmo)

# This program will add an mp3 sound to the sounds folder and update the json file.
# The sound can come from youtube or from the discord files.
# If it comes from youtube, the lenght can be specified.

from json import loads, dumps
from pytube import YouTube # Run 'pip install pytube'
from pydub import AudioSegment # Run 'pip install pydub'
from subprocess import run as subp_run
import os

from pathlib import Path
PYPATH = str(Path(__file__).parent.absolute()) + "/"
BOT_SETTINGS_JSON = PYPATH + 'bot_settings.json'
NORMALIZE_TO= 0

def add_to_json(sound):
    """
    This func adds a sound at the end of the list of sounds
    in BOT_SETTINGS_JSON .
    First it tries to add it "nicely", but if it doesn't work,
    it will add it in a forced way.
    """
    with open(BOT_SETTINGS_JSON, 'r') as fin:
        # Getting the text
        text = fin.read()

    lines = text.split('\n')

    # We generate what we would like to see.
    json_converted = loads(text)
    json_converted['cmds'].append(sound)

    # We try to generate it ourselves
    our_final = '\n'.join(lines[:-3] + [lines[-3]+',', f'        "{sound}"'] + lines[-2:])

    with open(BOT_SETTINGS_JSON, 'w') as fout:
        # Checking if they are the same and updating.
        if json_converted==loads(our_final):
            fout.write(our_final)
        else:
            fout.write(dumps(json_converted))

def download_mp3_yt(yt_link, dest_folder, dest_file, trim):
    """
    Downloads and saves an mp3 of that yt video.
    dest_file doesn't need to have the '.mp3' extension.
    """
    # Removing mp3 extension if it has any.
    if dest_file[-4:]=='.mp3':
        dest_file = dest_file[:-4]

    try:
        yt = YouTube(yt_link)
    except:
        return -1

    stream = yt.streams.filter(only_audio=True).first()
    fileout = stream.download(output_path=dest_folder, filename=dest_file)

    # Converting to .mp3 using ffmpeg
    # We could just change the file exstension but
    # we want to make sure that the file has the correct headers.
    subp_run([
        'ffmpeg', '-y',
        '-i', os.path.join(dest_folder, dest_file+'.mp4'),
        os.path.join(dest_folder, dest_file+'.mp3')
    ])

    # Removing old mp4 file
    os.remove(fileout)

    endfile = dest_folder+ dest_file+'.mp3'
    trim_norm_mp3(endfile, trim[0], trim[1])

    return 0

def trim_norm_mp3(filepath, start=0, end=5000):
    """
    Trims an mp3 file to it start and end.
    After trimming, it normalizes the audio to treshhold.
    Default values are for getting the first 10 seconds of the clip.
    If end is > than len(audio), all audio is returned.
    """
    # Get file info
    sound = AudioSegment.from_mp3(filepath)
    # len() and slicing are in milliseconds
    sound_lenght = len(sound)

    # Making sure start is in range
    if start<0 or type(start)!=int or start>sound_lenght or start>=end:
        start = 0

    # Making sure end is in range
    if end<=start or type(end)!=int or end>sound_lenght:
        end = sound_lenght

    # Trimming and exporting
    trimmed = sound[start:end]
    trimmed.export(filepath, format="mp3")

# Debugging
if __name__ == "__main__":
    print('Debug')
    # download_mp3_yt('v=-crhchLNdas', PYPATH+'', 'mega', [0, 4000])
    # trim_norm_mp3(PYPATH + 'mega.mp3')
    # print('endd')
