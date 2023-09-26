import os
import re
import toolbox

import openpyxl.worksheet.worksheet
from openpyxl import load_workbook
from openpyxl.cell.cell import Cell

path_dir = os.path.dirname(__file__)
path_file_teams_xlsx = os.path.join(path_dir, "Result", "result_home.xlsx")


def get_current_names_teams():
    wb = load_workbook(path_file_teams_xlsx)
    sheet: openpyxl.worksheet.worksheet.Worksheet = wb.active
    names_team = []

    for datas_a in sheet.columns:
        for t, data_a in enumerate(datas_a, start=1):
            if t == 1: continue
            data_a: Cell
            names_team.append(data_a.value)
        break
    return names_team


def set_correct_name_value(names_team: list, data_dicts: list[dict], key1: str, key2: str):
    new_list_data = []

    for data_result in data_dicts:
        name_1 = data_result[key1]['name']
        name_2 = data_result[key2]['name']
        for name in names_team:
            if re.search(fr"\b{name_1}\b", name):
                data_result[key1]['name'] = name
            if re.search(fr"\b{name_2}\b", name):
                data_result[key2]['name'] = name

        new_list_data.append(data_result)

    return new_list_data


def rewrite_names():
    if os.path.isfile('teams_to_search.txt'):
        os.remove('teams_to_search.txt')

    names_team = get_current_names_teams()
    team_result_games = toolbox.download_json_data(path_file='teams_result_game.json')
    coeff_team = toolbox.download_json_data(path_file='coeff_team.json')

    for data in [
        (team_result_games, 'team_1', 'team_2', 'teams_result_game.json'),
        (coeff_team, 'home_team', 'away_team', 'coeff_team.json')
    ]:
        new_list_data = set_correct_name_value(names_team, data[0], key1=data[1], key2=data[2])
        toolbox.save_json_data(json_data=new_list_data, path_file=data[3])

        if data[3] == 'coeff_team.json':
            for data_s in new_list_data:
                pair_teams = f"{data_s['home_team']['name']}, {data_s['away_team']['name']}"
                toolbox.save_txt_data_complementing(data_txt=pair_teams, path_file='teams_to_search.txt')

if __name__ == '__main__':
    rewrite_names()
