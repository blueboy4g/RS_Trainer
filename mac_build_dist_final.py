from setuptools import setup

#Run this!!! ->    rm -rf build dist
#                  python mac_build_dist_final.py py2app
#                  dist/main.app/Contents/MacOS/main

APP = ['main.py']

OPTIONS = {
    'argv_emulation': True,
    'includes': [
        'tkinter',
        'requests',
        'PyObjCTools',
        'charset_normalizer',  # or chardet
        'pynput',
        'charset_normalizer',
        'pygame',
        'pynput.keyboard',
        'pynput.keyboard._darwin',
    ],    'packages': ['pynput'],
    'resources': [
        'resources/azulyn_icon.png',  # icon or images (non-code)
        'boss_rotations',             # data folder (like JSONs)
        'config',
        'scripts',
        'ability_icons',
    ],
    'frameworks': [
        '/Library/Frameworks/Python.framework/Versions/3.11/lib/libtcl8.6.dylib',
        '/Library/Frameworks/Python.framework/Versions/3.11/lib/libtk8.6.dylib',
    ],
    'plist': {
        'CFBundleName': 'RS_Trainer',
        'CFBundleDisplayName': 'RS_Trainer',
        'CFBundleIdentifier': 'com.grant.rstrainer',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0',
    },

    'iconfile': 'resources/azulyn_icon.png',  # optional
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
