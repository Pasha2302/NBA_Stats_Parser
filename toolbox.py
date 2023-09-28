import fnmatch
import json
import platform
import types
from datetime import datetime, timezone, timedelta
import os
import time
import asyncio
import pickle
import traceback
from contextlib import contextmanager
from urllib.parse import urlparse, parse_qs, urlencode

import telegram
from telegram import InputFile


class Style:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    END_SC = '\033[0m'


def find_files_with_extension(extension, folder_path):  # extension = 'txt'; folder_path = '/data_dir'
    # Функция возвращаем список найденных файлов с указанным расширением
    found_files = []
    # Обход файловой системы, начиная с указанной папки
    for root, dirs, files in os.walk(folder_path):
        # root - текущая директория, dirs - список поддиректорий, files - список файлов в текущей директории
        for filename in fnmatch.filter(files, f'*.{extension}'):
            # Фильтруем файлы по расширению, добавляем пути к найденным файлам в список found_files
            found_files.append(os.path.join(root, filename))

    return found_files


def save_txt_data(data_txt, path_file):
    """Сохраняет текстовые данные в файл.
    Args:
        data_txt (str): текстовые данные для сохранения.
        path_file (str): путь к файлу для сохранения данных.
    """
    with open(path_file, 'w', encoding='utf-8') as f:
        f.write(str(data_txt))


def save_txt_data_complementing(data_txt, path_file):
    """Дописывает текстовые данные в конец файла.
    Args:
        data_txt (str): текстовые данные для записи.
        path_file (str): путь к файлу для записи данных.
    """
    with open(path_file, 'a', encoding='utf-8') as f:
        f.write(f"{str(data_txt)}\n")


def download_txt_data(path_file) -> str:
    """Загружает текстовые данные из файла.
    Args:
        path_file (str): путь к файлу для загрузки данных.
    Returns:
        str: загруженные текстовые данные.
    """
    with open(path_file, encoding='utf-8') as f:
        return f.read()


def save_json_complementing(json_data, path_file, ind=False):
    """Дописывает данные в формате JSON в конец файла.
    Args:
        json_data (list[dict] | dict): данные в формате JSON для записи.
        path_file (str): путь к файлу для записи данных.
        ind (bool): Флаг, указывающий на необходимость форматирования записываемых данных.
                    По умолчанию форматирование отключено.
    """
    indent = None
    if ind:
        indent = 4
    if os.path.isfile(path_file):
        # File exists
        with open(path_file, 'a', encoding='utf-8') as outfile:
            outfile.seek(outfile.tell() - 1, os.SEEK_SET)
            outfile.truncate()
            outfile.write(',\n')
            json.dump(json_data, outfile, ensure_ascii=False, indent=indent)
            outfile.write(']')
    else:
        # Create file
        with open(path_file, 'w', encoding='utf-8') as outfile:
            array = [json_data]
            json.dump(array, outfile, ensure_ascii=False, indent=indent)


def save_json_data(json_data, path_file):
    """Сохраняет данные в формате JSON в файл.
    Args:
        json_data (list[dict] | dict): данные в формате JSON для сохранения.
        path_file (str): путь к файлу для сохранения данных.
    """
    with open(path_file, 'w', encoding="utf-8") as file:
        json.dump(json_data, file, indent=4, ensure_ascii=False)


def download_json_data(path_file) -> list[dict] | dict:
    """Загружает данные в формате JSON из файла.
    Args:
        path_file (str): путь к файлу для загрузки данных.
    Returns:
        list[dict] | dict: загруженные данные в формате
    """
    with open(path_file, encoding="utf-8") as f:
        return json.load(f)


def save_pickle_data(data_pickle, path_file):
    """Сохраняет данные в файл в формате pickle"""
    with open(path_file, 'wb') as f:
        pickle.dump(data_pickle, f)


def save_complementing_pickle_data(data_pickle, path_file):
    """Дописывает данные в конец файла в формате pickle"""
    with open(path_file, 'ab') as f:
        pickle.dump(data_pickle, f)


def download_pickle_data(path_file):
    """Генератор, который поочередно возвращает объекты из файла в формате pickle"""
    with open(path_file, 'rb') as f:
        while True:
            try:
                yield pickle.load(f)
            except EOFError:
                break


def add_work_days(current_date):
    """Если текущая дата выпадает на выходной, возвращает ближайшую рабочую дату."""

    # Преобразовываем переданную дату в объект datetime
    current_datetime = datetime.fromtimestamp(current_date)
    # Определяем, является ли текущий день выходным
    is_weekend = current_datetime.weekday() >= 5
    if is_weekend:
        # Определяем количество дней, которое нужно добавить к текущей дате
        days_to_add = 7 - current_datetime.weekday()
        # Добавляем нужное количество дней к текущей дате
        current_datetime += timedelta(days=days_to_add)
    # Возвращаем результат в формате timestamp
    return current_datetime.timestamp()


def date_str(time_int, utc=False, seconds=False, standart=False):
    """Возвращает строку с датой в формате '%d/%m/%y %H:%M' или '%H:%M:%S' (если seconds=True).
            Если standart=True - '%y-%m-%d'
           Если utc=True, то время будет возвращено в UTC"""
    if time_int > 1670000000000:
        time_int = time_int // 1000
    if standart:
        form_str = '%Y-%m-%d'
    else:
        form_str = '%H:%M:%S' if seconds else '%d/%m/%y %H:%M'
    return datetime.fromtimestamp(time_int, tz=timezone.utc).strftime(form_str) if utc else datetime.fromtimestamp(
        time_int).strftime(form_str)


def date_file(time_int):
    """Возвращает строку с датой и временем в формате '%d-%m-%Y_%H-%M-%S' для имени файла"""
    if time_int > 1670000000000:
        time_int = time_int // 1000
    # form_str = '%d-%m-%Y_%H-%M-%S'
    form_str = '%Y-%m-%d %H:%M:%S.%f'
    return datetime.fromtimestamp(time_int).strftime(form_str)


def time_it(func):
    """
    Декоратор для замера времени выполнения функции в формате часы:минуты:секунды.
    Выводит время выполнения функции в консоль.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        total_time = end_time - start_time
        hours = int(total_time // 3600)
        minutes = int((total_time % 3600) // 60)
        seconds = round((total_time % 3600) % 60, 4)
        print(f"\nВремя выполнения функции {func.__name__}: {hours:02d}:{minutes:02d}:{seconds:.4f}")
        return result
    return wrapper


class TimeDelta:
    """
    Класс, представляющий временной интервал между двумя датами
        :param past_date: прошлая дата
        :param current_date: нынешняя или будущая
    """
    def __init__(self, past_date, current_date):
        if isinstance(past_date, datetime) and isinstance(current_date, datetime):
            self.timestamp1 = past_date.timestamp()
            self.timestamp2 = current_date.timestamp()
        elif isinstance(past_date, (int, float)) and isinstance(current_date, (int, float)):
            self.timestamp1 = past_date
            self.timestamp2 = current_date
        else:
            raise TypeError("Неподдерживаемый тип данных для past_date и current_date")

        self._calculate_diff()

    def _calculate_diff(self):
        """Вычисляет разницу между датами и записывает ее в атрибуты класса"""
        dt1 = datetime.fromtimestamp(self.timestamp1)
        dt2 = datetime.fromtimestamp(self.timestamp2)
        diff = dt2 - dt1
        self.days = diff.days
        self.hours = diff.seconds // 3600
        self.minutes = (diff.seconds // 60) % 60
        self.seconds = diff.seconds % 60

    def __str__(self):
        """Возвращает строку с описанием временного интервала"""
        return f"Разница между датами: " \
               f"{self.days} дней, {self.hours} часов, {self.minutes} минут, {self.seconds} секунд"


@contextmanager
def create_loop():
    loop_contex = None
    try:
        loop_contex = asyncio.new_event_loop()
        yield loop_contex
    finally:
        if loop_contex:
            if not loop_contex.is_closed():
                all_tasks = asyncio.all_tasks(loop_contex)
                if not all_tasks:
                    print("\nВсе задачи выполнены...")
                else:
                    for t, task in enumerate(all_tasks, start=1):
                        # print(f"[{t}] {task}\n{task.done()=}")
                        # print('--' * 40)
                        task.cancel()
                loop_contex.close()
                time.sleep(2)


class UrlParser:
    def __init__(self, url):
        # Разбиваем URL на составляющие и сохраняем в self.parsed_url
        self.parsed_url = urlparse(url)
        # Получаем параметры запроса и сохраняем в self.query_params
        self.query_params = parse_qs(self.parsed_url.query)

    def get_scheme(self):
        # Возвращает схему (http, https, ftp и т.д.)
        return self.parsed_url.scheme

    def get_domain(self):
        # Возвращает доменное имя
        return self.parsed_url.netloc

    def get_path(self):
        # Возвращает путь
        return self.parsed_url.path

    def get_query_params(self):
        # Возвращает параметры запроса в виде словаря
        return self.query_params

    def set_query_param(self, key, value):
        # Изменяет значение параметра запроса с заданным ключом на заданное значение
        self.query_params[key] = [value]

    def set_query_params(self, params: dict):
        # Задает новые параметры запроса
        # принимает словарь параметров запроса, а метод
        self.query_params = params

    def build_url(self):
        # Преобразует словарь параметров запроса в строку запроса и возвращает полный URL-адрес
        query_string = urlencode(self.query_params, doseq=True)
        return f"{self.get_scheme()}://{self.get_domain()}{self.get_path()}?{query_string}"


class TgBot3000:
    loop = asyncio.get_event_loop()
    try:
        conf = download_pickle_data('conf3000.bin').__next__()
    except FileNotFoundError:
        conf = {}

    def __init__(self):
        self.token = self.conf['tb3000']
        self.chat_id = self.conf['mci']
        self.bot = telegram.Bot(self.token)

    def start_coroutine(self, coroutine):
        self.loop.run_until_complete(coroutine)

    def send_text_message(self, text):
        try:
            self.start_coroutine(self.bot.send_message(chat_id=self.chat_id, text=text))
            print("Сообщение успешно отправлено.")
        except Exception as e:
            print(f"Произошла ошибка при отправке сообщения: {e}")

    def send_image(self, image_path):
        try:
            if not isinstance(image_path, str):
                image = image_path
            else:
                image = open(image_path, 'rb')
            self.start_coroutine(self.bot.send_photo(chat_id=self.chat_id, photo=InputFile(image)))
            print("Изображение успешно отправлено.")
        except Exception as e:
            print(f"Произошла ошибка при отправке изображения: {e}")


def error_handler(func: types.FunctionType):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            traceback_info = traceback.extract_tb(e.__traceback__)[-1]
            er = {
                "error": f"{Style.RED}DATETIME: ({datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')})\n"
                         f"FUNC NAME: [{func.__name__}]\n"
                         f"PATH MODULE: [{func.__code__.co_filename}]\n"
                         f"ERROR IN LINE: [{traceback_info.lineno}]\n"
                         f"ERROR CODE STR: {traceback_info.line}\n"
                         f"ARGUMENTS:\n\tpositional: {args}, named: {kwargs}\n"
                         f"ERROR: {e}{Style.END_SC}",
                "input_data": (args, kwargs)
            }
            print(er['error'])
            return er
    return wrapper


def async_error_handler(func):
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            traceback_info = traceback.extract_tb(e.__traceback__)[-1]
            er = {
                "error": f"{Style.RED}DATETIME: ({datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')})\n"
                         f"FUNC NAME: [{func.__name__}]\n"
                         f"PATH MODULE: [{func.__code__.co_filename}]\n"
                         f"ERROR IN LINE: [{traceback_info.lineno}]\n"
                         f"ERROR CODE STR: {traceback_info.line}\n"
                         f"ARGUMENTS:\n\tpositional: {args}, named: {kwargs}\n"
                         f"ERROR: {e}{Style.END_SC}",
                "input_data": (args, kwargs)
            }
            print(er['error'])
            return er
    return wrapper


@error_handler
def get_system_information():
    # Получение информации о системе
    system_info = platform.uname()
    # Получение информации о версии Python
    python_version = platform.python_version()
    # Получение информации о процессоре
    processor = platform.processor()
    # Получение информации о системе (имя и версия)
    # system_name = platform.system()
    system_version = platform.version()
    # Получение информации о версии операционной системы
    os_release = platform.release()
    # Формирование упорядоченного текста
    computer_info = f"Система: {system_info.system}\n" \
                    f"Узел сети: {system_info.node}\n" \
                    f"Выпуск: {os_release}\n" \
                    f"Версия системы: {system_version}\n" \
                    f"Версия Python: {python_version}\n" \
                    f"Процессор: {processor}"
    return computer_info


# class OpenAITranscriber:
#     def __init__(self, api_key):
#         self.api_key = api_key
#         openai.api_key = self.api_key
#
#     def transcribe_audio(self, model, audio_path):
#         with open(audio_path, "rb") as audio_file:
#             transcript = openai.Audio.transcribe(model, audio_file)
#             return transcript


if __name__ == '__main__':
    pass
