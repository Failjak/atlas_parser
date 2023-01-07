import datetime


def generate_final_route(arrival_place, departure_place, date):
    return f"{date.strftime('%Y-%m-%d') if isinstance(date, datetime.date) else date} " \
           f"{departure_place.capitalize()} --> {arrival_place.capitalize()}"
