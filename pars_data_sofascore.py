import os
import re

import toolbox
from selenium.webdriver.chrome.webdriver import WebDriver
from custom_selenium_chrome_driver import CustomChromeDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup

driver: None | WebDriver = None
click_slider_is = False


def entrance_site(url_sofascore):
    global click_slider_is

    driver.get(url_sofascore)
    if not click_slider_is:
        while True:
            check_dialog_button = driver.find_elements(
                By.CSS_SELECTOR, "button[class='fc-button fc-cta-consent fc-primary-button']")
            if check_dialog_button:
                check_dialog_button[0].click()
            try:
                driver.find_element(By.CSS_SELECTOR, "span[class='slider']").click()
                driver.refresh()
                break
            except Exception as err2:
                print(f"\n[entrance_site()]:\n{err2}")

        click_slider_is = True


def get_data_five_result(result_tags):
    tags_results = result_tags.find_element(
        By.CSS_SELECTOR, "div[class='sc-fqkvVR sc-dcJsrY eEGGTW hNspbb sc-4d3c2798-2 ioyshH']") \
        .find_elements(By.TAG_NAME, 'div')
    list_type_res = [
        res.get_attribute('type').strip() for res in tags_results
        if res.get_attribute('type') is not None
    ]
    five_results = ','.join(list_type_res).strip(',')
    return five_results


def get_results_games(tag_team: WebElement, info_teams: dict):
    dict_info_result_five_games = {
        'team_1': {
            'name': info_teams['home_team']['name'],
            'team_id': info_teams['home_team']['team_id'],
            'five_results': ''
        },
        'team_2': {
            'name': info_teams['away_team']['name'],
            'team_id': info_teams['away_team']['team_id'],
            'five_results': ''
        }
    }
    ActionChains(driver).move_to_element(tag_team).pause(1).click().perform()
    block_result_game = driver.find_element(By.CSS_SELECTOR, "div[class='sc-fqkvVR liWFVJ']")
    ActionChains(driver).move_to_element(block_result_game).pause(5).perform()

    block_result_game = driver.find_element(By.CSS_SELECTOR, "div[class='sc-fqkvVR liWFVJ']")
    block_teams_result_game = block_result_game.find_elements(
        By.CSS_SELECTOR, "div[class='sc-fqkvVR sc-dcJsrY ditMfZ fFmCDf']")

    for result_tags in block_teams_result_game:
        src_img = result_tags.find_element(By.TAG_NAME, "img").get_attribute('src')

        if re.search(fr"\b{dict_info_result_five_games['team_1']['team_id']}\b", src_img):
            five_results = get_data_five_result(result_tags)
            dict_info_result_five_games['team_1']['five_results'] = five_results

        if re.search(fr"\b{dict_info_result_five_games['team_2']['team_id']}\b", src_img):
            five_results = get_data_five_result(result_tags)
            dict_info_result_five_games['team_2']['five_results'] = five_results

    return dict_info_result_five_games


def get_data_teams_usa_nba(teams_gams_html_tags) -> dict:
    coefficient_1 = coefficient_2 = None

    soup = BeautifulSoup(teams_gams_html_tags, 'lxml')
    teams_tags = soup.find("div", {"class": "sc-fqkvVR bALrbz"}).find_all("div")
    coefficients_tags = soup.find_all("a", {"class": "sc-fqkvVR kvpsZC"})

    links = soup.find_all("img", {"class": "sc-cPiKLX kArRjP"})
    team_1_link_search = links[0].get('src')
    team_2_link_search = links[1].get('src')

    team_id_1 = re.search("(?<=/)\d+[/]*", team_1_link_search).group()
    team_id_2 = re.search("(?<=/)\d+[/]*", team_2_link_search).group()

    name_team_1 = teams_tags[0].text
    name_team_2 = teams_tags[1].text

    for check_tag in coefficients_tags:
        check_number_coefficient = check_tag.find("span", {"class": "sc-jEACwC dxXJOS"}).text
        if check_number_coefficient.strip() == '1':
            coefficient_1 = check_tag.text[1:]
        if check_number_coefficient.strip() == '2':
            coefficient_2 = check_tag.text[1:]

    return {
        'home_team': {'name': name_team_1, 'coeff': coefficient_1, 'team_id': team_id_1},
        'away_team': {'name': name_team_2, 'coeff': coefficient_2, 'team_id': team_id_2}}


def search_blocks_teams_usa_nba():
    league_search_name = "USA NBA Box score"
    text_name_league = ''
    tags_name_league = None
    stop_class = "sc-fHjqPf hEicas"
    data_coeff_team = []
    list_data_result_game = []

    while True:
        try:
            block_leagues = driver.find_element(By.CSS_SELECTOR, "div[id='pinned-list-fade-target']")
            block_names_leagues = block_leagues.find_elements(By.XPATH, "./*")
            if block_names_leagues:
                break
        except StaleElementReferenceException as error:
            error = str(error)
            print(f"\n[block_names_leagues]:\n{error[:error.find('Stacktrace:')]}")
            driver.refresh()
            pass

    for tag_team in block_names_leagues:
        tag_text = tag_team.text.replace('\n', ' ').strip()
        print(f"{tag_text}\n{'..' * 60}")
        if tag_text == text_name_league:
            continue
        if tag_text != league_search_name and not text_name_league:
            continue

        check_stop_class = tag_team.get_attribute('class')
        if league_search_name != text_name_league:
            tags_name_league = tag_team.find_elements(
                By.CSS_SELECTOR, "div[class='sc-fqkvVR sc-dcJsrY fCtlUD fFmCDf']")

        if tags_name_league and text_name_league != league_search_name:
            text_name_league = tags_name_league[0].text.replace('\n', ' ').strip()
            continue

        if text_name_league == league_search_name:
            if stop_class == check_stop_class:
                break
            data_team_coeff_name = get_data_teams_usa_nba(teams_gams_html_tags=tag_team.get_attribute('outerHTML'))
            data_coeff_team.append(data_team_coeff_name)
            result_five_games = get_results_games(tag_team, info_teams=data_team_coeff_name)
            list_data_result_game.append(result_five_games)
    print(f"\n{'==' * 60}")

    toolbox.save_json_data(json_data=list_data_result_game, path_file='teams_result_game.json')
    toolbox.save_json_data(json_data=data_coeff_team, path_file='coeff_team.json')

    for data_coeff, data_five_result in zip(data_coeff_team, list_data_result_game):
        print(data_coeff)
        print(data_five_result)
        print('--' * 60)


def pars_html_page_sofascore(url_sofascore):
    while True:
        try:
            entrance_site(url_sofascore)
            search_blocks_teams_usa_nba()
            break
        except Exception as error:
            error = str(error)
            print(f"\n{toolbox.Style.YELLOW}[ pars_html_page_sofascore(): ]\n:"
                  f"{error[:error.find('Stacktrace:')]}{toolbox.Style.END_SC}")


def start_pars_html_page_sofascore(url_sofascore, proxy=None):
    global driver
    driver = CustomChromeDriver(proxy=proxy).create_driver()
    try:
        pars_html_page_sofascore(url_sofascore)
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()
