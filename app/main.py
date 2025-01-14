import os
try:
    import sys
    sys.path.append('/'.join(os.path.dirname(sys.modules['__main__'].__file__).split('/')[:-1]))
except:
    pass
import re
from _tkinter import TclError
from tkinter import *
from tkinter import filedialog, messagebox
from urllib.error import URLError
from webbrowser import open_new

from scripts.sqllite import database
from scripts.network import get_ip
from scripts.setting_windows import Setting
from scripts.already_running import SingleInstance
from scripts.paths import add_path_database, write_paths
from server import threading_start, threading_stop
from about import UPDATE_NUMBER
from scripts.check_update import check_last_update

connected_network = False
ip = ''


def icon_window(window):
    """
    :param window: Display window
    :return: Set the icon for the desired window
    """
    try:
        window.iconbitmap(os.path.join(os.path.dirname(__file__), "static/icon/icon.ico"))
    except TclError:
        pass


def check_update():
    """
    This function checks if updates are available
    :return: If an update is available, a window with a download link will be displayed, otherwise your message you are
     using the latest version will be displayed.
    """
    try:
        update = check_last_update()
        if update[0]:
            ask_update = messagebox.askquestion(title="New version available", message=update[1])
            if ask_update == 'yes':
                open_new(update[2])
        else:
            messagebox.showinfo(title="updated", message="You are using the latest version")
    except URLError:
        messagebox.showerror(title="ERROR", message="No connection to the server")


def path_dir():
    """
    This function is called when selecting a new route, Its task is to add new folders to the list of folders and save
    the paths in the database
    :return: Update the list of folders
    """
    directory = filedialog.askdirectory()
    if re.fullmatch(r'.:/', directory):
        messagebox.showwarning(title="WARNING",
                               message="You are not allowed to select a drive, you must select a folder")
    else:
        add_path_database(directory)
        load_data()


def path_clear():
    if messagebox.askyesno('Delete all paths', 'All the paths you have added will be deleted. Are you sure?'):
        database.write_data('', 'paths')
        load_data()


def del_itms():
    """
    :return: Delete a folder path from the folder list
    """
    try:
        list_box.delete(0, 'end')
    except:
        pass


def del_path(*args):
    """
    :return: Function to delete the selected path from the database and the list of folders
    """
    try:
        cs = list_box.curselection()[0]
        paths = database.get_data()[0].split(',')
        del paths[cs]
        write_paths(paths)
        load_data()
    except IndexError:
        pass


def load_data():
    """
    :return: Function to get the path of folders from the database and add them to the list
    """
    try:
        del_itms()
        paths = database.get_data()[0].split(',')
        for i in paths[::-1]:
            list_box.insert(0, i)
    except:
        pass


def _threading_start():
    """
    :return: Function to execute the flask program in the form of threading
    """
    threading_start(_run, _run_ftp)
    button_run["state"] = "disabled"
    button_Selection["state"] = "disabled"
    button_clear["state"] = "disabled"
    list_box["state"] = "disabled"
    button_stop["state"] = "normal"


def _threading_stop():
    """
    :return: Function to stop the flask program as threading
    """
    address_run.place_forget()
    address_run_ftp.place_forget()
    threading_stop()
    button_run["state"] = "normal"
    button_Selection["state"] = "normal"
    button_clear["state"] = "normal"
    list_box["state"] = "normal"
    button_stop["state"] = "disabled"
    load_data()


def _run(port_app):
    """
    :param port_app: Port for the program to run
    :return: Disable different sections of the main window and run the flask program
    """
    global address_run
    if port_app == '80':
        address_app = str(ip)
    else:
        address_app = f"{ip}:{port_app}"
    address_run = Label(root, text=address_app, font=('arial', 10, 'bold'), fg="blue")
    address_run.bind("<Button-1>", lambda e: open_new(f"http://{address_app}"))
    address_run.place(x=165, y=225)


def _run_ftp(data):
    """
    :return: According to the settings of the ftp server, it turns on
    """
    global address_run_ftp
    if data[6] == '0':
        address_run_ftp = 'disable'
        address_run_ftp = Label(root, text=address_run_ftp, font=('arial', 10, 'bold'), fg="blue")
        address_run_ftp.place(x=115, y=250)
    else:
        address_run_ftp = f'Host: {ip}  Port: {data[5]}'
        if data[11] == '0':
            address_run_ftp += '  Login anonymously'
        address_run_ftp = Label(root, text=address_run_ftp, font=('arial', 10, 'bold'), fg="blue")
        address_run_ftp.place(x=115, y=250)


def delete_window():
    """
    :return: Stops or hides the program according to the settings
    """
    if database.get_data()[10] == "0":
        if button_stop["state"] == "disabled":
            root.destroy()
        elif messagebox.askquestion("Quit", "Do you want to quit?\nThis stops the program") == "yes":
            if button_run["state"] == "disabled":
                _threading_stop()
            root.destroy()
    else:
        root.destroy()


def open_setting():
    """
    :return: Open the settings window
    """
    if button_run["state"] == "normal":
        Setting(root, icon_window, database)
    else:
        messagebox.showerror("Error",
                             message="You can not change the settings while running the program. Stop the program first, then try again.")


if __name__ == '__main__':
    try:
        # This feature works in the output file (.exe, ...)
        a_running = SingleInstance()
        if a_running:
            ask = messagebox.askyesno(title='HomeServer is Already running',
                                      message="A version of the program is running, do you want to stop it?")
            if ask:
                for i in a_running:
                    a_running.kill_process(i)
            else:
                raise NameError
        ip = get_ip()
        connected_network = True
    except OSError:
        messagebox.showerror(title="HomeServer ERROR", message="You are not connected to any networks")
    except NameError:
        pass
    if connected_network:
        root = Tk()
        root.title("Home Server")
        root.geometry("500x300")
        root.resizable(False, False)
        root.protocol("WM_DELETE_WINDOW", delete_window)
        menubar = Menu(root)
        # file menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Setting", command=open_setting)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=delete_window)
        menubar.add_cascade(label="File", menu=filemenu)
        # help menu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About developer", command=lambda: open_new('https://MrMRM.ir'))
        helpmenu.add_command(label="Github", command=lambda: open_new('https://github.com/MrMRM1/HomeServer'))
        helpmenu.add_command(label="Donate", command=lambda: open_new('https://MrMRM.ir/donate'))
        helpmenu.add_separator()
        helpmenu.add_command(label="Check Update", command=check_update)
        menubar.add_cascade(label="Help", menu=helpmenu)
        title_list = Label(root, text="List of folders (Double click to delete the item)", font=('arial', 10, 'bold'))
        title_list.place(x=25, y=15)
        button_Selection = Button(root, text="Add folder", font=('arial', 10, 'bold'), command=path_dir)
        button_Selection.place(x=317, y=10)
        button_clear = Button(root, text="Clear", font=('arial', 10, 'bold'), command=path_clear)
        button_clear.place(x=410, y=10)
        list_box = Listbox(root)
        load_data()
        list_box.bind('<Double-Button>', del_path)
        list_box.place(x=25, y=50, width=447, height=170)
        button_run = Button(root, text="Run", font=('arial', 10, 'bold'), command=_threading_start)
        button_run.place(x=418, y=225)
        button_stop = Button(root, text="Stop", font=('arial', 10, 'bold'), command=_threading_stop)
        button_stop["state"] = "disabled"
        button_stop.place(x=362, y=225)
        Label(root, text=f"Enter in the browser:", font=('arial', 10, 'bold')).place(x=25, y=225)
        Label(root, text=f"FTP Server :", font=('arial', 10, 'bold')).place(x=25, y=250)
        icon_window(root)
        root.config(menu=menubar)
        root.mainloop()
