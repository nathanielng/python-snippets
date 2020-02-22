#!/usr/bin/env python

import apiclient
import os

from oauth2client.service_account import ServiceAccountCredentials


GDRIVE_CREDENTIALS = os.getenv('GDRIVE_CREDENTIALS')


class G_Drive():

    def __init__(self, credential_file):
        self._credential_file = credential_file
        self._scope = ['https://www.googleapis.com/auth/drive']
        self._credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self._credential_file, self._scope)
        self._service = apiclient.discovery.build(
            'drive', 'v3', credentials=self._credentials)


    def get_files(self):
        file_obj = self._service.files()
        results = file_obj.list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        return items


    def print_files(self):
        items = self.get_files()
        for i, item in enumerate(items):
            print(f"{i}: {item['name']} (id = {item['id']})")


    def move_files(self, file_ids, new_folder_id):
        """
        Moves file_ids to new_folder_id
        Adapted from: https://developers.google.com/drive/api/v3/folder
        """
        file_obj = self._service.files()
        for file_id in file_ids:
            try:
                file = file_obj.get(
                    fileId=file_id,
                    fields='parents').execute()
                previous_parents = ",".join(file.get('parents'))
                file = file_id.update(
                    fileId=file_id,
                    addParents=new_folder_id,
                    removeParents=previous_parents,
                    fields='id, parents').execute()
            except Exception as e:
                print(f"Failed to move file_id: {', '.join(file_ids)} to folder_id: {new_folder_id}")
                return


    def delete_files(self, file_ids):
        file_obj = self._service.files()
        for file_id in file_ids:
            try:
                file_obj.delete(fileId=file_id).execute()
            except apiclient.errors.HttpError as e:
                print(f'Failed to delete file_id={file_id}')
                print(f'Error: {e}')


    def create_folder(self, folder_name):
        """
        Creates a new folder
        Adapted from: https://developers.google.com/drive/api/v3/folder
        """
        file_obj = self._service.files()
        body = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        file = file_obj.create(body=body, fields='id').execute()
        folder_id = file.get('id')
        return folder_id


if __name__ == "__main__":
    GD = G_Drive(GDRIVE_CREDENTIALS)
    GD.print_files()
