import os
from selenium import webdriver

pathdir = os.path.dirname(__file__)
default_path_data_dir = os.path.join(pathdir, "data_chrome")


class CustomChromeDriver:
    def __init__(self, proxy: str | None = None, path_data_dir: str | None = None):
        self.pathdir = os.path.dirname(__file__)  # Получаем путь к текущей директории скрипта
        self.path_logs = os.path.join(self.pathdir, "logs_driver_chrome")  # Путь к директории для логов ChromeDriver
        self.proxy = proxy
        self.driver: None | webdriver.Chrome = None
        self.path_data_dir = path_data_dir
        # if not self.path_data_dir:
        #     self.path_data_dir = default_path_data_dir

    def create_driver(self) -> webdriver.Chrome:
        service = webdriver.ChromeService()  # Инициализация сервиса ChromeDriver
        chrome_options = webdriver.ChromeOptions()  # Инициализация опций Chrome

        if self.proxy and os.path.isfile('proxy_01.zip'):
            chrome_options.add_argument('--proxy-server=%s' % self.proxy)  # Установка прокси-сервера
            chrome_options.add_extension("proxy_01.zip")  # Добавление расширения

        chrome_options.add_argument('ignore-certificate-errors')  # Игнорирование ошибок сертификатов
        # Исключение опции "enable-automation"
        chrome_options.add_experimental_option("excludeSwitches",["enable-automation"])
        # Отключение расширения автоматизации
        chrome_options.add_experimental_option('useAutomationExtension', False)
        if self.path_data_dir:
            # Путь к директории с данными профиля пользователя (закомментировано)
            chrome_options.add_argument(f"user-data-dir={self.path_data_dir}")

        # chrome_options.add_argument("--headless")  # Запуск браузера в режиме без интерфейса (закомментировано)
        chrome_options.page_load_strategy = 'normal'  # 'eager' ,  'none', 'normal'

        # service = webdriver.ChromeService(
        #     service_args=['--log-level=DEBUG'], log_output=subprocess.STDOUT, log_path=path_logs
        # )  # Настройка логирования (закомментировано)

        self.driver = webdriver.Chrome(service=service, options=chrome_options)  # Инициализация ChromeDriver с настройками

        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            'source': '''
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                  '''
        })  # Выполнение команды в Chrome DevTools Protocol (Скрытие автоматизации)

        self.driver.maximize_window()  # Максимизация окна браузера
        self.driver.implicitly_wait(15)  # Установка неявного ожидания (30 секунд)

        return self.driver
