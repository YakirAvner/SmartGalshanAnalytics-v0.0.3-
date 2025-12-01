import os
import paramiko as pmk
import posixpath
import socket
import stat


class IP_DB_Copier:
    def __init__(self, device_name_list, device_ip_list):
        self.device_name_list = device_name_list
        self.device_ip_list = device_ip_list

    def copy_folder(self, sftp, local_dir, phone_source_folder):
        os.makedirs(local_dir, exist_ok=True)
        for files_or_folders in sftp.listdir_attr(phone_source_folder):
            local_item = os.path.join(local_dir, files_or_folders.filename)
            remote_item = posixpath.join(
                phone_source_folder, files_or_folders.filename)
            if stat.S_ISDIR(files_or_folders.st_mode):
                self.copy_folder(sftp, local_item, remote_item)
            else:
                if not os.path.exists(local_item):
                    sftp.get(remote_item, local_item)
                    print(f"Copied {remote_item} to {local_item}")
                else:
                    print(
                        f"The {local_item} is already copied in the local directory")

    def connect_to_SGPhone(self):
        base_local_dir = r"C:\\Users\\user\Desktop\\Yakir Avner\\SG_Devices"
        for phone_name, ip in zip(self.device_name_list, self.device_ip_list):
            # Connecting to each DB in the list.
            # Define the database connector from the given IP
            try:
                hostname, port = ip.split(":")
                port = int(port)
            except ValueError:
                print(f"Invalid IP format: {ip}")
                continue
            username = "g188"
            password = "1470"
            phone_source_folder = r"/Documents"
            client = pmk.SSHClient()
            client.set_missing_host_key_policy(pmk.AutoAddPolicy())

            try:
                client.connect(hostname=hostname, port=port,
                               username=username, password=password)
                sftp = client.open_sftp()
                local_dir = os.path.join(base_local_dir, phone_name)
                
                # Looping inside the dates of the file.  
                for date_folder in sftp.listdir_attr(phone_source_folder):
                    # Checks if the remote item (date_file) is a DIRECTORY!!!
                    if stat.S_ISDIR(date_folder.st_mode):
                        db_folder = f"{phone_source_folder}/{date_folder.filename}"
                        # Loops the date_folders
                        for item in sftp.listdir_attr(date_folder):
                            # Checks if the remote item (db_file) is a DIRECTORY!!! & and named "SQLite".
                            if item.filename == "SQLite" and stat.S_ISDIR(item).st_mode:
                                SQLite_file = f"{db_folder}/{item.filename}"
                                # Loops the SQLite folder.
                                for Galshan_db in SQLite_file:
                                    # Checks if the files name is "Galshan.db".
                                    if Galshan_db == "Galshan.db":
                                        remote_db = f"{SQLite_file}/{Galshan_db}"
                                        local_db = os.path.join(local_dir, f"{date_folder.filename}_Galshan.db")

                                        self.copy_folder(sftp, local_db, remote_db)

            except (pmk.SSHException, socket.timeout, TimeoutError, OSError) as e:
                print(
                    f"Failed to connect to device at IP: {hostname} with an {e} error")
