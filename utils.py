import os
import shutil
import time
import subprocess
import logger

#this folder should have permissions set so only Admin can read it.
ISOLATION_FOLDER = "C:/Server_Quarantine"

def isolate_file(infected_file_path, threat_name):
    if not os.path.exists(ISOLATION_FOLDER):
        create_secure_quarantine("C:/Server_Quarantine")

    # We add a timestamp so if multiple uploads occurd at the same time with the same name, we don't overwrite.
    filename = os.path.basename(infected_file_path)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    
    new_name = f"{timestamp}_{filename}.infected"
    destination = os.path.join(ISOLATION_FOLDER, new_name)

    try:
        logger.log(f"!!! MOVING INFECTED FILE TO: {destination}")
        shutil.move(infected_file_path, destination)
        
        warning_note = "Note_about_" + infected_file_path + ".txt"
        with open(warning_note, "w") as f:
            f.write(f"The file '{filename}' was removed by Server Protection.\n")
            f.write(f"Reason: Malware Detected ({threat_name})\n")
            f.write("Contact the Administrator if you believe this is an error.")
            
    except Exception as e:
        logger.log(f"Error isolating file: {e}")


def create_secure_quarantine(path):
    if not os.path.exists(path):
        os.makedirs(path)

    # Set permissions to allow only Admin access
    try:
        subprocess.run(
            ['icacls', path, '/inheritance:r', '/grant:r', 'Administrators:(OI)(CI)F'], 
            check=True, 
            stdout=subprocess.DEVNULL
        )
        logger.log(f" [SECURE] Quarantine locked. Only Admins can access: {path}")
    except Exception as e:
        logger.log(f" [WARNING] Could not set permissions: {e}")