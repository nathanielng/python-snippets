#!/usr/bin/env python
import argparse
import google_drive
import gspread
import os

from oauth2client.service_account import ServiceAccountCredentials


GDRIVE_CREDENTIALS = os.getenv('GDRIVE_CREDENTIALS', None)

class GoogleSpreadsheet():

    def __init__(self, credential_file, spreadsheet_name, worksheet_name=None, scope=['https://www.googleapis.com/auth/drive']):
        self._credential_file = os.path.expanduser(credential_file)
        self._spreadsheet_name = spreadsheet_name
        self._scope = scope
        self._credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self._credential_file, self._scope)
        self._gc = gspread.authorize(self._credentials)

        try:
            self._sh = self._gc.open(spreadsheet_name)
        except gspread.exceptions.SpreadsheetNotFound as e:
            print(f'Spreadsheet not found: {spreadsheet_name}')
            print(f'Error: {e}')
            self._sh = None
            return

        try:
            self._ws = self._sh.sheet1
        except gspread.exceptions.APIError as e:
            print(f'API Error: {e}')
            self._ws = None


    def switch_worksheet(self, worksheet_name=None):
        if worksheet_name is None:
            self._ws = sh.sheet1
        else:
            self._ws = self._sh.worksheet(worksheet_name)
        return self._ws


    def get_worksheets(self):
        worksheets = self._sh.worksheets()
        return [ worksheet.title for worksheet in worksheets ]


    def get_cell(self, row, col):
        return self._ws.cell(row, col).value


    def get_cell_formula(self, row, col):
        return self._ws.cell(row, col, value_render_option='FORMULA').value


    def get_all_cells(self):
        return self._ws.get_all_values()


    def update_cell(self, row, col, value):
        self._ws.update_cell(row, col, value)

    
    def print_cell_data(self):
        cell_data = self.get_all_cells()
        for i, row_data in enumerate(cell_data):
            print(f'{i}: ', end='')
            for data in row_data:
                print(data, end='|')
            print()


def main(args):
    GS = GoogleSpreadsheet(
        args.credential_file,
        args.spreadsheet,
        args.worksheet)
    if GS._sh is None or GS._ws is None:
        return

    print(f"Spreadsheet: {args.spreadsheet} (id={GS._sh.id})")
    print(f"Worksheets: {','.join(GS.get_worksheets())}")
    GS.print_cell_data()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--credential_file', default=GDRIVE_CREDENTIALS)
    parser.add_argument('--spreadsheet')
    parser.add_argument('--worksheet')
    parser.add_argument('--upload_csv', help='Specify csv file to upload')
    args = parser.parse_args()
    main(args)
