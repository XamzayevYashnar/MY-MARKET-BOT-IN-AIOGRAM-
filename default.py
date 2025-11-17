from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from databse import Database

db = Database("shop_bot.db")


def main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍️ Mahsulotlar"), KeyboardButton(text="📦 Buyurtmalarim")],
            [KeyboardButton(text="ℹ️ Ma'lumot"), KeyboardButton(text="📞 Aloqa")]
        ],
        resize_keyboard=True
    )

def register_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Ro'yxatdan o'tish")]
        ],
        resize_keyboard=True
    )

def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Mahsulot qo'shish"), KeyboardButton(text="📦 Kategoriya qo'shish")],
            [KeyboardButton(text="👥 Foydalanuvchilar"), KeyboardButton(text="📊 Buyurtmalar")],
            [KeyboardButton(text="🛍️ Mahsulotlar"), KeyboardButton(text="🏠 Asosiy menyu")]
        ],
        resize_keyboard=True
    )

def phone_request_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📞 Telefon raqamni yuborish",
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_category_keyboard():
    categories = db.get_all_categories()

    if not categories:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Kategoriya mavjud emas😔")],
                [KeyboardButton(text="🏠 Asosiy menyu")]
            ],
            resize_keyboard=True
        )
    else:
        buttons = []
        for category in categories:
            buttons.append([KeyboardButton(text=category[1])])
        
        buttons.append([KeyboardButton(text="🏠 Asosiy menyu")])
        
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

def get_category_keyboard_for_admin():
    categories = db.get_all_categories()

    if not categories:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Kategoriya mavjud emas😔")],
                [KeyboardButton(text="❌ Bekor qilish")]
            ],
            resize_keyboard=True
        )
    else:
        buttons = []
        for category in categories:
            buttons.append([KeyboardButton(text=category[1])])
        
        buttons.append([KeyboardButton(text="❌ Bekor qilish")])
        
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )


def get_products_by_category(category_name):
    products = db.get_products_by_category(category_name)

    if not products:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Mahsulot mavjud emas😔")],
                [KeyboardButton(text="⬅️ Orqaga"), KeyboardButton(text="🏠 Asosiy menyu")]
            ],
            resize_keyboard=True
        )
    else:
        buttons = []
        for product in products:
            buttons.append([KeyboardButton(text=product[3])]) 
        buttons.append([
            KeyboardButton(text="⬅️ Orqaga"), 
            KeyboardButton(text="🏠 Asosiy menyu")
        ])
        
        return ReplyKeyboardMarkup(
            keyboard=buttons,
            resize_keyboard=True
        )

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True
    )

def get_back_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Orqaga"), KeyboardButton(text="🏠 Asosiy menyu")]
        ],
        resize_keyboard=True
    )

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_order_confirmation_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➖", callback_data="decrease_count"),
                InlineKeyboardButton(text="1", callback_data="current_count"),
                InlineKeyboardButton(text="➕", callback_data="increase_count")
            ],
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_order")
            ],
            [
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")
            ]
        ]
    )


def get_admin_products_keyboard():
    products = db.get_all_products()
    
    if not products:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Mahsulotlar mavjud emas")],
                [KeyboardButton(text="🏠 Asosiy menyu")]
            ],
            resize_keyboard=True
        )
    
    buttons = []
    for i in range(0, len(products), 2):
        row = []
        row.append(KeyboardButton(text=products[i][3]))  
        if i + 1 < len(products):
            row.append(KeyboardButton(text=products[i + 1][3]))
        buttons.append(row)
    
    buttons.append([KeyboardButton(text="🏠 Asosiy menyu")])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )

def get_admin_categories_keyboard():
    categories = db.get_all_categories()
    
    if not categories:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Kategoriyalar mavjud emas")],
                [KeyboardButton(text="🏠 Asosiy menyu")]
            ],
            resize_keyboard=True
        )
    
    buttons = []
    for category in categories:
        buttons.append([KeyboardButton(text=category[1])])
    
    buttons.append([KeyboardButton(text="🏠 Asosiy menyu")])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )