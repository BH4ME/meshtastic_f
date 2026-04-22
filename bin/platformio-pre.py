#!/usr/bin/env python3
# trunk-ignore-all(ruff/F821)
# trunk-ignore-all(flake8/F821): For SConstruct imports
import sys
import subprocess
from pathlib import Path

Import("env")
platform = env.PioPlatform()

if platform.name == "native":
    env.Replace(PROGNAME="meshtasticd")
else:
    from readprops import readProps
    prefsLoc = env["PROJECT_DIR"] + "/version.properties"
    verObj = readProps(prefsLoc)
    env.Replace(PROGNAME=f"firmware-{env.get('PIOENV')}-{verObj['long']}")
    env.Replace(ESP32_FS_IMAGE_NAME=f"littlefs-{env.get('PIOENV')}-{verObj['long']}")

# Print the new program name for verification
print(f"PROGNAME: {env.get('PROGNAME')}")
if platform.name == "espressif32":
    print(f"ESP32_FS_IMAGE_NAME: {env.get('ESP32_FS_IMAGE_NAME')}")

    # Keep ESP32 LittleFS contents in sync with either a local web checkout or the
    # pinned release bundle before PlatformIO decides what needs rebuilding.
    web_sync_script = Path(env["PROJECT_DIR"]) / "bin" / "web_ui_sync.py"
    subprocess.run([sys.executable, str(web_sync_script), "--project-dir", env["PROJECT_DIR"]], check=True)
