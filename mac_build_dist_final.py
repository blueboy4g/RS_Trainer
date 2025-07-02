from setuptools import setup

#Run this!!! ->    rm -rf build dist/Azulyn.app
#                  arch -x86_64 python mac_build_dist_final.py py2app
# Test app         dist/Azulyn.app/Contents/MacOS/Azulyn


# When ready to covert for M1s do this to to force intel arch:

# lipo "dist/Azulyn.app/Contents/MacOS/Azulyn" \
#   -remove arm64 \
#   -output "dist/Azulyn.app/Contents/MacOS/Azulyn_x86"

# mv "dist/Azulyn.app/Contents/MacOS/Azulyn_x86" "dist/Azulyn.app/Contents/MacOS/Azulyn"

# Get all the paths of stuff thats not intel
# find dist/Azulyn.app -type f -perm +111 -exec file {} \; | grep 'Mach-O universal binary'

# add those paths to something like what I have below
# lipo <path> -remove arm64 -output <path>_x86 && mv <path>_x86 <path>
#
# lipo dist/Azulyn.app/Contents/MacOS/Azulyn -remove arm64 -output dist/Azulyn.app/Contents/MacOS/Azulyn_x86 && mv dist/Azulyn.app/Contents/MacOS/Azulyn_x86 dist/Azulyn.app/Contents/MacOS/Azulyn
# lipo dist/Azulyn.app/Contents/MacOS/python -remove arm64 -output dist/Azulyn.app/Contents/MacOS/python_x86 && mv dist/Azulyn.app/Contents/MacOS/python_x86 dist/Azulyn.app/Contents/MacOS/python

# hold option right click finder and restart
# the app type should now be intel (might take some time or you have to open it)

# create-dmg 'dist/Azulyn.app' \
#   --overwrite \
#   --dmg-title='Azulyn' \
#   --app-drop-link \
#   --quit-app-before-install \
#   --identity="" \
#   --dmg-path=dist/installer/Azulyn_0.7.0.dmg


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
        'CFBundleName': 'Azulyn',
        'CFBundleDisplayName': 'Azulyn',
        'CFBundleIdentifier': 'com.grant.rstrainer',
        'CFBundleVersion': '0.7.0',
        'CFBundleShortVersionString': '7.0',
    },

    'iconfile': 'resources/azulyn_icon.png',  # optional
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
