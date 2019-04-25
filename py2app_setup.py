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
    'resources': ['static', 'templates', 'data'],
    'iconfile': 'assets/icon.icns',
    'excludes': [],
    'includes': ['WebKit', 'Foundation', 'webview'],
    'packages': [
        'Cryptodome',  # 需要在这里配置，否则 .so 文件不会导入
        'mountains',
        'openpyxl',  # 有一些数据文件
        '_sysconfigdata_m_darwin_darwin'  # 因为sysconfig是动态导入的，无法识别出来
    ],
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleGetInfoString': "Restran",
        'CFBundleIdentifier': "net.restran.mac.%s" % APP_NAME.lower(),
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
        'NSHumanReadableCopyright': "Copyright © 2019, Restran, All Rights Reserved"
    }
}

setup(
    app=ENTRY_POINT,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
