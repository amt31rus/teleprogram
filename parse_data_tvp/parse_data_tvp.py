from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup, Comment, Tag
import re
from datetime import datetime
import logging

from bs4 import BeautifulSoup
import re
from datetime import datetime
from typing import List, Dict
from bs4 import Comment  # Для удаления комментариев


def parse_tvp(html: str, date: datetime) -> List[Dict[str, str]]:
    """Парсит телепрограмму, обрабатывая все каналы"""
    soup = BeautifulSoup(html, 'html.parser')
    programs = []
    current_channel = None

    for prog_block in soup.find_all('div', class_='prog_text'):
        # Получаем все содержимое блока как текст
        block_text = prog_block.get_text('\n')
        lines = [line.strip() for line in block_text.split('\n') if line.strip()]

        i = 0
        while i < len(lines):
            line = lines[i]

            # Определяем канал по ключевым словам
            if any(chan in line for chan in
                   ['Первая программа', 'Вторая программа', 'Четвёртая программа', 'Московская программа']):
                current_channel = line
                i += 1
                # Пропускаем строку с датой если она следует за каналом
                if i < len(lines) and re.match(r'\d{1,2}\s+[а-я]+\s+\d{4}', lines[i]):
                    i += 1
                continue

            if current_channel:
                # Улучшенное регулярное выражение для времени и описания
                match = re.match(
                    r'(\d{1,2}[.:]\d{2}(?:,\s*\d{1,2}[.:]\d{2})*)\s*[-\u2013\u2014]\s*(.+)',
                    line
                )
                if match:
                    times_str, description = match.groups()
                    for time in re.split(r'\s*,\s*', times_str):
                        time = time.strip().replace('.', ':')
                        try:
                            hour, minute = map(int, time.split(':'))
                            program_time = datetime(date.year, date.month, date.day, hour, minute)
                            if hour < 5:  # Коррекция через полночь
                                program_time += timedelta(days=1)

                            programs.append({
                                'channel': current_channel,
                                'time': program_time,
                                'description': description.strip()
                            })
                        except ValueError:
                            continue
            i += 1

    return programs

def save_programs_to_db(programs: List[Dict[str, Any]], connection) -> int:
    """
    Сохраняет программы в БД.
    Возвращает количество сохраненных записей.
    """
    if not programs or not connection:
        return 0

    saved_count = 0
    try:
        with connection.cursor() as cur:
            for program in programs:
                cur.execute(
                    """INSERT INTO oldtvprogram 
                    (current_program, program_datetime, program_description)
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING""",
                    (program['channel'], program['time'], program['description'])
                )
                saved_count += cur.rowcount
        connection.commit()
    except Exception as e:
        logging.error(f"Ошибка сохранения в БД: {str(e)}")
        connection.rollback()
        return 0

    return saved_count

def parse_and_save_tvp(html: str, date: datetime, save_to_db: bool = False):
    """
    Модифицированная версия:
    - При save_to_db=False только парсит и показывает результат
    - При save_to_db=True сохраняет в БД
    """
    programs = parse_tvp(html, date)  # Основной парсинг
    for prog in programs:
        print(f"{prog['time']} | {prog['channel']} | {prog['description']}")

    # Вывод результатов в любом случае
    logging.info(f"Найдено программ: {len(programs)}")
    for prog in programs[:3]:  # Показываем первые 3 для примера
        logging.info(f"{prog['time'].time()} [{prog['channel']}] {prog['description'][:50]}...")

    # Сохранение в БД (если включено)
    if save_to_db:
        from database.db_connector import connect_to_database
        with connect_to_database() as conn:
            with conn.cursor() as cur:
                for prog in programs:
                    cur.execute(
                        """INSERT INTO oldtvprogram 
                        (current_program, program_datetime, program_description)
                        VALUES (%s, %s, %s)
                        ON CONFLICT DO NOTHING""",
                        (prog['channel'], prog['time'], prog['description'])
                    )
                conn.commit()
        logging.info(f"Сохранено в БД: {len(programs)} программ")