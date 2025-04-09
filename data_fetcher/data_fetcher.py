import requests


class DataFetcher:
    def fetch_data(self, url):
        response = requests.get(url)
        response.encoding = 'utf-8'

        html_content = response.text

        # Ваш код обработки ответа
        # print (response.text)
        return response.text
