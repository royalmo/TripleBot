# TO BE RUNNED ON PYTHON3.8
# MADE BY ERIC ROY (github/royalmo)

# This program will add an mp3 sound to the sounds folder and update the json file.
# The sound can come from youtube or from the discord files.
# If it comes from youtube, the lenght can be specified.

from json import loads, dumps

from pathlib import Path
PYPATH = str(Path(__file__).parent.absolute()) + "/"
BOT_SETTINGS_JSON = PYPATH + 'bot_settings.json'

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


# Debugging
if __name__ == "__main__":
    print('Debug')
