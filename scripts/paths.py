from libraries.sqllite import Database
import os
import re


def edit_path_windows_other(path: str) -> str:
    """
    :param path:  Directory path
    :return: If it is Windows, it remains unchanged, in other systems / it is added to the first path
    """
    if os.name != 'nt':
        path = '/' + path
    return path


def list_file(format_file, path):
    """
    :param format_file: The desired file format, for example mp4
    :param path: The desired folder path
    :return: Returns a list of files related to the imported format
    """
    files = []
    path = edit_path_windows_other(path)
    for i in format_file:
        for name in os.listdir(path):
            if re.match(rf'.*\.{i}', name):
                files.append(os.path.join(path, name))
    return files


def list_folders(path):
    """
    :param path: The desired folder path
    :return: Returns a list of all the folders in the path
    """
    return [x[0] for x in os.walk(path)]


def list_dir():
    """
    :return: Returns the list of folders stored in the database
    """
    database = Database()
    dirc = eval(database.get_data()[0])
    return dirc


def check_dir(path):
    """
    Check if the file is available through the page
    :param path: The requested file path on the page
    :return: Returns true if the file path is in the database, otherwise false
    """
    dircs = list_dir()
    status = False
    if '.' in path:
        path = path.split('/')
        del path[-1]
        path = "/".join(path)
    if path in dircs:
        status = True
    return status