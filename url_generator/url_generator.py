class URLGenerator:
    def __init__(self, base_url):
        self.base_url = base_url

    def generate_url(self, date):
        formatted_date = date.strftime('%d.%m.%Y')
        formatted_year = date.strftime('%Y')
        formatted_month = date.strftime('%m')
        formatted_day = date.strftime('%d')
        # return f'{self.base_url}?func=2&date_show={formatted_date}'
        return f"{self.base_url}?y={formatted_year}&m={formatted_month}&d={formatted_day}"
