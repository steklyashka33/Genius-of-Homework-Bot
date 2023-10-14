from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

main_kb = [
    [
        KeyboardButton(text="Домашнее задание📕"),
     ],
    [
        KeyboardButton(text="Профиль👤"),
        KeyboardButton(text="Информацияℹ"),
    ]
]

main = ReplyKeyboardMarkup(keyboard=main_kb,
                           resize_keyboard=True,
                           one_time_keyboard=True,
                           input_field_placeholder="Выберите действие:")