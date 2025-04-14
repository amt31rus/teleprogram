from datetime import datetime, timedelta
import logging
from logging.handlers import RotatingFileHandler
import time
import random
from data_fetcher.data_fetcher import DataFetcher
from parse_data_tvp.parse_data_tvp import parse_and_save_tvp
from url_generator.url_generator import URLGenerator
from date_range_generator.date_range_generator import DateRangeGenerator
from database.db_connector import connect_to_database


# Настройка логирования
def setup_logging():
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    log_file = 'tv_parser.log'

    # Создаем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Форматтер для всех обработчиков
    formatter = logging.Formatter(log_format)

    # Файловый обработчик (с явным указанием encoding)
    file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Консольный обработчик
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # Добавляем обработчики к корневому логгеру
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)


# Конфигурация парсера
PARSER_CONFIG = {
    'request_delay': (1, 3),
    'max_retries': 3,
    'retry_delay': 5,
    'timeout': 15,
    # user_agents теперь передается в DataFetcher
}


def ask_save_mode():
    """Интерактивный запрос режима работы"""
    print("\n" + "=" * 50)
    print("Выберите режим работы:")
    print("1 - Только парсинг (без записи в БД)")
    print("2 - Парсинг с сохранением в БД")
    print("=" * 50)

    while True:
        choice = input("Введите номер режима (1/2): ")
        if choice in ('1', '2'):
            return choice == '2'  # True если выбран режим с сохранением


def main():
    # Конфигурация
    setup_logging()

    save_to_db = ask_save_mode()  # Запрашиваем режим при запуске

    logging.info(f"\n{'=' * 50}\n"
                 f"РЕЖИМ: {'С СОХРАНЕНИЕМ В БД' if save_to_db else 'ТОЛЬКО ПАРСИНГ'}\n"
                 f"{'=' * 50}")


    logging.info("Настройка логирования завершена")
    start_date = datetime(1984, 2, 21)
    end_date = datetime(1984, 2, 21)  # 30 дней для примера
    base_url = 'http://tvp.netcollect.ru/prog_day.php'

    # Инициализация компонентов
    date_generator = DateRangeGenerator(start_date, end_date)
    url_generator = URLGenerator(base_url)
    data_fetcher = DataFetcher(
        timeout=PARSER_CONFIG['timeout'],
        user_agents=[
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
    )

    total_processed = 0
    total_errors = 0

    try:
        for date in date_generator.generate_dates():
            url = url_generator.generate_url(date)
            logging.info(f"Обработка даты: {date.strftime('%Y-%m-%d')}")

            # Пауза вежливости перед запросом
            delay = random.uniform(*PARSER_CONFIG['request_delay'])
            logging.debug(f"Пауза {delay:.2f} сек перед запросом")
            time.sleep(delay)

            # Повторные попытки при ошибках
            for attempt in range(PARSER_CONFIG['max_retries']):
                try:
                    html_data = data_fetcher.fetch_data(url)
                    if not html_data:
                        raise ValueError("Пустой ответ от сервера")

                    if "не найдена" in html_data.lower():
                        logging.warning("Страница сообщает об отсутствии данных")
                        break

                    logging.debug(f"Размер HTML: {len(html_data)} символов")

                    # Сохраняем HTML для отладки
                    with open(f"debug_{date.strftime('%Y%m%d')}.html", "w", encoding="utf-8") as f:
                        f.write(html_data)

                    parse_and_save_tvp(html_data, date, save_to_db=save_to_db)
                    # parse_data_tvp.parse_and_save_tvp(html_data, date, False)
                    # parse_data_tvp(html_data,date)
                    total_processed += 1
                    break  # Успешный парсинг, выходим из цикла попыток

                except Exception as e:
                    if attempt < PARSER_CONFIG['max_retries'] - 1:
                        logging.warning(
                            f"Попытка {attempt + 1} не удалась. Ошибка: {str(e)}. "
                            f"Повтор через {PARSER_CONFIG['retry_delay']} сек..."
                        )
                        time.sleep(PARSER_CONFIG['retry_delay'])
                    else:
                        logging.error(
                            f"Не удалось обработать дату {date.strftime('%Y-%m-%d')} "
                            f"после {PARSER_CONFIG['max_retries']} попыток. Ошибка: {str(e)}"
                        )
                        total_errors += 1

    except KeyboardInterrupt:
        logging.info("Парсинг прерван пользователем")
    except Exception as e:
        logging.critical(f"Критическая ошибка: {str(e)}", exc_info=True)
    finally:
        logging.info(
            f"\nИтоги:\n"
            f"Обработано дат: {total_processed}\n"
            f"Ошибок: {total_errors}\n"
            f"Завершено: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )


if __name__ == "__main__":

    # Временное включение подробного лога
    debug_mode = True  # Можно сделать запрос через input()

    if debug_mode:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Включен режим отладки (DEBUG)")
    else:
        logging.getLogger().setLevel(logging.INFO)

    main()
