from custom_selenium_chrome_driver import CustomChromeDriver
from selenium.webdriver.common.by import By


def start_get_data_html(proxy=None):
    driver = CustomChromeDriver(proxy=proxy).create_driver()
    from pathlib import Path
    import toolbox

    path_result_html = str(Path("HTML_Data_Table", "{}_test_data.html"))

    for url_data in toolbox.download_json_data(path_file='headers_search.json'):
        url = url_data['url']

        while True:
            driver.get(url)
            try:
                check_elm = driver.find_element(By.CSS_SELECTOR, "table[class='Crom_table__p1iZz']")
                if check_elm:
                    break
            except Exception as err1:
                print("check_elm: <<table[class='Crom_table__p1iZz>>\n", err1)

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        res = str(driver.page_source)
        path_result_html_f = path_result_html.format(url_data['header'])
        toolbox.save_txt_data(data_txt=res, path_file=path_result_html_f)
        print('>', end='')
    driver.quit()
