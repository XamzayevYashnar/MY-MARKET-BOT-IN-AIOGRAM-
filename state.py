from aiogram.fsm.state import State, StatesGroup

class CategoryState(StatesGroup):
    new_category_name = State()
    product_category_name = State()

class ProductState(StatesGroup):
    product_name = State()
    product_description = State()
    product_price = State()
    product_image = State()

class OrderState(StatesGroup):
    user_name = State()
    user_age = State()
    user_phone = State()
    product_selection = State()
    quantity_selection = State()

class ProductOrderState(StatesGroup):
    category_selection = State()
    product_selection = State()
    product_name = State()
    quantity = State()
    confirmation = State()

class UserRegistrationState(StatesGroup):
    name = State()
    age = State()
    phone = State()