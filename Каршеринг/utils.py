#utils.py
#Вспомогательные функции

def format_time(time_str):
    """Форматирование времени из БД"""
    if not time_str:
        return ""
    try:
        #Время может быть в формате HH:MM:SS или секунды
        if isinstance(time_str, str):
            return time_str
        elif isinstance(time_str, int):
            hours = time_str // 3600
            minutes = (time_str % 3600) // 60
            seconds = time_str % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return str(time_str)
    except:
        return str(time_str)