import argparse
import sys
import os

import observer
import logger

PATHS_FILE = "Paths.txt"
CLAMAV_PATH = r"C:\\ClamAV"
# CONFIG_FILE = os.path.join(CLAMAV_PATH, "clamd.conf")
# SAMPLE_FILE = os.path.join(CLAMAV_PATH, "clamd.conf.sample")

BANNER = f"""
{logger.Colors.CYAN}
   █████████     ██████             
  ███░░░░░███  ███░░░░███           
 ███     ░░░  ███    ░░███ ████████ 
░███         ░███     ░███░░███░░███
░███         ░███   ██░███ ░███ ░░░ 
░░███     ███░░███ ░░████  ░███     
 ░░█████████  ░░░██████░██ █████    
  ░░░░░░░░░     ░░░░░░ ░░ ░░░░░     
                                                    
{logger.Colors.ENDC}{logger.Colors.BOLD}CQr [Secure] Protection System v1.0 - Real-Time File Protection{logger.Colors.ENDC}
"""

def get_paths():
    if not os.path.exists(PATHS_FILE):
        return []
    with open(PATHS_FILE, "r") as f:
        # Filter out empty lines and whitespace
        return [line.strip() for line in f if line.strip()]
    
def handle_add(args):

    path_to_add = args.path.strip().strip('"').strip("'")

    if not os.path.exists(path_to_add):
        logger.print_exception(f"[ERR] Directory not found: {path_to_add}")
        return
    
    if not os.path.isdir(path_to_add):
        logger.print_exception(f"[ERR] Target must be a directory, not a file.")
        return

    current_paths = get_paths()
    
    if path_to_add in current_paths:
        logger.print_warning(f"[!] Path is already monitored.")

    else:
        with open(PATHS_FILE, "a") as f:
            f.write(f"{path_to_add}\n")
        logger.print_success(f"[OK] Added to configuration: {path_to_add}")

def handle_configure_info(args):
    if not os.path.exists(CLAMAV_PATH):
        logger.print_exception(f"[ERR] ClamAV folder not found at: {CLAMAV_PATH}")
        logger.print_info("Please install ClamAV from https://www.clamav.net/downloads and try again.")
        return
    logger.print_header("\n=== ClamAV Configuration Guide ===")
    print("To enable the scanner, you must manually create two files")
    print(f"in your ClamAV folder: {logger.Colors.BOLD}{CLAMAV_PATH}{logger.Colors.ENDC}")
    logger.print_info("\n--- Step 1: Create 'clamd.conf' ---")
    print("Create a file named 'clamd.conf' and paste this exact content:")
    logger.print_success("""
TCPSocket 3310
TCPAddr 127.0.0.1""")
    logger.print_info("\n--- Step 2: Create 'freshclam.conf' ---")
    print("Create a file named 'freshclam.conf' and paste this exact content:")
    logger.print_success("""
DatabaseMirror database.clamav.net""")
    logger.print_info("\n--- Step 3: Start the Service ---")
    print(f"1. Go to {CLAMAV_PATH}")
    print("2. Find the file named clamd.exe.")
    print("3. Double-click to start it.")
    
    logger.print_header("\n=== End of Guide ===")

def handle_list(args):
    paths = get_paths()
    logger.print_header(f"\n--- Active Monitor Configuration ---")
    if not paths:
        logger.print_warning("(No paths configured. Use 'add'.)")
    else:
        for idx, p in enumerate(paths, 1):
            print(f"{logger.Colors.BLUE}[{idx}]{logger.Colors.ENDC} {p}")
    logger.print_info("-" * 40)

def handle_help(args):
    print("USAGE:")
    print(f"  {logger.Colors.BOLD}configure_info{logger.Colors.ENDC}  : Show manual setup instructions.")
    print(f"  {logger.Colors.BOLD}add <path>{logger.Colors.ENDC}     : Add directory to monitor list.")
    print(f"  {logger.Colors.BOLD}list{logger.Colors.ENDC}           : Show configured paths.")
    print(f"  {logger.Colors.BOLD}start{logger.Colors.ENDC}          : Launch the protection engine.")

def handle_start(args):
    paths = get_paths()
    if not paths:
        logger.print_warning(f"[WARNING] Configuration is empty. No folders to monitor.")
        

    logger.print_info(f"[*] Initializing Observer Module...")
    logger.print_info(f"[*] Loading {len(paths)} watch targets...")
    
    try:
        observer.start_engine()
    except KeyboardInterrupt:
        pass # Observer handles the shutdown 

def main():
    parser = argparse.ArgumentParser(description="CQr CLI", add_help=False)
    subparsers = parser.add_subparsers(dest='command')

    # COMMAND: add <path>
    p_add = subparsers.add_parser('add')
    p_add.add_argument('path', help="Path to directory")
    p_add.set_defaults(func=handle_add)

    # COMMAND: list
    p_list = subparsers.add_parser('list')
    p_list.set_defaults(func=handle_list)

    # COMMAND: start
    p_start = subparsers.add_parser('start')
    p_start.set_defaults(func=handle_start)

    # COMMAND: help
    p_help = subparsers.add_parser('help')
    p_help.set_defaults(func=handle_help)

    # COMMAND: configure_info
    p_conf = subparsers.add_parser('configure_info')
    p_conf.set_defaults(func=handle_configure_info)

    if len(sys.argv) == 1:
        print(BANNER)
        logger.print_header(f"Use 'help' to see available commands.")
        sys.exit(1)
    
    try:
        args = parser.parse_args()
        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()
    except SystemExit:
        pass

if __name__ == "__main__":
    main()
