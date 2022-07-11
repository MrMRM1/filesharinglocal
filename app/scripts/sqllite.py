import sqlite3
from pathlib import Path
from os.path import join as join_path
from os import remove
from re import fullmatch
from ast import literal_eval

from scripts.network import port_flask

path_received = join_path(Path.home().__str__(), 'Downloads', 'HomeServerReceived')


class Database:
    def __init__(self):
        self.data = sqlite3.connect('data.db', check_same_thread=False)
        self.my_db = self.data.cursor()
        try:
            self.my_db.execute(f"SELECT * from data_user")
            data = self.my_db.fetchone()
            if len(data) < 11:
                data = list(data)
                if fullmatch(r'^\[.*]$', data[0]):
                    data[0] = ','.join(literal_eval(data[0]))
                self.data.close()
                remove('data.db')
                key = ['paths', 'port', 'data_id', 'upload', 'password', 'port_ftp', 'ftp_server', 'ftp_root',
                       'ftp_create_directory', 'ftp_store_file', 'run_background']
                self.__init__()
                for i, j in zip(data, key):
                    self.write_data(i, j)
        except:
            self.my_db.execute(f'CREATE TABLE data_user (paths LONGTEXT NULL, port INT DEFAULT {port_flask()}, data_id DEFAULT "1" ,upload DEFAULT "{path_received}", password TEXT NULL, port_ftp INT DEFAULT 8821, ftp_server DEFAULT "0", ftp_root NULL, ftp_create_directory DEFAULT "0", ftp_store_file DEFAULT "0", run_background DEFAULT "0")')
            sql = f'INSERT INTO data_user (data_id) VALUES ("1")'
            self.my_db.execute(sql)
            self.data.commit()

    def get_data(self):
        self.my_db.execute(f'SELECT * from data_user WHERE data_id = "1"')
        return self.my_db.fetchone()

    def write_data(self, data, data_type):
        sql = f'UPDATE data_user SET {data_type} = "{data}" WHERE data_id = "1"'
        self.my_db.execute(sql)
        self.data.commit()

