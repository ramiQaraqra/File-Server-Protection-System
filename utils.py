import os
import shutil
import time
import subprocess
import logger

# Use raw string for Windows paths to avoid escaping issues
ISOLATION_FOLDER = r"C:\CQr_Quarantine"

def isolate_file(infected_file_path, threat_name):
    # 1. Ensure the secure folder exists and permissions are set
    create_secure_quarantine(ISOLATION_FOLDER)

    filename = os.path.basename(infected_file_path)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    new_name = f"{timestamp}_{filename}.infected"
    destination = os.path.join(ISOLATION_FOLDER, new_name)

    logger.log(f"!!! ATTEMPTING ISOLATION: {infected_file_path} -> {destination}")

    # 2. RETRY LOGIC: Windows often locks files briefly after scanning/downloading.
    # We try moving the file 5 times with a 1-second delay between attempts.
    max_retries = 5
    for attempt in range(max_retries):
        try:
            shutil.move(infected_file_path, destination)
            logger.log(f" [SUCCESS] File isolated on attempt {attempt + 1}")
            
            # Leave the warning note only after successful move
            leave_warning_note(infected_file_path, filename, threat_name)
            return  # Exit function immediately on success

        except PermissionError:
            logger.log(f" [LOCKED] Attempt {attempt + 1}/{max_retries}: File is in use or Access Denied. Retrying...")
            time.sleep(1)  # Wait for the lock to release
        except Exception as e:
            logger.log(f" [ERROR] Critical error moving file: {e}")
            return # Stop trying if it's not a permission error

    logger.log(f" [FAIL] Could not isolate file after {max_retries} attempts. Check Admin privileges.")

def leave_warning_note(original_path, filename, threat_name):
    try:
        folder_path = os.path.dirname(original_path)
        warning_note_path = os.path.join(folder_path, f"Note_about_({filename}).txt")
        with open(warning_note_path, "w") as f:
            f.write(f"The file '{filename}' was removed by the CQr Server Protection.\n")
            f.write(f"Reason: Malware Detected ({threat_name})\n")
            f.write("Contact the Administrator if you believe this is an error.")
    except Exception as e:
        logger.log(f" [WARNING] Could not write warning note: {e}")

def create_secure_quarantine(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            logger.log(f" [ERR] Failed to create quarantine folder: {e}")
            return

    # Force reset permissions every time to ensure security
    # /inheritance:r -> Removes inherited perms from C:\
    # /grant:r -> Grants Admin full control
    try:
        subprocess.run(
            ['icacls', path, '/inheritance:r', '/grant:r', 'Administrators:(OI)(CI)F'], 
            check=True, 
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        # We suppress the error here because it usually fails if you aren't Admin,
        # but we don't want to crash the whole engine over it.
        pass