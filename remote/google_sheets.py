#!/usr/bin/env python
import argparse
import gspread
import os

from oauth2client.service_account import ServiceAccountCredentials


class GoogleSpreadsheet():

    def __init__(self, credential_file, spreadsheet_name, worksheet_name=None, scope=['https://www.googleapis.com/auth/drive']):
        self._credential_file = os.path.expanduser(credential_file)
        self._spreadsheet_name = spreadsheet_name
        self._scope = scope
        self._credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self._credential_file, self._scope)
        self._gc = gspread.authorize(self._credentials)
        self._sh = self._gc.open(spreadsheet_name)
        self._ws = self._sh.sheet1


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


def main(args):
    GS = GoogleSpreadsheet(
        args.credential_file,
        args.spreadsheet,
        args.worksheet)
    print(f"Worksheets: {','.join(GS.get_worksheets())}")

    cell_data = GS.get_all_cells()
    for i, row_data in enumerate(cell_data):
        print(f'{i}: ', end='')
        for data in row_data:
            print(data, end='|')
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--credential_file')
    parser.add_argument('--spreadsheet')
    parser.add_argument('--worksheet')
    args = parser.parse_args()
    main(args)