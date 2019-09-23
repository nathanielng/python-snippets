#!/usr/bin/env python

import os
import pandas as pd
import paramiko
import PIL


HOME = os.getenv('HOME')


class SSHHost:
    """A class to handle remote SSH connections"""


    def __init__(self, userid, host, key):
        self._userid = userid
        self._host = host
        self._key = key


    def get_remote_ssh_client(self):
        k = paramiko.RSAKey.from_private_key_file(self._key)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=self._host,
                           username=self._userid,
                           pkey=k)  # password='...')
        return ssh_client


    def remote_execute(self, command):
        ssh_client = self.get_remote_ssh_client()
        stdin, stdout, stderr = ssh_client.exec_command(command)
        stdout = [x.strip() for x in stdout.readlines()]
        stderr = [x.strip() for x in stderr.readlines()]
        ssh_client.close()
        return stdin, stdout, stderr


    def remote_file_download(self, src_file, dest_file):
        ssh_client = self.get_remote_ssh_client()
        ftp_client = ssh_client.open_sftp()
        success = True
        try:
            ftp_client.get(src_file, dest_file)
        except:
            success = False
        ftp_client.close()
        ssh_client.close()
        return success


    def remote_file_upload(self, src_file, dest_file):
        ssh_client = self.get_remote_ssh_client()
        ftp_client = ssh_client.open_sftp()
        ftp_client.put(src_file, dest_file)
        ftp_client.close()
        ssh_client.close()


    def remote_file_to_df(self, src_file, action='read_table'):
        ssh_client = self.get_remote_ssh_client()
        ftp_client = ssh_client.open_sftp()
        if action == 'read_table':
            df = pd.read_table(ftp_client.open(src_file))
        elif action == 'read_csv':
            df = pd.read_csv(ftp_client.open(src_file))
        ftp_client.close()
        ssh_client.close()
        return df


    def remote_file_to_display(self, src_file):
        ssh_client = self.get_remote_ssh_client()
        ftp_client = ssh_client.open_sftp()
        img = PIL.Image.open(ftp_client.open(src_file))
        img.load()  # read the data
        ftp_client.close()
        ssh_client.close()
        return img


if __name__ == "__main__":
    pass
