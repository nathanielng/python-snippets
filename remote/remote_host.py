#!/usr/bin/env python

import argparse
import dropbox
import io
import os
import pandas as pd
import paramiko
import PIL


HOME = os.getenv('HOME')


class SSHHost:
    """A class to handle remote SSH connections"""


    def __init__(self, userid, host, key, passwd=None):
        self._userid = userid
        self._host = host
        self._keyfile = os.path.expanduser(key)
        if 'ed25519' in self._keyfile:
            if passwd is None:
                self._key = paramiko.Ed25519Key.from_private_key_file(self._keyfile)
            else:
                self._key = paramiko.Ed25519Key.from_private_key_file(self._keyfile, password=passwd)
        elif 'edcsa' in self._keyfile:
            self._key = paramiko.ECDSAKey.from_private_key_file(self._keyfile)
        else:
            self._key = paramiko.RSAKey.from_private_key_file(self._keyfile)
        self._ssh_client = self.get_remote_ssh_client()


    def get_remote_ssh_client(self):
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=self._host,
                           username=self._userid,
                           pkey=self._key)
        return ssh_client


    def remote_execute(self, command):
        try:
            stdin, stdout, stderr = self._ssh_client.exec_command(command)
            stdout = [x.strip() for x in stdout.readlines()]
            stderr = [x.strip() for x in stderr.readlines()]
            return stdin, stdout, stderr
        except Exception as e:
            print("Exception: {e}")
            return None, None, None


    def remote_file_download(self, src_file, dest_file):
        ftp_client = self._ssh_client.open_sftp()
        success = True
        try:
            ftp_client.get(src_file, dest_file)
        except:
            success = False
        ftp_client.close()
        return success


    def remote_file_upload(self, src_file, dest_file):
        ftp_client = self._ssh_client.open_sftp()
        success = True
        try:
            ftp_client.put(src_file, dest_file)
        except:
            success = False
        ftp_client.close()
        return success


    def remote_file_to_df(self, src_file, action='read_table'):
        ftp_client = self._ssh_client.open_sftp()
        if action == 'read_table':
            df = pd.read_table(ftp_client.open(src_file))
        elif action == 'read_csv':
            df = pd.read_csv(ftp_client.open(src_file))
        ftp_client.close()
        return df


    def remote_file_to_display(self, src_file):
        ftp_client = self._ssh_client.open_sftp()
        img = PIL.Image.open(ftp_client.open(src_file))
        img.load()  # read the data
        ftp_client.close()
        return img


    def describe(self):
        print(f"Login: {self._userid}@{self._host}")
        print(f"Key File: {self._keyfile}")


    def close(self):
        self._ssh_client.close()


class PBSHost:
    """A class to handle PBS connections"""
    def __init__(self, userid, host, key, password=None):
        self._SSH = SSHHost(userid, host, key, password)

    def qstat(self):
        stdin, stdout, stderr = \
            self._SSH.remote_execute("qstat")
        if len(stdout) == 0:
            return pd.DataFrame()
        qstat_txt = '\n'.join([stdout[0]] + stdout[2:])
        return pd.read_fwf(io.StringIO(qstat_txt), header=0)

    def close(self):
        self._SSH.close()


class DropboxHost:
    """A class to handle Dropbox connections"""

    def __init__(self, access_token):
        self._access_token = access_token
        self._dbx = dropbox.Dropbox(access_token)
        self._account = self._dbx.users_get_current_account()

    def get_file_list(self, folder=''):
        files = [entry.name for entry in
                 self._dbx.files_list_folder(folder).entries]
        return files

    def print_file_list(self, path):
        file_list = self.get_file_list(path)
        for filename in file_list:
            print(filename)

    def upload(self, src, dest):
        with open(src) as f:
            data = f.read()
        self._dbx.files_upload(data.encode('ascii'), dest)

    def download(self, src, dest):
        self._dbx.files_download_to_file(dest, src)


def main(args):
    if args.host == 'DROPBOX':
        DROPBOX_API_TOKEN = os.getenv("DROPBOX_API_TOKEN")
        DBX = DropboxHost(DROPBOX_API_TOKEN)

    elif args.command == 'qstat':
        PBS = PBSHost(
            args.user,
            args.host,
            os.path.abspath(args.key),
            args.password)
        qstat_df = PBS.qstat()
        print(qstat_df)

    else:
        SSH = SSHHost(
            args.user,
            args.host,
            os.path.abspath(args.key),
            args.password)
        SSH.describe()
        stdin, stdout, stderr = SSH.remote_execute(args.command)
        for txt in stdout:
            print(txt)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--user')
    parser.add_argument('--host')
    parser.add_argument('--key')
    parser.add_argument('--command', help="Remote command")
    parser.add_argument('--password', default=None)
    args = parser.parse_args()
    main(args)