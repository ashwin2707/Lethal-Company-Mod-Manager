import requests
import zipfile
from io import BytesIO
import os
import json
import shutil
import glob

base_url = 'https://thunderstore.io/package/download/'
temp_dir = './temp'
plugin_dir = os.path.join(temp_dir, './BepInEx/plugins')
config_dir = os.path.join(temp_dir, './BepInEx/config')

def download_and_extract_zip(dependencyString):
    response = requests.get(base_url + dependencyString.replace('-', '/'))
    if response.status_code == 200:
        with zipfile.ZipFile(BytesIO(response.content), 'r') as zip_ref:
            zip_ref.extractall(os.path.join(temp_dir, dependencyString))
        print(f'Extracted: {dependencyString}')
    else:
        print(f'Failed to extract: {dependencyString}')
        print(f'Status code: {response.status_code}')


def main():
    # Load json mod data
    with open('./Mods.json', 'r') as f:
        mods = json.loads(f.read())
    
    # Work inside a temp folder
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    # Extract the BepInEx folder and other stuff
    download_and_extract_zip(mods[0]['dependencyString'])
    for dir in glob.glob(
        os.path.join(temp_dir, mods[0]['dependencyString'], mods[0]["plugins"][0])
    ):
        shutil.move(dir, temp_dir)
    shutil.rmtree(os.path.join(temp_dir, mods[0]['dependencyString']))

    # Add plugins/config folder
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    # Start downloading and injecting mods
    mods = mods[1:]
    for mod in mods:
        download_and_extract_zip(mod['dependencyString'])
        for plugin_path in mod["plugins"]:
            for path in glob.glob(os.path.join(temp_dir, mod['dependencyString'], plugin_path)):
                shutil.move(path, plugin_dir)
        for config_path in mod['config']:
            for path in glob.glob(os.path.join(temp_dir, mod['dependencyString'], config_path)):
                shutil.move(path, config_dir)
        shutil.rmtree(os.path.join(temp_dir, mod['dependencyString']))
main()