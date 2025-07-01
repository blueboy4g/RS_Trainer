import os
import shutil
import stat

def create_mac_app_bundle(app_name, executable_path, bundle_identifier, version="1.0"):
    """
    Creates a minimal .app bundle structure for a given executable.

    Args:
      app_name (str): Name of your app (e.g., "RS Trainer")
      executable_path (str): Path to your Unix executable
      bundle_identifier (str): Bundle identifier, e.g., "com.yourcompany.rstrainer"
      version (str): App version string
    """
    app_dir = f"{app_name}.app"
    contents_dir = os.path.join(app_dir, "Contents")
    macos_dir = os.path.join(contents_dir, "MacOS")
    resources_dir = os.path.join(contents_dir, "Resources")

    # Create directories
    os.makedirs(macos_dir, exist_ok=True)
    os.makedirs(resources_dir, exist_ok=True)  # can add icons here later if you want

    # Copy executable into MacOS folder
    dest_executable = os.path.join(macos_dir, app_name.replace(" ", "_"))
    shutil.copy2(executable_path, dest_executable)

    # Make sure it's executable
    st = os.stat(dest_executable)
    os.chmod(dest_executable, st.st_mode | stat.S_IEXEC)

    # Write minimal Info.plist
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
 <dict>
   <key>CFBundleName</key>
   <string>{app_name}</string>
   <key>CFBundleDisplayName</key>
   <string>{app_name}</string>
   <key>CFBundleIdentifier</key>
   <string>{bundle_identifier}</string>
   <key>CFBundleVersion</key>
   <string>{version}</string>
   <key>CFBundleExecutable</key>
   <string>{app_name.replace(" ", "_")}</string>
   <key>CFBundlePackageType</key>
   <string>APPL</string>
   <key>LSMinimumSystemVersion</key>
   <string>10.12.0</string>
 </dict>
</plist>
"""

    plist_path = os.path.join(contents_dir, "Info.plist")
    with open(plist_path, "w") as f:
        f.write(plist_content)

    print(f"{app_dir} created successfully!")

# Example usage:
create_mac_app_bundle(
    app_name="RS Trainer",
    executable_path="dist/main/main",  # path to your Unix executable
    bundle_identifier="com.yourcompany.rstrainer",
    version="1.0"
)
