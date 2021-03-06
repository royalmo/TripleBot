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
NORMALIZE_TO = -20.0

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
    try:
        json_converted['cmds'].append(sound)
    except:
        print('Json error when decoding our generated string.')

    # We try to generate it ourselves
    if lines[-1] != '}': # Some nano bug
        del lines[-1]
    # The big stuff.
    our_final = '\n'.join(lines[:-3] + [lines[-3]+',', f'        "{sound}"'] + lines[-2:])
    our_final_loaded = loads(our_final)

    with open(BOT_SETTINGS_JSON, 'w') as fout:
        # Checking if they are the same and updating.
        if json_converted==our_final_loaded:
            fout.write(our_final)
        else:
            print('Switching to bullshit json...')
            fout.write(dumps(json_converted))

def rm_from_json(sound):
    """
    This func removes a sound from the list of sounds
    in BOT_SETTINGS_JSON .
    First it tries to do it "nicely", but if it doesn't work,
    it will do it in a forced way.

    Returns -1 if the sound isn't found.
    """
    with open(BOT_SETTINGS_JSON, 'r') as fin:
        # Getting the text
        text = fin.read()

    lines = text.split('\n')

    # We generate what we would like to see.
    json_converted = loads(text)

    # But before that, we make sure sound is in cmds.
    if sound not in json_converted['cmds']:
        return -1

    # Now we can do it safely
    json_converted['cmds'].remove(sound)

    # We try to generate it ourselves. We have to cases:
    # First, when the sound has a ',' at the end.
    if f'        "{sound}",' in lines:
        lines.remove(f'        "{sound}",')
    elif f'        "{sound}"' in lines:
        # In this case, we have to remove also the last comma
        # of the previous element, so we could check for the position as
        # it will always be the -3
        lines = lines[:-4] + [lines[-4][:-1]] + lines[-2:]

    # We generate the textfile again.
    our_final = '\n'.join(lines)

    with open(BOT_SETTINGS_JSON, 'w') as fout:
        # Checking if they are the same and updating.
        if json_converted==loads(our_final):
            fout.write(our_final)
        else:
            fout.write(dumps(json_converted))

def download_mp3_yt(yt_link, dest_folder, dest_file, starttrim, endtrim):
    """
    Downloads and saves an mp3 of that yt video.
    dest_file doesn't need to have the '.mp3' extension.
    """
    # Removing mp3 extension if it has any.
    if dest_file[-4:]=='.mp3':
        dest_file = dest_file[:-4]
    
    print("Creating yt instance for", yt_link, "...")
    # We do this try/except to make sure we can handle video not found err.
    try:
        yt = YouTube(yt_link)
    except Exception as e:
        print(e)
        return -1

    # Looking for streams and downloading
    print("Looking for streams and downloading")
    stream = yt.streams.filter(only_audio=True).first()
    fileout = stream.download(output_path=dest_folder, filename=dest_file)

    # Converting to .mp3 using ffmpeg
    # We could just change the file exstension but
    # we want to make sure that the file has the correct headers.
    print("Converting to .mp3 using ffmpeg.")
    subp_run([
        'ffmpeg', '-y',
        '-i', os.path.join(dest_folder, dest_file+'.mp4'),
        os.path.join(dest_folder, dest_file+'.mp3')
    ])

    # Removing old mp4 file
    print("Removing mp4 temp file")
    os.remove(fileout)

    # Triming and normalizing
    print("Trimming and normalising")
    endfile = dest_folder+ dest_file+'.mp3'
    trim_norm_mp3(endfile, starttrim, endtrim)

    return 0

def trim_norm_mp3(filepath, start=0, end=5000, norm_to=NORMALIZE_TO):
    """
    Trims an mp3 file to it start and end.
    After trimming, it normalizes the audio to treshhold.
    Default values are for getting the first 10 seconds of the clip.
    If end is > than len(audio), all audio is returned.
    """
    # Get file info
    print("Loading sound for trimming and normalising.")
    sound = AudioSegment.from_mp3(filepath)
    # len() and slicing are in milliseconds
    sound_lenght = len(sound)

    # Making sure start is in range
    if start<0 or start>sound_lenght or start>=end:
        start = 0

    # Making sure end is in range
    if end<=start or end>sound_lenght:
        end = sound_lenght

    # Trimming
    print(f"Trimming {filepath} to {start}:{end}")
    trimmed = sound[start:end]

    # Normalizing
    change_in_dBFS = norm_to - trimmed.dBFS
    print("Sound", filepath, "will be gained with dB:", change_in_dBFS)
    norm_sound = trimmed.apply_gain(change_in_dBFS)

    # Exporting
    norm_sound.export(filepath, format="mp3")

def print_gains():
    """
    For debug and statistics, prints all sounds and their gain.
    At the end it prints the average gain
    """
    # Loads all sounds
    with open(BOT_SETTINGS_JSON) as fin:
        commands = loads(fin.read())['cmds']

    # Gets all gains
    totaldbfs = []
    for onesound in commands:
        current = AudioSegment.from_mp3(PYPATH + 'sounds/{}_sound.mp3'.format(onesound)).dBFS
        totaldbfs.append(current)
        print(onesound, current)

    # Prints average gain
    print('\n')
    print('Average:', sum(totaldbfs)/len(totaldbfs))

def normalise_gains(norm_to=NORMALIZE_TO, add2commit=False):
    """
    Changes all gains to the selected gain.
    """
    # Loads sound list
    with open(BOT_SETTINGS_JSON) as fin:
        commands = loads(fin.read())['cmds']

    # Going to folder
    if add2commit:
        os.system("cd {}".format(PYPATH))

    # Gets all gains
    totaldbfs = []
    for onesound in commands:

        # Loads sound
        current = AudioSegment.from_mp3(PYPATH + 'sounds/{}_sound.mp3'.format(onesound))

        # Calculating gain
        change_in_dBFS = norm_to - current.dBFS
        print("Sound", onesound, "will be gained with dB:", change_in_dBFS)

        # Normalizing and exporting
        norm_sound = current.apply_gain(change_in_dBFS)
        norm_sound.export(PYPATH + 'sounds/{}_sound.mp3'.format(onesound), format="mp3")

        # Adding to git.
        if add2commit:
            os.system("git add sounds/{}_sound.mp3".format(onesound))

    # Commit and push
    if add2commit:
        os.system("git commit -m \"BOT: Auto-commit. Normalized sounds.\" && git push")

def commit_new_sound(sound, replace):
    """
    Makes a commit with the new sound modified.
    If replace is True we don't add bot settings json.
    """
    new_mp3_path = PYPATH + f'/sounds/{sound}_sound.mp3'
    if replace:
        os.system("cd {} && git add {} && git commit -m \"BOT: Auto-commit for new sound: {}\" && git push".format(PYPATH, new_mp3_path, sound))
    else:
        os.system("cd {} && git add {} && git add {} && git commit -m \"BOT: Auto-commit for new sound: {}\" && git push".format(PYPATH, BOT_SETTINGS_JSON, new_mp3_path, sound))

def yt_command(params, replace=False):
    """
    Mannages a new sound command.

    The params is not the entire msg: !triple add PARAMS
    PARAMS must contain a command, a YT link, a start, and an end (in ms).

    Error returns:
    -1: Bad params lenght
    -2: Sound command already exists
    -3: YT video not found or bad link
    """
    # Checks list lenght
    if len(params) != 4:
        return -1

    # Gets all params
    [new_sound, yt_link, starttrim, endtrim] = params
    new_sound = new_sound.lower()

    # Checks new_sound availability
    if not replace:
        with open(BOT_SETTINGS_JSON) as fin:
            commands = loads(fin.read())['cmds']
            if new_sound in commands:
                return -2

    # Checks integers
    try:
        starttrim = int(starttrim)
        endtrim = int(endtrim)
    except ValueError:
        starttrim = -1
        endtrim = -1

    # Checks and downloads YT and trims
    if download_mp3_yt(yt_link, PYPATH+'sounds/', new_sound+'_sound', starttrim, endtrim) == -1:
        return -3

    if not replace: # We change json file only if it's a new sound.
        # If all worked nicely, new sound is added into libraryes
        print(f"Exporting {new_sound} to the json file")
        add_to_json(new_sound)

    # Return 0 and commit if all is OK
    print("Committing changes")
    commit_new_sound(new_sound, replace)
    return 0

def change_gain(sound, gain, commit=False):
    """
    This function will change the gain of a soundtrack and will commit the changes if necessary.

    :param sound: The sound command that will have the gain changed.
    :type sound: str

    :param gain: The amount of gain applied. If negative, the volume is lowered instead of rised.
    :type gain: float

    :param commit: If you want to commit the changes. Default value is False.
    :type commit: bool

    :return: 0 or -1 depending if nothing went wrong (0) or something did (-1).
    :rtype: int
    """
    # Loads sound
    current = AudioSegment.from_mp3(PYPATH + 'sounds/{}_sound.mp3'.format(sound))

    # Calculating gain
    print("Sound", sound, "will be gained with dB:", gain)

    # Normalizing and exporting
    norm_sound = current.apply_gain(gain)
    norm_sound.export(PYPATH + 'sounds/{}_sound.mp3'.format(sound), format="mp3")

    # Commit and push if needed
    if commit:
        os.system(f"cd {PYPATH} && git add sounds/{sound}_sound.mp3 && git commit -m \"BOT: Auto-commit. Changed gain of sound {sound}.\" && git push")

    return 0

# Debugging
if __name__ == "__main__":
    print('Debug')
    # download_mp3_yt('v=-crhchLNdas', PYPATH+'', 'mega', 0, 4000)
    # trim_norm_mp3(PYPATH + 'sounds/gas_sound.mp3', -1, -1)
    print_gains()
    # normalise_gains()
    print('End of debug')
