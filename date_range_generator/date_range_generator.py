from datetime import datetime, timedelta

class DateRangeGenerator:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def generate_dates(self):
        current_date = self.start_date
        while current_date <= self.end_date:
            yield current_date
            current_date += timedelta(days=1)