import os
import shutil
import subprocess
from pathlib import Path

# ==== CONFIGURATION ====
PYTHON_SCRIPTS = [
    "Main.py",
    "Config.py",
    "Scripts/RS_Trainer.py",
    "Scripts/RS_Overlay.py",
    "Scripts/Rotation_Creation.py",
    "Scripts/Ability.py",
    "Scripts/DialAnimation.py",
]

RESOURCE_FILES = [
    "Config.json",
    "PVM_Discord.txt",
]

RESOURCE_DIRS = [
    "Boss_Rotations",
    "Ability_Icons",
    "Config",
    "Resources",
]

DIST_DIR = Path("dist_final")

# ==== CLEAN UP ====
print("[✓] Cleaning previous build...")
shutil.rmtree(DIST_DIR, ignore_errors=True)
DIST_DIR.mkdir(exist_ok=True)

# ==== BUILD EXEs ====
for script_path in PYTHON_SCRIPTS:
    print(f"[✓] Building {script_path}...")
    icon_path = "resources/azulyn_icon.ico"

    cmd = (
        f'pyinstaller --onefile --noconsole '
        f'--icon="{icon_path}" '
        f'"{script_path}"'
    )
    subprocess.run(cmd, shell=True, check=True)

    # Determine source .exe and destination
    exe_name = Path(script_path).stem + ".exe"
    built_exe = Path("dist") / exe_name
    rel_target_path = Path(script_path).with_suffix(".exe")  # Scripts/RS_Trainer.exe
    final_exe_path = DIST_DIR / rel_target_path

    if built_exe.exists():
        print(f"[✓] Copying {exe_name} to dist_final/{rel_target_path.parent}...")
        final_exe_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(built_exe, final_exe_path)

# ==== COPY EXEs ====
for script in PYTHON_SCRIPTS:
    exe_name = Path(script).stem + ".exe"
    built_exe = Path("dist") / exe_name
    if built_exe.exists():
        print(f"[✓] Copying {exe_name} to final dist...")
        shutil.copy(built_exe, DIST_DIR)

# ==== COPY RESOURCE FILES ====
for file in RESOURCE_FILES:
    if Path(file).exists():
        print(f"[✓] Copying {file} to final dist...")
        shutil.copy(file, DIST_DIR)

# ==== COPY RESOURCE DIRECTORIES ====
for dir_name in RESOURCE_DIRS:
    src_dir = Path(dir_name)
    dst_dir = DIST_DIR / dir_name
    if src_dir.exists():
        print(f"[✓] Copying {dir_name}/ to final dist...")
        shutil.copytree(src_dir, dst_dir)

# ==== CLEAN BUILD TRASH ====
print("[✓] Cleaning PyInstaller temp files...")
shutil.rmtree("build", ignore_errors=True)
shutil.rmtree("dist", ignore_errors=True)
shutil.rmtree("__pycache__", ignore_errors=True)
for spec in Path().glob("*.spec"):
    spec.unlink()

print(f"\n✅ Done! Final dist ready at: {DIST_DIR.resolve()}")
