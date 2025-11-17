import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command

from databse import Database
from state import CategoryState, ProductState, OrderState, ProductOrderState, UserRegistrationState
from default import (
    main_keyboard, 
    register_keyboard, 
    admin_keyboard,
    phone_request_keyboard,
    get_category_keyboard,
    get_category_keyboard_for_admin,
    get_products_by_category,
    get_cancel_keyboard,
    get_back_keyboard,
    get_order_confirmation_keyboard,
    get_admin_products_keyboard,
    get_admin_categories_keyboard
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8253333514:AAFuHbRZ9fa87mcfsxVD3CEovZ5L2oEarAk"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

from keep_alive import keep_alive
keep_alive()

db = Database("shop_bot.db")

ADMIN_ID = "788842777"

def is_admin(user_id: str) -> bool:
    return user_id == ADMIN_ID

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await state.clear()
    
    user_id = str(message.from_user.id)
    
    user = db.check_user(user_id)
    
    if is_admin(user_id):
        await message.answer(
            f"Xush kelibsiz, Admin! 👑",
            reply_markup=admin_keyboard()
        )
    elif user:
        await message.answer(
            f"Xush kelibsiz, {user[1]}! 🎉",
            reply_markup=main_keyboard()
        )
    else:
        await message.answer(
            "Assalomu alaykum! Botimizga xush kelibsiz. 🤗\n"
            "Buyurtma berish uchun avval ro'yxatdan o'ting.",
            reply_markup=register_keyboard()
        )

@router.message(F.text == "📝 Ro'yxatdan o'tish")
async def start_registration(message: Message, state: FSMContext):
    await message.answer("Ismingizni kiriting:")
    await state.set_state(UserRegistrationState.name)

@router.message(UserRegistrationState.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Yoshingizni kiriting:")
    await state.set_state(UserRegistrationState.age)

@router.message(UserRegistrationState.age)
async def process_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        if age < 10 or age > 100:
            await message.answer("Iltimos, to'g'ri yosh kiriting (10-100):")
            return
        await state.update_data(age=age)
        
        phone_keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="📞 Telefon raqamni yuborish", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer("Telefon raqamingizni yuboring:", reply_markup=phone_keyboard)
        await state.set_state(UserRegistrationState.phone)
        
    except ValueError:
        await message.answer("Iltimos, raqam kiriting:")

@router.message(UserRegistrationState.phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    phone = message.contact.phone_number
    await process_user_registration(message, state, phone)

@router.message(UserRegistrationState.phone)
async def process_phone_text(message: Message, state: FSMContext):
    phone = message.text
    await process_user_registration(message, state, phone)

async def process_user_registration(message: Message, state: FSMContext, phone: str):
    data = await state.get_data()
    
    name = data.get('name')
    age = data.get('age')
    username_id = str(message.from_user.id)
    
    try:
        db.add_user(name, age, phone, username_id)
        
        if is_admin(username_id):
            keyboard = admin_keyboard()
        else:
            keyboard = main_keyboard()
            
        await message.answer(
            f"✅ Ro'yxatdan muvaffaqiyatli o'tdingiz!\n"
            f"👤 Ism: {name}\n"
            f"🎂 Yosh: {age}\n"
            f"📞 Telefon: {phone}",
            reply_markup=keyboard
        )
    except Exception as e:
        await message.answer("Ro'yxatdan o'tishda xatolik yuz berdi. Qayta urinib ko'ring.")
    
    await state.clear()

@router.message(F.text == "➕ Mahsulot qo'shish")
async def add_product_handler(message: Message, state: FSMContext):
    if not is_admin(str(message.from_user.id)):
        await message.answer("Sizga ruxsat yo'q! ❌", reply_markup=main_keyboard())
        return
        
    await state.clear()
    
    categories = db.get_all_categories()
    if not categories:
        await message.answer("Avval kategoriya qo'shing.", reply_markup=admin_keyboard())
        return
    
    category_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=category[1])] for category in categories],
        resize_keyboard=True
    )
    
    await message.answer("Kategoriya tanlang🍕:", reply_markup=category_keyboard)
    await state.set_state(CategoryState.product_category_name)

@router.message(CategoryState.product_category_name)
async def process_category_for_product(message: Message, state: FSMContext):
    if not is_admin(str(message.from_user.id)):
        await message.answer("Sizga ruxsat yo'q! ❌", reply_markup=main_keyboard())
        await state.clear()
        return
        
    category_name = message.text
    category = db.check_category(category_name)
    if not category:
        await message.answer("Kategoriya topilmadi😔. Iltimos, to'g'ri kategoriya nomini kiriting😁:")
        return
    await state.update_data(category_name=category_name, category_id=category[0])
    await message.answer("Mahsulot nomini kiriting😊:", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Bekor qilish")]],
        resize_keyboard=True
    ))
    await state.set_state(ProductState.product_name)

@router.message(ProductState.product_name)
async def process_product_name(message: Message, state: FSMContext):
    if not is_admin(str(message.from_user.id)):
        await message.answer("Sizga ruxsat yo'q! ❌", reply_markup=main_keyboard())
        await state.clear()
        return
        
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("Amal bekor qilindi.", reply_markup=admin_keyboard())
        return
        
    await state.update_data(product_name=message.text)
    await message.answer("Mahsulot tavsifini kiriting☺️:")
    await state.set_state(ProductState.product_description)

@router.message(ProductState.product_description)
async def process_product_description(message: Message, state: FSMContext):
    if not is_admin(str(message.from_user.id)):
        await message.answer("Sizga ruxsat yo'q! ❌", reply_markup=main_keyboard())
        await state.clear()
        return
        
    await state.update_data(product_description=message.text)
    await message.answer("Mahsulot narxini kiriting💵:")
    await state.set_state(ProductState.product_price)

@router.message(ProductState.product_price)
async def process_product_price(message: Message, state: FSMContext):
    if not is_admin(str(message.from_user.id)):
        await message.answer("Sizga ruxsat yo'q! ❌", reply_markup=main_keyboard())
        await state.clear()
        return
        
    try:
        price = float(message.text)
        if price <= 0:
            await message.answer("Narx 0 dan katta bo'lishi kerak😊. Qaytadan kiriting:")
            return
        await state.update_data(product_price=price)
        await message.answer("Mahsulot rasm linkini yuboring🖼️ (URL):")
        await state.set_state(ProductState.product_image)
    except ValueError:
        await message.answer("Iltimos, raqam kiriting💵:")

@router.message(ProductState.product_image)
async def process_product_image(message: Message, state: FSMContext):
    if not is_admin(str(message.from_user.id)):
        await message.answer("Sizga ruxsat yo'q! ❌", reply_markup=main_keyboard())
        await state.clear()
        return

    # agar rasm yuborilgan bo'lsa, uning file_id ni olamiz
    image_value = None
    if message.photo:  # foto sifatida yuborgan bo'lsa
        image_value = message.photo[-1].file_id
        image_source = "file_id"
    else:
        # agar matn yuborilgan bo'lsa, ehtimol URL
        text = (message.text or "").strip()
        if text:
            image_value = text
            image_source = "url"
        else:
            await message.answer("Iltimos, rasm yuboring yoki rasm linkini kiritng 🖼️:")
            return

    data = await state.get_data()
    category_id = data.get("category_id")
    product_name = data.get("product_name")
    product_description = data.get("product_description")
    product_price = data.get("product_price")
    category_name = data.get("category_name")  # agar kerak bo'lsa

    try:
        # DB funksiyangizga image_value yuboring — DB da bu string sifatida saqlanishi kerak
        db.add_product(category_id, product_name, product_description, product_price, image_value)

        # Xabar: rasm file_id yoki url qay tarzda saqlanganini ko'rsatish
        saved_repr = f"📎 Rasm turi: {image_source}"
        await message.answer(
            (
                f"✅ Mahsulot qo'shildi:\n"
                f"🍕 Kategoriya: {category_name}\n"
                f"📦 Nomi: {product_name}\n"
                f"📝 Tavsifi: {product_description}\n"
                f"💵 Narxi: {product_price}\n"
                f"🖼️ Rasm: {image_value}\n\n"
                f"{saved_repr}"
            ),
            reply_markup=admin_keyboard()
        )
    except Exception as e:
        await message.answer(f"Xatolik yuz berdi😔: {str(e)}")

    await state.clear()

@router.message(F.text == "🛍️ Mahsulotlar")
async def show_products_handler(message: Message, state: FSMContext):
    await state.clear()
    
    user = db.check_user(str(message.from_user.id))
    if not user:
        await message.answer("Iltimos, avval ro'yxatdan o'ting!", reply_markup=register_keyboard())
        return
    
    categories = db.get_all_categories()
    
    if not categories:
        await message.answer("Hozircha kategoriyalar mavjud emas😔", reply_markup=main_keyboard())
        return
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=category[1])] for category in categories] + [[KeyboardButton(text="🏠 Asosiy menyu")]],
        resize_keyboard=True
    )
    
    await message.answer("Kategoriya tanlang🍕:", reply_markup=keyboard)
    await state.set_state(ProductOrderState.category_selection)

@router.message(ProductOrderState.category_selection)
async def process_category_selection(message: Message, state: FSMContext):
    if message.text == "🏠 Asosiy menyu":
        await state.clear()
        user_id = str(message.from_user.id)
        if is_admin(user_id):
            await message.answer("Asosiy menyu:", reply_markup=admin_keyboard())
        else:
            await message.answer("Asosiy menyu:", reply_markup=main_keyboard())
        return
        
    category_name = message.text
    category = db.check_category(category_name)
    
    if not category:
        await message.answer("Kategoriya topilmadi😔. Iltimos, ro'yxatdan tanlang:")
        return
    
    products = db.get_products_by_category(category_name)
    
    if not products:
        await message.answer("Bu kategoriyada hozircha mahsulotlar mavjud emas😔", reply_markup=main_keyboard())
        await state.clear()
        return
    
    products_keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=product[3])] for product in products] + [
            [KeyboardButton(text="⬅️ Orqaga"), KeyboardButton(text="🏠 Asosiy menyu")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(f"'{category_name}' kategoriyasidagi mahsulotlar:", reply_markup=products_keyboard)
    await state.set_state(ProductOrderState.product_selection)

@router.message(ProductOrderState.product_selection)
async def process_product_selection(message: Message, state: FSMContext):
    if message.text == "🏠 Asosiy menyu":
        await state.clear()
        user_id = str(message.from_user.id)
        if is_admin(user_id):
            await message.answer("Asosiy menyu:", reply_markup=admin_keyboard())
        else:
            await message.answer("Asosiy menyu:", reply_markup=main_keyboard())
        return
    elif message.text == "⬅️ Orqaga":
        await show_products_handler(message, state)
        return
    
    product_name = message.text
    product = db.check_product(product_name)
    
    if not product:
        await message.answer("Mahsulot topilmadi😔. Iltimos, ro'yxatdan tanlang:")
        return
    
    await state.update_data(
        product_name=product[3],
        product_id=product[0],
        product_price=product[5],
        product_image=product[2],
        product_description=product[4]
    )
    
    product_id, category_id, image, name, description, price, created_at = product
    
    await state.update_data(product_count=1)
    
    caption = f"""
🛍️ {name}
📝 {description}
💵 Narxi: {price} so'm
🔢 Soni: 1
💰 Jami: {price} so'm
"""
    
    keyboard = InlineKeyboardMarkup(
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
    
    if image:
        try:
            await message.answer_photo(
                photo=image,
                caption=caption,
                reply_markup=keyboard
            )
        except:
            await message.answer(
                text=f"🖼️ {caption}",
                reply_markup=keyboard
            )
    else:
        await message.answer(
            text=caption,
            reply_markup=keyboard
        )

@router.callback_query(F.data.in_(["increase_count", "decrease_count", "confirm_order", "cancel_order"]))
async def handle_count_buttons(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_count = data.get('product_count', 1)
    product_price = data.get('product_price', 0)
    product_name = data.get('product_name', '')
    
    if callback.data == "increase_count":
        current_count += 1
        await state.update_data(product_count=current_count)
        
    elif callback.data == "decrease_count":
        if current_count > 1:
            current_count -= 1
            await state.update_data(product_count=current_count)
        else:
            await callback.answer("Soni 1 dan kam bo'lishi mumkin emas!", show_alert=True)
            return
    
    elif callback.data == "cancel_order":
        await callback.message.delete()
        user_id = str(callback.from_user.id)
        if is_admin(user_id):
            await callback.message.answer("Buyurtma bekor qilindi❌", reply_markup=admin_keyboard())
        else:
            await callback.message.answer("Buyurtma bekor qilindi❌", reply_markup=main_keyboard())
        await state.clear()
        return
    
    elif callback.data == "confirm_order":
        await confirm_order_handler(callback, state)
        return
    
    total_price = product_price * current_count
    
    caption = f"""
🛍️ {product_name}
💵 Narxi: {product_price} so'm
🔢 Soni: {current_count}
💰 Jami: {total_price} so'm
"""
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="➖", callback_data="decrease_count"),
                InlineKeyboardButton(text=str(current_count), callback_data="current_count"),
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
    
    try:
        if callback.message.photo:
            await callback.message.edit_caption(
                caption=caption,
                reply_markup=keyboard
            )
        else:
            await callback.message.edit_text(
                text=caption,
                reply_markup=keyboard
            )
    except Exception as e:
        await callback.answer("Yangilandi!", show_alert=False)
    
    await callback.answer()

async def confirm_order_handler(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    product_name = data.get('product_name')
    product_id = data.get('product_id')
    product_count = data.get('product_count', 1)
    product_price = data.get('product_price', 0)
    total_price = product_price * product_count
    
    user_id = callback.from_user.id
    user = db.check_user(str(user_id))
    
    if not user:
        await callback.message.answer("Iltimos, avval ro'yxatdan o'ting! /start")
        await state.clear()
        return
    
    try:
        order_id = db.add_order(
            user_id=user[0],
            product_id=product_id,
            quantity=product_count,
            total_price=total_price,
            status="pending"
        )
        
        success_message = f"""
✅ Buyurtma qabul qilindi!

📦 Mahsulot: {product_name}
🔢 Soni: {product_count}
💰 Jami: {total_price} so'm
📞 Buyurtma raqami: #{order_id}

Tez orada siz bilan bog'lanamiz!
"""
        
        if callback.message.photo:
            await callback.message.edit_caption(caption=success_message)
        else:
            await callback.message.edit_text(text=success_message)
        
    except Exception as e:
        error_message = "Buyurtma qabul qilinishida xatolik yuz berdi😔. Iltimos, qayta urinib ko'ring."
        if callback.message.photo:
            await callback.message.edit_caption(caption=error_message)
        else:
            await callback.message.edit_text(text=error_message)
    
    await state.clear()

@router.message(F.text == "📦 Buyurtmalarim")
async def show_my_orders(message: Message):
    user = db.check_user(str(message.from_user.id))
    if not user:
        await message.answer("Iltimos, avval ro'yxatdan o'ting!", reply_markup=register_keyboard())
        return
    
    orders = db.get_user_orders(user[0])
    
    if not orders:
        await message.answer("Sizda hali buyurtmalar mavjud emas😔", reply_markup=main_keyboard())
        return
    
    orders_text = "📦 Sizning buyurtmalaringiz:\n\n"
    for order in orders:
        orders_text += f"🆔 #{order[0]}\n"
        orders_text += f"📦 {order[8]}\n"  
        orders_text += f"🔢 Soni: {order[3]}\n"
        orders_text += f"💰 Jami: {order[4]} so'm\n"
        orders_text += f"📊 Holati: {order[5]}\n"
        orders_text += f"📅 Sana: {order[6]}\n"
        orders_text += "─" * 20 + "\n"
    
    await message.answer(orders_text, reply_markup=main_keyboard())

@router.message(F.text == "👥 Foydalanuvchilar")
async def show_users(message: Message):
    if not is_admin(str(message.from_user.id)):
        await message.answer("Sizga ruxsat yo'q! ❌", reply_markup=main_keyboard())
        return
        
    users = db.get_users()
    
    if not users:
        await message.answer("Hozircha foydalanuvchilar mavjud emas😔", reply_markup=admin_keyboard())
        return
    
    users_text = "👥 Foydalanuvchilar ro'yxati:\n\n"
    for user in users:
        users_text += f"👤 {user[1]}\n"
        users_text += f"🎂 Yosh: {user[2]}\n"
        users_text += f"📞 Tel: {user[3]}\n"
        users_text += f"🆔 ID: {user[4]}\n"
        users_text += "─" * 20 + "\n"
    
    await message.answer(users_text, reply_markup=admin_keyboard())

@router.message(F.text == "📊 Buyurtmalar")
async def show_all_orders(message: Message):
    if not is_admin(str(message.from_user.id)):
        await message.answer("Sizga ruxsat yo'q! ❌", reply_markup=main_keyboard())
        return
        
    orders = db.get_all_orders()
    
    if not orders:
        await message.answer("Hozircha buyurtmalar mavjud emas😔", reply_markup=admin_keyboard())
        return
    
    orders_text = "📊 Barcha buyurtmalar:\n\n"
    for order in orders:
        orders_text += f"🆔 #{order[0]}\n"
        orders_text += f"👤 {order[6]}\n"  
        orders_text += f"📞 {order[7]}\n"  
        orders_text += f"📦 {order[8]}\n"  
        orders_text += f"🔢 Soni: {order[3]}\n"
        orders_text += f"💰 Jami: {order[4]} so'm\n"
        orders_text += f"📊 Holati: {order[5]}\n"
        orders_text += "─" * 20 + "\n"
    
    await message.answer(orders_text, reply_markup=admin_keyboard())

@router.message(F.text == "🏠 Asosiy menyu")
async def main_menu(message: Message, state: FSMContext):
    await state.clear()
    user_id = str(message.from_user.id)
    if is_admin(user_id):
        await message.answer("Asosiy menyu:", reply_markup=admin_keyboard())
    else:
        await message.answer("Asosiy menyu:", reply_markup=main_keyboard())

@router.message(F.text == "ℹ️ Ma'lumot")
async def show_info(message: Message):
    user_id = str(message.from_user.id)
    if is_admin(user_id):
        reply_markup = admin_keyboard()
    else:
        reply_markup = main_keyboard()
        
    await message.answer(
        "🛍️ Onlayn do'kon boti\n\n"
        "Bizning bot orqali turli mahsulotlarni sotib olishingiz mumkin!\n\n"
        "📞 Aloqa: @your_username\n"
        "🌐 Vebsayt: example.com",
        reply_markup=reply_markup
    )

@router.message(F.text == "📞 Aloqa")
async def show_contact(message: Message):
    user_id = str(message.from_user.id)
    if is_admin(user_id):
        reply_markup = admin_keyboard()
    else:
        reply_markup = main_keyboard()
        
    await message.answer(
        "📞 Biz bilan bog'laning:\n\n"
        "📱 Telefon: +998901234567\n"
        "📧 Email: info@example.com\n"
        "📢 Telegram: @your_username\n"
        "📍 Manzil: Toshkent shahri",
        reply_markup=reply_markup
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())