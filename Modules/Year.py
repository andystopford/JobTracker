
import calendar
import itertools


class Year:
    def __init__(self, parent, year):
        """ Make list of the year's dates sorted by month to set up model
        display"""
        self.cal = calendar.Calendar()
        self.year = year
        self.parent = parent

    def get_months(self):
        month_list = []
        for month in range(1, 13):
            days = self.cal.monthdayscalendar(self.year, month)
            days = list(itertools.chain(*days))  # 12 lists of dates
            for n, i in enumerate(days):
                if i == 0:
                    days[n] = ''  # Removes Zeros at beginning of month
            days += [''] * (37 - len(days))  # pads list to fill table
            month_list.append(days)
        return month_list

    def get_column(self, month, day):
        days = self.cal.monthdayscalendar(int(self.year), month)
        merged = list(itertools.chain.from_iterable(days))
        col = merged.index(day)
        return col





