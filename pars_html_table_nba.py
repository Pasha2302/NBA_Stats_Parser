import os
from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup
import toolbox

path_dir = os.path.dirname(__file__)
path_result_xlsx = os.path.join(path_dir, "Result")
path_result_html = os.path.join(path_dir, "HTML_Data_Table")

# pd.describe_option()
pd.set_option('display.max_columns', 10)
pd.set_option('display.max_rows', 10)
# # display.expand_frame_repr позволяет DataFrame растянуть представление на страницы, охватывая все столбцы.
pd.set_option("display.expand_frame_repr", False)


def create_merged_df(list_df, title_team: str):
    # Инициализируем объединенный DataFrame (берем первый DataFrame из списка для присоединения остальных)
    merged_df = list_df[0]
    # Выполняем объединение (join) всех DataFrame из списка
    for df in list_df[1:]:
        merged_df = merged_df.merge(df, on=title_team, how='inner')
    # Сортируем DataFrame по колонке 'Home/Away TEAM' в алфавитном порядке
    sorted_df = merged_df.sort_values(by=title_team)
    return sorted_df


def calculate_column_values(df, key_win: str, key_def: str):
    # Умножаем значения в колонке "Win % Home/Away" на 100 и округляем до 1 знака после точки
    df[key_win] = (df[key_win] * 100).round(1)
    # Создаем рейтинг, где значения в колонке "2P Def Home/Away" заменяются на их места в рейтинге
    df[key_def] = df[key_def].rank(method='min', ascending=False).astype(int)
    return df


def get_table_nba():
    list_df_home = []
    list_df_away = []
    header_keys = toolbox.download_json_data(path_file='header_keys.json')
    list_name_files = os.listdir(path_result_html)

    for t, file_name in enumerate(list_name_files, start=1):
        path_data = os.path.join(path_result_html, file_name)
        key_file_html = file_name.split('_', maxsplit=1)[0]
        print(f"- {toolbox.Style.GREEN}[{t}] {key_file_html}\033[0m")

        text_html = toolbox.download_txt_data(path_file=path_data)
        soup = BeautifulSoup(text_html, 'lxml')
        html_pd = soup.find('table', {'class': 'Crom_table__p1iZz'})

        html_io = StringIO(str(html_pd))
        table = pd.read_html(html_io)[0]
        list_keys_table = list(table.keys())
        # print(list_keys_table)

        key_table1 = [k for k in list_keys_table if k.lower() == 'team'][0]
        if isinstance(header_keys[key_file_html], int):
            key_table2 = list_keys_table[header_keys[key_file_html]]
        elif isinstance(header_keys[key_file_html], str):
            key_table2 = [k for k in list_keys_table if k == header_keys[key_file_html]][0]
        else:
            key_table2 = [k for k in list_keys_table if k == r"Diff%"][0]

        desired_table = table[[key_table1, key_table2]]
        # Создаем копию DataFrame с переименованной колонкой
        if 'Away' in key_file_html:
            table_f = desired_table.rename(columns={key_table1: 'AWAY TEAM', key_table2: key_file_html})
            list_df_away.append(table_f)
            # print(table_f)
        else:
            table_f = desired_table.rename(columns={key_table1: 'HOME TEAM', key_table2: key_file_html})
            list_df_home.append(table_f)
            # print(table_f)

    merged_df_home = create_merged_df(list_df=list_df_home, title_team='HOME TEAM')
    merged_df_away = create_merged_df(list_df=list_df_away, title_team='AWAY TEAM')

    column_order = [
        title_table.replace('Home', 'Away').replace('HOME', 'AWAY') for title_table in list(merged_df_home.columns)
    ]
    merged_df_away = merged_df_away[column_order]

    merged_df_home = calculate_column_values(merged_df_home, key_win='Win % Home', key_def='2P Def Home')
    merged_df_away = calculate_column_values(merged_df_away, key_win='Win % Away', key_def='2P Def Away')

    # Записываем DataFrame в файл Excel
    merged_df_home.to_excel(os.path.join(path_result_xlsx, "result_home.xlsx"), index=False)
    merged_df_away.to_excel(os.path.join(path_result_xlsx, "result_away.xlsx"), index=False)

    print(f"{toolbox.Style.YELLOW}{'--' * 60}\033[0m")
    print(merged_df_home)
    print(f"{toolbox.Style.YELLOW}{'--' * 60}\033[0m")
    print(merged_df_away)


if __name__ == '__main__':
    get_table_nba()
