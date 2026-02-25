"""
Log Manager - Bronze Tier AI Employee

This script prevents log files from growing too large.
It checks log files and archives them if they exceed a size limit.

Features:
- Checks System_Log.md and Logs/watcher_errors.log
- Archives files larger than 1 MB with a timestamp
- Creates fresh empty log files after archiving
- No external dependencies required
"""

import os
from datetime import datetime

# Configuration
# Maximum file size in bytes (1 MB = 1024 * 1024 bytes)
MAX_FILE_SIZE_BYTES = 1 * 1024 * 1024

# Log files to manage
SYSTEM_LOG = "System_Log.md"
WATCHER_ERROR_LOG = os.path.join("Logs", "watcher_errors.log")


def get_file_size(filepath):
    """
    Get the size of a file in bytes.
    
    Args:
        filepath (str): Path to the file.
    
    Returns:
        int: File size in bytes, or 0 if file doesn't exist.
    """
    if os.path.exists(filepath):
        return os.path.getsize(filepath)
    return 0


def archive_log_file(filepath):
    """
    Archive a log file by renaming it with a timestamp.
    
    Creates a backup of the file with a timestamp in the filename,
    then creates a fresh empty file with the original name.
    
    Args:
        filepath (str): Path to the log file to archive.
    
    Returns:
        bool: True if archived successfully, False otherwise.
    """
    try:
        # Check if the file exists before trying to archive
        if not os.path.exists(filepath):
            print(f"File does not exist, skipping: {filepath}")
            return False
        
        # Generate a timestamp for the archive filename
        # Format: YYYY-MM-DD_HH-MM-SS (safe for filenames)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Split the filepath into directory, name, and extension
        directory = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        name, ext = os.path.splitext(filename)
        
        # Create the new archive filename with timestamp
        # Example: System_Log_2026-01-20_14-30-00.md
        archive_filename = f"{name}_{timestamp}{ext}"
        archive_filepath = os.path.join(directory, archive_filename) if directory else archive_filename
        
        # Rename the original file to the archive filename
        os.rename(filepath, archive_filepath)
        print(f"Archived: {filepath} -> {archive_filepath}")
        
        # Create a fresh empty file with the original name
        # For System_Log.md, we add basic structure
        if filepath == SYSTEM_LOG:
            fresh_content = """# System Log

## Activity Log

<!-- Log entries will be added here -->

| Timestamp | Action | Details |
|-----------|--------|---------|
|           |        |         |

"""
        else:
            # For error logs, start with a simple header comment
            fresh_content = f"# Error Log\n# Fresh start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(fresh_content)
        
        print(f"Created fresh log file: {filepath}")
        return True
        
    except Exception as e:
        print(f"Error archiving {filepath}: {e}")
        return False


def check_and_rotate_log(filepath, log_name):
    """
    Check if a log file exceeds the size limit and rotate it if needed.
    
    Args:
        filepath (str): Path to the log file.
        log_name (str): Friendly name for display purposes.
    """
    # Get the current file size
    size_bytes = get_file_size(filepath)
    
    # Convert to megabytes for easier reading (optional, for display)
    size_mb = size_bytes / (1024 * 1024)
    
    # Check if file exceeds the maximum size
    if size_bytes > MAX_FILE_SIZE_BYTES:
        print(f"[{log_name}] Size: {size_mb:.2f} MB - Exceeds limit, archiving...")
        archive_log_file(filepath)
    else:
        print(f"[{log_name}] Size: {size_mb:.2f} MB - OK")


def main():
    """
    Main function that checks all log files and rotates them if needed.
    
    This function:
    1. Checks System_Log.md
    2. Checks Logs/watcher_errors.log
    3. Archives any files that exceed the size limit
    """
    print("=" * 50)
    print("Log Manager - Checking log files")
    print(f"Maximum file size: {MAX_FILE_SIZE_BYTES / (1024 * 1024):.1f} MB")
    print("=" * 50)
    
    # Ensure the Logs folder exists
    os.makedirs("Logs", exist_ok=True)
    
    # Check and rotate System_Log.md
    check_and_rotate_log(SYSTEM_LOG, "System_Log.md")
    
    # Check and rotate watcher_errors.log
    check_and_rotate_log(WATCHER_ERROR_LOG, "Logs/watcher_errors.log")
    
    print("=" * 50)
    print("Log Manager - Check complete")


if __name__ == "__main__":
    main()
