-- Название: Поиск дат без данных в oldtvprogram
-- Автор: Тараканов Александр
-- Дата создания: 2024-04-15
-- Описание: Возвращает даты из заданного диапазона, для которых нет записей в таблице oldtvprogram.

WITH date_range AS (
    SELECT generate_series(
        '{start_date}'::timestamp,  -- Начальная дата диапазона
        '{end_date}'::timestamp,  -- Конечная дата диапазона
        '1 day'::interval
    )::date AS missing_date
)
SELECT dr.missing_date
FROM date_range dr
LEFT JOIN oldtvprogram otp ON dr.missing_date = otp.program_datetime::date
WHERE otp.id IS NULL
ORDER BY dr.missing_date;