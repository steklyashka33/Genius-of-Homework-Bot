from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

main_kb = [
    [
        KeyboardButton(text="hi"),
        KeyboardButton(text="Как дела?"),
     ],
    [
        KeyboardButton(text="Info"),
    ]
]

main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           one_time_keyboard=True,
                           input_field_placeholder="Выберите действие:")