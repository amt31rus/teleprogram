import re
from datetime import datetime

from bs4 import BeautifulSoup
from database.db_connector import connect_to_database
from database.db_connector import create_program_table


def parse_data(html, date):
    soup = BeautifulSoup(html, 'html.parser')
    # soup = BeautifulSoup(html, 'html.parser', from_encoding='utf-8')
    table = soup.find('table')  # Находим таблицу с программой
    if table:
        rows = table.find_all('tr')  # Получаем все строки таблицы
        programs = []
        conn = connect_to_database()
        create_program_table(conn)
        current_program = None
        for row in rows:
            if row.find('b'):
                current_program = row.text.strip()  # Получаем название программы
            else:
                cells = row.find_all('td')
                if len(cells) >= 1:
                    # Используем регулярное выражение для разделения времени и описания программы
                    match = re.match(r'^(\d{1,2}:\d{2}) - (.*)$', cells[0].text.strip())
                    if match:
                        time = match.group(1)
                        description = match.group(2)
                        date_time_str = date.strftime("%Y-%m-%d %H:%M:%S")
                        date_components = date_time_str.split(' ')
                        date_date = date_components[0]  # '1982-01-01'

                        # Разбиваем строку date_date на год, месяц и день
                        year, month, day = map(int, date_date.split('-'))

                        # Разбиваем строку time_str на часы и минуты
                        hour, minute = map(int, time.split(':'))

                        # Создаем объект datetime
                        dt = datetime(year, month, day, hour, minute)

                        # Преобразуем datetime в строку в нужном формате для Postgres
                        formatted_datetime = dt.strftime("%Y-%m-%d %H:%M:%S")

                        # Печатаем результат

                        # programs.append(f"{current_program}|{formatted_datetime}|{description}")
                        # with conn.cursor() as cur:
                        #    cur.execute(
                        #        'INSERT INTO oldtvprogram (current_program, program_datetime, program_description) VALUES '
                        #        '(%s, %s, %s)',
                        #        (current_program, formatted_datetime, description)
                        #    )
                        #    conn.commit()
        print(date)
        conn.close()

        return programs
    else:
        return None
