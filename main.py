import os

import get_query_team
from get_html_table import start_get_data_html
from pars_data_sofascore import start_pars_html_page_sofascore
from pars_html_table_nba import get_table_nba
from search_for_command_names import rewrite_names
import toolbox


def main():
    proxy = None  # "ip:port"
    if os.path.isfile('my_proxy.txt'):
        proxy = toolbox.download_txt_data(path_file='my_proxy.txt').strip()
    url_sofascore = 'https://www.sofascore.com/basketball/2023-02-17'  # Укажите URL Адресс для сбора Коэффициентов

    print("<<================== ...ИДЕТ СБОР ДАННЫХ ... ==================>>\n")
    start_get_data_html(proxy)
    get_table_nba()
    start_pars_html_page_sofascore(url_sofascore, proxy)
    rewrite_names()

    if not os.path.isfile('teams_to_search.txt'):
        print('\nКоманды Для Поиска Не Найдены ...')
        return 0

    data_names = toolbox.download_txt_data(path_file='teams_to_search.txt')
    t_n = [(d_n.split(',')[0].strip(), d_n.split(',')[1].strip()) for d_n in data_names.split('\n') if d_n != '']

    for team_names in t_n:
        get_query_team.start_create_final_data(home_team=team_names[0], away_team=team_names[1])


if __name__ == '__main__':
    # pip freeze > requirements.txt
    main()

