import os
import sys

from datetime import datetime
from dotenv import load_dotenv

def get_time() -> str:
    # Return date in the format of "MM-DD-YYYY HH:MM:SS:MS"
    return datetime.now().strftime("%m-%d-%Y %H:%M:%S:%f")

# Standardizes console output, use whenever possible
def log_info(output:str) -> None:
    print(f"[{get_time()}] [INFO] {output}")

def log_warn(output:str) -> None:
    print(f"[{get_time()}] [WARNING] {output}")

def log_err(output:str) -> None:
    print(f"[{get_time()}] [ERROR] {output}")

def log_fatal(output:str) -> None:
    print(f"[{get_time()}] [FATAL] {output}")
    sys.exit(1)

# Given a relative path, returns its absolute path equivalent, or the absolute path to
# the temp folder created by PyInstaller's bootloader. Necessary if this project is to
# be compiled into a one-file build.
def getResourcePath(rel_path:str) -> str:
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath("./")
    # Returns a Unix-friendly path using only forward slashes
    return os.path.join(base_path, rel_path).replace("\\", "/")


load_dotenv(".env")

TOKEN = os.getenv("token")
PREFIX = os.getenv("prefix")

COG_PATH = "../src/cogs"