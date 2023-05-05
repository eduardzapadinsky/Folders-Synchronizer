"""
Program for synchronizing two folders: source and replica.
The program maintains a full, identical copy of the source folder to the replica folder.

"""

import os
import shutil
import sys
import time
from datetime import datetime


def getting_args():
    """
    Parses command-line arguments and returns the source folder, replica folder, sync interval, and log file name.
    Raises:
        IndexError: If there are not enough command-line arguments.
        ValueError: If the third argument is not an integer.
    Returns:
        A tuple containing the parsed values for folder_source, folder_replica, sync_interval, and log_file.

    """
    try:
        folder_source = sys.argv[1]
        folder_replica = sys.argv[2]
        sync_interval = int(sys.argv[3])
        log_file = f"{sys.argv[4]}.log"
        return folder_source, folder_replica, sync_interval, log_file
    except IndexError:
        print("You must enter four arguments. For instance 'python synchronizer.py source replica 10 logfile'")
        sys.exit()
    except ValueError:
        print("The third argument must be an integer number")
        sys.exit()


def log_and_print(log_file, message):
    """
    Appends the given message to the log file and prints it to the console.
    Args:
       log_file: A string representing the log file path.
       message: A string containing the message to be logged and printed.

    """
    with open(log_file, "a") as file:
        file.write(message + "\n")
    print(message)


def copy_files_and_dirs(folder_source, folder_replica, log_file, datetime_format):
    """
    Copies files and directories from the source folder to the replica folder.
    Args:
        folder_source: A string representing the path of the source folder.
        folder_replica: A string representing the path of the replica folder.
        log_file: A string representing the path of the log file.
        datetime_format: A string representing the datetime format for logging.

    """
    for source_root, source_dirs, source_files in os.walk(folder_source):
        folder_source_path = os.path.relpath(source_root, folder_source)
        folder_replica_path = os.path.join(folder_replica, folder_source_path)

        # creating a replica dir if needed
        if not os.path.exists(folder_replica_path):
            os.makedirs(folder_replica_path)

        # creating or updating files
        for source_file in source_files:
            source_file_path = os.path.join(source_root, source_file)
            replica_file_path = os.path.join(folder_replica_path, source_file)

            replica_file_exists = os.path.exists(replica_file_path)
            # creating files
            if not replica_file_exists:
                shutil.copy2(source_file_path, replica_file_path)
                event_datetime = datetime.fromtimestamp(os.stat(source_file_path).st_ctime).strftime(
                    datetime_format)
                message = f"File '{source_file_path}' was created at {event_datetime}"
                log_and_print(log_file, message)
            # updating files
            else:
                replica_file_differs = os.stat(source_file_path).st_mtime != os.stat(replica_file_path).st_mtime
                if replica_file_differs:
                    shutil.copy2(source_file_path, replica_file_path)
                    event_datetime = datetime.fromtimestamp(os.stat(source_file_path).st_mtime).strftime(
                        datetime_format)
                    message = f"File '{source_file_path}' was modified at {event_datetime}"
                    log_and_print(log_file, message)

        # creating or updating dirs
        for source_dir in source_dirs:
            folder_source_path = os.path.join(source_root, source_dir)
            folder_replica_path_inner = os.path.join(folder_replica_path, source_dir)
            if os.path.exists(folder_source_path) and not os.path.exists(folder_replica_path_inner):
                os.makedirs(folder_replica_path_inner)
                event_datetime = datetime.fromtimestamp(os.path.getctime(folder_replica_path_inner)).strftime(
                    datetime_format)
                message = f"Folder '{folder_replica_path_inner}' was created at {event_datetime}"
                log_and_print(log_file, message)


def remove_files_and_dirs(folder_source, folder_replica, log_file, datetime_format):
    """
    Removes files and directories from the replica folder that are not present in the source folder.
    Args:
        folder_source: A string representing the path of the source folder.
        folder_replica: A string representing the path of the replica folder.
        log_file: A string representing the path of the log file.
        datetime_format: A string representing the datetime format for logging.

    """
    for replica_root, replica_dirs, replica_files in os.walk(folder_replica, topdown=False):
        folder_replica_path = os.path.relpath(replica_root, folder_replica)
        folder_source_path = os.path.join(folder_source, folder_replica_path)

        # deleting files
        for replica_file in replica_files:
            replica_file_path = os.path.join(replica_root, replica_file)
            source_file_path = os.path.join(folder_source_path, replica_file)

            if not os.path.exists(source_file_path):
                os.remove(replica_file_path)
                message = f"File '{source_file_path}' was deleted before {datetime.now().strftime(datetime_format)}"
                log_and_print(log_file, message)

        # deleting dirs
        for replica_dir in replica_dirs:
            folder_replica_path = os.path.join(replica_root, replica_dir)
            folder_source_path_inner = os.path.join(folder_source_path, replica_dir)
            if not os.listdir(folder_replica_path) and not os.path.exists(folder_source_path_inner):
                os.rmdir(folder_replica_path)
                message = f"Folder '{folder_replica_path}' was deleted before {datetime.now().strftime(datetime_format)}"
                log_and_print(log_file, message)


def sync_folders():
    """
    Synchronizes the contents of two folders repeatedly at a specified interval.
    The function gets command-line arguments using getting_args() function, creates a folder
    if it doesn't exist and keeps synchronizing source and replica folders using copy_files_and_dirs()
    and remove_files_and_dirs() functions.

    """
    folder_source, folder_replica, sync_interval, log_file = getting_args()
    datetime_format = '%Y-%m-%d %H:%M:%S'

    # creating a source dir if needed
    if not os.path.exists(folder_source):
        os.makedirs(folder_source)

    # synchronization engine
    while True:
        copy_files_and_dirs(folder_source, folder_replica, log_file, datetime_format)
        remove_files_and_dirs(folder_source, folder_replica, log_file, datetime_format)
        time.sleep(sync_interval)


if __name__ == "__main__":
    sync_folders()
