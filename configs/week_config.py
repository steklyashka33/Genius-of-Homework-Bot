from typing import Union

class Week:
    # В винительном подеже
    Monday = "Понедельник"
    Tuesday = "Вторник"
    Wednesday = "Среду"
    Thursday = "Четверг"
    Friday = "Пятницу"
    Saturday = "Субботу"
    Sunday = "Воскресенье"
    
    Mon = "пн"
    Tue = "вт"
    Wed = "ср"
    Thu = "чт"
    Fri = "пт"
    Sat = "сб"
    Sun = "вс"

    days_of_week_dict = {
        1: [Monday, Mon],
        2: [Tuesday, Tue],
        3: [Wednesday, Wed],
        4: [Thursday, Thu],
        5: [Friday, Fri],
        6: [Saturday, Sat],
        7: [Sunday, Sun]
    }

    @classmethod
    async def day_to_number(cls, day_name: str) -> Union[int, None]:
        for day_number, day_names in cls.days_of_week_dict.items():
            if day_name in day_names:
                return day_number