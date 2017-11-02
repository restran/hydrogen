import sys
import os
from setuptools import setup
from settings import APP_NAME, VERSION


def tree(src):
    file_list = []
    for (root, dirs, files) in os.walk(os.path.normpath(src)):
        for f in files:
            f = os.path.join(root, f)
            if not f.endswith('.DS_Store'):
                file_list.append(f)

    return file_list


ENTRY_POINT = ['main.py']

DATA_FILES = []

OPTIONS = {
    'argv_emulation': True,
    'strip': True,
    'resources': ['static', 'templates'],
    'iconfile': 'assets/icon.icns',
    'includes': ['WebKit', 'Foundation', 'webview'],
    'packages': [
        'jinja2'
    ],
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Restran",
        'CFBundleIdentifier': "net.restran.mac.%s" % APP_NAME.lower(),
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
        'NSHumanReadableCopyright': "Copyright © 2017, Restran, All Rights Reserved"
    }
}

setup(
    app=ENTRY_POINT,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
