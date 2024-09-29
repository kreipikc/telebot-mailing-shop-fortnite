from typing import List
import datetime

def transform_date() -> List[str]:
    date = datetime.datetime.now().strftime('%d-%m-%Y')
    months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    day, month, year = date.split('-')
    return [days[datetime.datetime.today().weekday()], day, months[int(month) - 1], year]