from datetime import datetime
from data_fetcher.data_fetcher import DataFetcher
from parse_data.parse_data import parse_data
from url_generator.url_generator import URLGenerator
from date_range_generator.date_range_generator import DateRangeGenerator

start_date = datetime(1978, 1, 1)
end_date = datetime(1978, 1, 1)
# base_url = 'https://20vek.net/index.php'
base_url = 'http://tvp.netcollect.ru/prog_day.php'

date_generator = DateRangeGenerator(start_date, end_date)
url_generator = URLGenerator(base_url)
data_fetcher = DataFetcher()

for date in date_generator.generate_dates():
    url = url_generator.generate_url(date)
    data = data_fetcher.fetch_data(url)
    print (url)
    programs = parse_data(data, date)
    # print (programs)
    # Добавьте вашу обработку полученных данных здесь