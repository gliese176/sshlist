from tkinter import *
from tkinter import ttk
from collections import namedtuple
from pathlib import Path

import subprocess

from serializer import Serializer
from tuples import HostData, EditHostResult

PROJECT_ROOT = Path(__file__).resolve().parents[1]



class EditHostWindow(Toplevel):
    def __init__(self, parent, name="", host="", port="22", username="", key_file="") -> None:
        super().__init__(parent)

        self.name = StringVar()
        self.name.set(name)
        self.host = StringVar()
        self.host.set(host)
        self.port = StringVar()
        self.port.set(port)
        self.username = StringVar()
        self.username.set(username)
        self.key_file = StringVar()
        self.key_file.set(key_file)

        self.aborted = False

        self.setup_ui()
        self.setup_bindings()


    def setup_ui(self):
        self.title("Add host")

        self.label_frame = LabelFrame(self)
        self.label_frame.pack(anchor=CENTER)

        self.name_label = Label(self.label_frame, text="Name")
        self.name_label.grid(row=0)

        self.host_label = Label(self.label_frame, text="Host")
        self.host_label.grid(row=1)

        self.port_label = Label(self.label_frame, text="Port")
        self.port_label.grid(row=2)

        self.username_label = Label(self.label_frame, text="Username")
        self.username_label.grid(row=3)

        self.key_file_label = Label(self.label_frame, text="Key file")
        self.key_file_label.grid(row=4)

        self.name_entry = Entry(self.label_frame, textvariable=self.name)
        self.name_entry.grid(row=0, column=1, sticky=W)
        self.name_entry.focus_set()

        self.host_entry = Entry(self.label_frame, textvariable=self.host)
        self.host_entry.grid(row=1, column=1, sticky=W)

        self.port_entry = Entry(self.label_frame, textvariable=self.port)
        self.port_entry.grid(row=2, column=1, sticky=W)

        self.username_entry = Entry(self.label_frame, textvariable=self.username)
        self.username_entry.grid(row=3, column=1, sticky=W)

        self.key_file_entry = Entry(self.label_frame, textvariable=self.key_file)
        self.key_file_entry.grid(row=4, column=1, sticky=W)


    def setup_bindings(self):
        self.bind('<Escape>', lambda e: self.abort())
        self.bind('<Control-s>', lambda e: self.destroy())
        
        self.host_entry.bind('<Return>', lambda e: self.port_entry.focus_set())
        self.port_entry.bind('<Return>', lambda e: self.username_entry.focus_set())
        self.username_entry.bind('<Return>', lambda e: self.key_file_entry.focus_set())
        self.key_file_entry.bind('<Return>', lambda e: self.destroy())


    def open(self):
        self.grab_set()
        self.wait_window()

        aborted = self.aborted
        name = self.name.get()
        host = self.host.get()
        port = self.port.get()
        username = self.username.get()
        key_file = self.key_file.get()

        host_data = HostData(name, host, port, username, key_file)

        return EditHostResult(aborted, host_data)
    
    def abort(self):
        self.aborted = True
        self.destroy()


class MainWindow(Tk):
    def __init__(self):
        super().__init__()

        self.serializer = Serializer(PROJECT_ROOT / "servers.json", PROJECT_ROOT / "settings.json")

        self.servers = self.serializer.load_servers()

        self.setup_ui()
        self.setup_bindings()

    def setup_ui(self):
        self.title("SSHList")
        self.geometry("300x400")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill=BOTH)

        # Hosts tab

        self.servers_frame = ttk.Frame(self.notebook)
        self.servers_frame.pack(fill=BOTH, expand=True)

        self.servers_list = Listbox(self.servers_frame)
        self.servers_list.pack(fill=BOTH, expand=True)
        self.update_servers_list()
        self.servers_list.focus_set()
        self.servers_list.activate(0)
        self.servers_list.selection_set(0)

        # Settings tab

        self.settings_frame = ttk.Frame(self.notebook)
        self.settings_frame.pack(fill=BOTH, expand=True)

        # Bindings tab

        self.bindings_frame = ttk.Frame(self.notebook)
        self.bindings_frame.pack(fill=BOTH, expand=True)

        self.bindings_label = Label(self.bindings_frame, text="<Escape> - quit\n<e> - edit server\n<a> - add server\n<d> - delete server\n<Return> - select server")
        self.bindings_label.pack()

        # Adding tabs

        self.notebook.add(self.servers_frame, text="Servers <F1>")
        self.notebook.add(self.settings_frame, text="Settings <F2>")
        self.notebook.add(self.bindings_frame, text="Bindings <F3>")

    def setup_bindings(self):
        self.bind('<F1>', lambda e: self.select_tab(0))
        self.bind('<F2>', lambda e: self.select_tab(1))
        self.bind('<F3>', lambda e: self.select_tab(2))
        self.bind('<Escape>', lambda e: self.destroy())
        self.bind('<e>', lambda e: self.edit_server())
        self.bind('<a>', lambda e: self.add_server())
        self.bind('<d>', lambda e: self.delete_server())
        self.bind('<Return>', lambda e: self.select_server())
        self.bind('<q>', lambda e: self.update_servers_list())
    
    def select_tab(self, tab_id):
        self.notebook.select(tab_id)
    
    def edit_server(self):
        window = EditHostWindow(self)
        window.attributes('-type', 'dialog')
        host = window.open()

    def add_server(self):
        window = EditHostWindow(self)
        window.attributes('-type', 'dialog')
        result = window.open()
        if not result.aborted:
            self.servers.append(result.host_data)
        self.serializer.save_servers(self.servers)
        self.update_servers_list()
    
    def delete_server(self):
        for index in self.servers_list.curselection():
            self.servers.pop(index)
        self.serializer.save_servers(self.servers)
        self.update_servers_list()

    def select_server(self):
        for index in self.servers_list.curselection():
            self.open_console(self.servers[index])
    
    def open_console(self, host: HostData):
        command = f"/usr/bin/alacritty -e bash -c 'eval $(ssh-agent) && ssh-add {host.key_file} && ssh -p {host.port} {host.username}@{host.host} && bash' &"
        subprocess.call(command, shell=True)
        self.destroy()
    
    def update_servers_list(self):
        self.servers_list.delete(0,END)
        self.servers = self.serializer.load_servers()
        self.servers_list.insert(0, *[s.name for s in self.servers])


window = MainWindow()
window.attributes('-type', 'dialog')
window.mainloop()
