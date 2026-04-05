import os
import subprocess

if os.name == "nt":
    STARTUPINFO_DEFAULT = subprocess.STARTUPINFO()  # type: ignore
    STARTUPINFO_DEFAULT.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore
else:
    STARTUPINFO_DEFAULT = None  # type: ignore
