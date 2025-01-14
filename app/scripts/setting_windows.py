import os
import platform
from hashlib import sha256
from tkinter import filedialog, messagebox, Label, Button, Entry, ttk, Toplevel, Checkbutton, IntVar, StringVar

from app.ftp.ftp_scripts.filesystems import get_root
from app.admin.scripts.validity_check import check_username, check_password
from app.scripts.network import check_port_bool

if platform.system() != 'Windows':
    import subprocess


def open_path(path: str) -> None:
    """
    a cross-platform file opening
    :param path: file path
    :return: file path opening
    """

    def showerror():
        """
        :return:  Show error This folder does not exist.
        """
        messagebox.showerror(title="File Not Found", message="This folder does not exist.")

    match platform.system():
        case 'Windows':
            try:
                os.startfile(path)
            except FileNotFoundError:
                showerror()
        case 'Darwin':
            try:
                subprocess.Popen(['open', path])
            except FileNotFoundError:
                showerror()
        case _:
            try:
                subprocess.Popen(['xdg-open', path])
            except FileNotFoundError:
                showerror()


def check_port(port: str) -> str:
    def show_error():
        messagebox.showerror('Error enter a valid value', 'The port value must be a number')
    if check_port_bool(port):
        return port
    else:
        show_error()
    return ''


class Setting:
    def __init__(self, root, icon_window, database):
        self.database = database
        self.data = self.database.get_data()
        setting = Toplevel(root)
        setting.title("Setting")
        setting.geometry("600x300")
        setting.resizable(False, False)
        icon_window(setting)

        tab_control = ttk.Notebook(setting)

        self.tab_received = ttk.Frame(tab_control)
        self.tab_control_system_pas = ttk.Frame(tab_control)
        self.tab_ftp_server = ttk.Frame(tab_control)
        self.tab_login_page = ttk.Frame(tab_control)
        self.tab_more = ttk.Frame(tab_control)

        tab_control.add(self.tab_received, text="Received files")
        self._window_received()
        tab_control.add(self.tab_control_system_pas, text="Control system password")
        self._shutdown_sleep()
        tab_control.add(self.tab_ftp_server, text="FTP Server")
        self._ftp_server()
        tab_control.add(self.tab_login_page, text="Login page")
        self.login_page()
        tab_control.add(self.tab_more, text="More")
        self.more()
        tab_control.pack(expand=1, fill="both")

    def _redirect_received(self):
        """
        Saves the upload folder path to the database.
        """
        deiconiry = filedialog.askdirectory()
        if deiconiry not in ['', ()]:
            self.database.write_data(deiconiry, "upload")
            path_upload['text'] = deiconiry
            path_upload.bind("<Button-1>", lambda event, e=deiconiry: open_path(e))

    def _window_received(self):
        """
        settings of received files
        """
        global path_upload
        path_uploads = self.data[3]
        Label(self.tab_received, text="Path of received files: ", font=('arial', 10, 'bold')).place(x=10, y=10)
        path_upload = Label(self.tab_received, text=path_uploads, font=('arial', 10, 'bold'), fg="blue")
        path_upload.bind("<Button-1>", lambda event, e=path_uploads: open_path(e))
        path_upload.place(x=10, y=35)
        Button(self.tab_received, text="Select a folder", font=('arial', 10, 'bold'),
               command=self._redirect_received).place(relx=0.5, rely=0.3, anchor="center")

    def _shutdown_sleep(self):
        """
        Window related to changing the shutdown password and system sleep mode
        """

        def _save_password():
            """
             Function to check the password and confirm the password and save it in the database
            """
            password = password_box.get()
            password_v = password_v_box.get()
            if password != password_v:
                messagebox.showerror(title="ERROR", message="Password and verification password must be the same")
            elif password is not None and check_password(password):
                self.database.write_data(sha256(password.encode()).hexdigest(), "password")
                messagebox.showinfo(title="successful", message="Password set successfully")
            else:
                messagebox.showerror(title="ERROR", message="Enter valid password\nMinimum 8 characters,\nat least one uppercase letter, \none lowercase letter, \none number and one special character (@$!%*?&)'")

        Label(self.tab_control_system_pas, text="Enter password: ", font=('arial', 10, 'bold')).place(x=10, y=10)
        Label(self.tab_control_system_pas, text="Repeat password for verification: ",
              font=('arial', 10, 'bold')).place(x=10, y=60)

        password_box = Entry(self.tab_control_system_pas, font=('arial', 10, 'bold'), show="*")
        password_box.place(x=10, y=35, width=300)
        password_v_box = Entry(self.tab_control_system_pas, font=('arial', 10, 'bold'), show="*")
        password_v_box.place(x=10, y=85, width=300)
        Button(self.tab_control_system_pas, text="Set password", font=('arial', 10, 'bold'),
               command=_save_password).place(x=215, y=130)

    def _ftp_server(self):
        """
         Ftp Server tab settings
        """

        def click_change_ftp_server():
            """
            Enables or disables settings based on Checkbutton server_enable
            """
            if self.server_enable.get() == 0:
                combobox_ftp['state'] = "disabled"
                self.port_box_ftp['state'] = "disabled"
                cb_create_directory['state'] = 'disabled'
                cb_store_file['state'] = 'disabled'
            else:
                combobox_ftp['state'] = "readonly"
                self.port_box_ftp['state'] = "normal"
                cb_create_directory['state'] = 'normal'
                cb_store_file['state'] = 'normal'

        self.server_enable = IntVar(self.tab_ftp_server)
        self.server_enable.set(int(self.data[6]))
        Checkbutton(self.tab_ftp_server, text="FTP Server", command=click_change_ftp_server,
                    font=('arial', 10, 'bold'), variable=self.server_enable).place(x=10, y=10)

        Label(self.tab_ftp_server, text="FTP Server Port :", font=('arial', 10, 'bold'), ).place(x=270, y=15)

        self.port_box_ftp = Entry(self.tab_ftp_server, font=('arial', 15, 'bold'))
        self.port_box_ftp.insert('end', str(self.data[5]))
        self.port_box_ftp.place(x=390, y=15, width=100)

        Label(self.tab_ftp_server, text="FTP Server access path: ", font=('arial', 10, 'bold'), ).place(x=10, y=60)

        self.textvariable_ftp_path = StringVar()
        root = get_root(username=self.data[12])
        combobox_ftp = ttk.Combobox(self.tab_ftp_server, values=root, width=20,
                                    textvariable=self.textvariable_ftp_path, state='readonly', )
        combobox_ftp.place(x=170, y=60)
        try:
            combobox_ftp.current(root.index(self.data[7]))
        except ValueError:
            combobox_ftp.current()

        self.create_directory = IntVar(self.tab_ftp_server)
        self.create_directory.set(int(self.data[8]))
        cb_create_directory = Checkbutton(self.tab_ftp_server, text="Create directory", command=click_change_ftp_server,
                                          font=('arial', 10, 'bold'), variable=self.create_directory)
        cb_create_directory.place(x=10, y=90)

        self.store_file = IntVar(self.tab_ftp_server)
        self.store_file.set(int(self.data[9]))
        cb_store_file = Checkbutton(self.tab_ftp_server, text="Store a file to the server",
                                    command=click_change_ftp_server,
                                    font=('arial', 10, 'bold'), variable=self.store_file)
        cb_store_file.place(x=10, y=115)

        Button(self.tab_ftp_server, text="Save", font=('arial', 10, 'bold'),
               command=self._save_settings_ftp).place(relx=0.5, rely=0.6, anchor="center")
        click_change_ftp_server()

    def _save_settings_ftp(self):
        """
        Save ftp server settings to database
        """
        ftp_root = self.textvariable_ftp_path.get()
        port = check_port(self.port_box_ftp.get())
        server_enable = self.server_enable.get()
        if server_enable == 1:
            if ftp_root == '':
                messagebox.showerror('Error', 'Select the access path of the ftp server')
            else:
                if port != '':
                    self.database.write_data('1', 'ftp_server')
                    self.database.write_data(port, 'port_ftp')
                    self.database.write_data(ftp_root, 'ftp_root')
                    self.database.write_data(str(self.create_directory.get()), 'ftp_create_directory')
                    self.database.write_data(str(self.store_file.get()), 'ftp_store_file')
                    messagebox.showinfo('successful', 'Changes saved')
        else:
            self.database.write_data('0', 'ftp_server')
            messagebox.showinfo('successful', 'Changes saved')

    def more(self):
        self.run_background = IntVar(self.tab_more)
        self.run_background.set(int(self.data[10]))
        Checkbutton(self.tab_more, text="Run in the background", font=('arial', 10, 'bold'),
                    variable=self.run_background).place(x=10, y=10)

        Button(self.tab_more, text="Save", font=('arial', 10, 'bold'),
               command=self._save_settings_more).place(relx=0.5, rely=0.6, anchor="center")

        Label(self.tab_more, text="Web App Port :", font=('arial', 10, 'bold'), ).place(x=270, y=15)

        self.port_box_web = Entry(self.tab_more, font=('arial', 15, 'bold'))
        self.port_box_web.insert('end', str(self.data[1]))
        self.port_box_web.place(x=370, y=10, width=100)

    def _save_settings_more(self):
        port = check_port(self.port_box_web.get())
        if port != '':
            self.database.write_data(port, "port")
            self.database.write_data(str(self.run_background.get()), 'run_background')
            messagebox.showinfo('successful', 'Changes saved')

    def login_page(self):

        def click_change_login():
            """
            Enables or disables settings based on Checkbutton login_status
            """
            if self.login_status.get() == 0:
                username_box['state'] = "disabled"
                password_box['state'] = "disabled"
                password_v_box['state'] = 'disabled'
            else:
                username_box['state'] = "normal"
                password_box['state'] = 'normal'
                password_v_box['state'] = 'normal'

        def _save_login_page():
            username = username_box.get()
            password = password_box.get()
            password_v = password_v_box.get()
            if self.login_status.get() == 1:
                if username_box.get() == '':
                    self.database.write_data('1', 'login_status')
                    messagebox.showinfo('successful', 'Settings saved successfully')
                elif check_username(username):
                    if password == password_v and check_password(password):
                        self.database.write_data('1', 'login_status')
                        self.database.write_data(username, 'admin_username')
                        self.database.write_data(sha256(password.encode()).hexdigest(), 'admin_password')
                        messagebox.showinfo('successful', 'Settings saved successfully')
                    else:
                        messagebox.showerror('Invalid password', 'Enter a valid Password\nMinimum 8 characters, at least one uppercase letter, one lowercase letter, one number and one special character (@$!%*?&)')
                else:
                    messagebox.showerror('Invalid username', 'Enter a valid username\nusername is 4-20 characters long\nallowed characters a-z A-Z 0-9')
            else:
                self.database.write_data('0', 'login_status')
                messagebox.showinfo('successful', 'Settings saved successfully')

        self.login_status = IntVar(self.tab_login_page)
        self.login_status.set(int(self.data[11]))
        Checkbutton(self.tab_login_page, text="Login page", command=click_change_login,
                    font=('arial', 10, 'bold'), variable=self.login_status).place(x=10, y=10)

        Label(self.tab_login_page, text="Username: ", font=('arial', 10, 'bold'), ).place(x=10, y=45)
        Label(self.tab_login_page, text="Password: ", font=('arial', 10, 'bold'), ).place(x=10, y=80)
        Label(self.tab_login_page, text="Password verification: ", font=('arial', 10, 'bold'), ).place(x=10, y=115)

        username_box = Entry(self.tab_login_page, font=('arial', 10, 'bold'))
        username_box.place(x=160, y=47, width=300)
        password_box = Entry(self.tab_login_page, font=('arial', 10, 'bold'), show="*")
        password_box.place(x=160, y=84, width=300)
        password_v_box = Entry(self.tab_login_page, font=('arial', 10, 'bold'), show="*")
        password_v_box.place(x=160, y=118, width=300)

        Button(self.tab_login_page, text="Save", font=('arial', 10, 'bold'),
               command=_save_login_page).place(relx=0.5, rely=0.7, anchor="center")
        click_change_login()
