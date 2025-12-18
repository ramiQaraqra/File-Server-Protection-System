import clamd
import os
import sys
from logger import log

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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        log("Usage: python scanner.py <path_to_file>")
        sys.exit(1)
    file_to_scan = sys.argv[1]
    log(f"Scanning file: {file_to_scan}...")
    result = scan_file(file_to_scan)
    log(f"Scan Result: {result}")
    if result.startswith("Infected"):
        sys.exit(2)
    elif result.startswith("Clean"):
        sys.exit(0)
    else:
        sys.exit(1)