import clamd
import os
import sys
import logger

CLAMD_HOST = '127.0.0.1'
CLAMD_PORT = 3310

def scan_file(file_path):
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    try:
        cd = clamd.ClamdNetworkSocket(CLAMD_HOST, CLAMD_PORT)
        scan_result = cd.scan(file_path)
        print(scan_result[file_path])
        if scan_result[file_path][0] == 'OK':
            return "Clean"
        elif scan_result[file_path][0] == 'FOUND':
            threat_name = scan_result[file_path][1]
            return f"Infected ({threat_name})"
        else:
            return f"Error: {scan_result[file_path][0]}"
    except clamd.ClamdError as e: 
        return f"Error: Couldnt connect to ClamAV service at {CLAMD_HOST}:{CLAMD_PORT}. Is clamd running? Details: {e}"
    except Exception as e:
        return f"Unexpected Error: {e}"

