from operator import methodcaller

class Ticket:
    def __init__(self):
        """Contains  notes, times, expenses for a ticketed job or event"""
        self.name = ''
        self.type = ''
        self.track_list = []
        self.hours_list = []
        self.expenses_list = []
        self.notes = None

    def set_name(self, name):
        self.name = name

    def set_type(self, type):
        self.type = type

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def set_notes(self, notes):
        self.notes = notes

    def get_notes(self):
        return self.notes

    def add_track(self, track):
        self.track_list.append(track)
        self.sort()

    def delete_track(self, track):
        print('track', track)
        del self.track_list[track]
        self.sort()
        return

    def get_tracks(self):
        return self.track_list

    def sort(self):
        self.track_list.sort(key=methodcaller('get_start'))
        return

    def get_expenses(self):
        return self.expenses_list




class Track:
    def __init__(self, start, end, hours, miles, notes, brush, gps):
        """Start, end, hours and miles - from GPS or manually added"""
        self.start = start
        self.end = end
        self.hours = hours
        self. miles = miles
        self.notes = notes
        self.brush = brush
        self.gps = gps

    def get_start(self):
        return self.start

    def get_end(self):
        return self.end

    def get_hours(self):
        return self.hours

    def get_miles(self):
        return self.miles

    def get_notes(self):
        return self.notes

    def get_brush(self):
        return self.brush

    def get_colour(self):
        colour = self.brush.color()
        colour = str(colour.getRgb())
        return colour

    def get_gps(self):
        return self.gps
    
    def set_start(self, start):
        self.start = start

    def set_end(self, end):
        self.end = end

    def set_hours(self, hours):
        self.hours = hours

    def set_miles(self, miles):
        self.miles = miles

    def set_notes(self, notes):
        self.notes = notes

    def set_all(self, start, end, hours, miles, notes):
        self.start = start
        self.end = end
        self.hours = hours
        self.miles = miles
        self.notes = notes


class Expense:
    def __init__(self, item, cost):
        """Expenses"""
