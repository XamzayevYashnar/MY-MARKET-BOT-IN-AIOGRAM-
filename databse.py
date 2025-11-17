import sqlite3

class Database:
    def __init__(self, db_name):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # Users jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                phone TEXT NOT NULL,
                username_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Categories jadvali
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                category_name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                category_id INTEGER,
                image TEXT,
                product_name TEXT NOT NULL,
                product_description TEXT,
                product_price REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                product_id INTEGER,
                quantity INTEGER,
                total_price REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        self.connection.commit()
        print("DEBUG DATABASE - All tables created successfully")

    def add_user(self, name, age, phone, username_id):
        self.cursor.execute('''
            INSERT INTO users (name, age, phone, username_id) VALUES (?, ?, ?, ?)
        ''', (name, age, phone, username_id))
        self.connection.commit()

    def get_users(self):
        self.cursor.execute('SELECT * FROM users')
        return self.cursor.fetchall()
    
    def check_user(self, username_id):
        self.cursor.execute('SELECT * FROM users WHERE username_id = ?', (username_id,))
        return self.cursor.fetchone()

    def add_category(self, category_name):
        self.cursor.execute('''
            INSERT INTO categories (category_name) VALUES (?)
        ''', (category_name,))
        self.connection.commit()

    def check_category(self, category_name):
        self.cursor.execute('SELECT * FROM categories WHERE category_name = ?', (category_name,))
        return self.cursor.fetchone()

    def get_all_categories(self):
        self.cursor.execute('SELECT * FROM categories')
        return self.cursor.fetchall()

    def add_product(self, category_id, product_name, product_description, product_price, image_data=None):
        print(f"🚀 DEBUG DATABASE - ADD_PRODUCT CALLED:")
        print(f"   📍 Category ID: {category_id}")
        print(f"   📦 Product Name: {product_name}")
        print(f"   🖼️ Image data type: {type(image_data)}")
        print(f"   🖼️ Image data length: {len(image_data) if image_data else 0}")
        print(f"   📝 Description: {product_description}")
        print(f"   💵 Price: {product_price}")
        
        try:
            self.cursor.execute('''
                INSERT INTO products (category_id, image, product_name, product_description, product_price) 
                VALUES (?, ?, ?, ?, ?)
            ''', (category_id, image_data, product_name, product_description, product_price))
            self.connection.commit()
            print("✅ DEBUG DATABASE - Product inserted successfully")
            
            # Qo'shilgan mahsulotni tekshirish
            self.cursor.execute('SELECT * FROM products WHERE product_name = ?', (product_name,))
            result = self.cursor.fetchone()
            print(f"🔍 DEBUG DATABASE - VERIFICATION - Added product from DB:")
            print(f"   📍 Full result: {result}")
            if result:
                print(f"   🆔 ID: {result[0]}")
                print(f"   📍 Category ID: {result[1]}")
                print(f"   🖼️ Image from DB type: {type(result[2])}")
                print(f"   🖼️ Image from DB length: {len(result[2]) if result[2] else 0}")
                print(f"   📦 Name: {result[3]}")
                print(f"   📝 Description: {result[4]}")
                print(f"   💵 Price: {result[5]}")
            else:
                print("❌ DEBUG DATABASE - Product not found after insertion!")
            
            return result
            
        except Exception as e:
            print(f"❌ DEBUG DATABASE - ERROR in add_product: {e}")
            raise

    def get_all_products(self):
        self.cursor.execute('SELECT * FROM products')
        results = self.cursor.fetchall()
        print(f"🔍 DEBUG DATABASE - ALL PRODUCTS IN DB:")
        for product in results:
            print(f"   📦 {product[3]} - 🖼️ BLOB length: {len(product[2]) if product[2] else 0}")
        return results

    def check_product(self, product_name):
        self.cursor.execute('SELECT * FROM products WHERE product_name = ?', (product_name,))
        result = self.cursor.fetchone()
        print(f"🔍 DEBUG DATABASE - CHECK_PRODUCT '{product_name}':")
        if result:
            print(f"   ✅ Found: ID={result[0]}, BLOB length={len(result[2]) if result[2] else 0}")
        else:
            print(f"   ❌ Not found")
        return result

    def get_products_by_category(self, category_name):
        self.cursor.execute('''
            SELECT p.* 
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE c.category_name = ?
        ''', (category_name,))
        results = self.cursor.fetchall()
        print(f"🔍 DEBUG DATABASE - PRODUCTS BY CATEGORY '{category_name}':")
        for product in results:
            print(f"   📦 {product[3]} - 🖼️ BLOB length: {len(product[2]) if product[2] else 0}")
        return results

    def get_product_by_id(self, product_id):
        self.cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
        result = self.cursor.fetchone()
        return result

    def add_order(self, user_id, product_id, quantity, total_price, status='pending'):
        self.cursor.execute('''
            INSERT INTO orders (user_id, product_id, quantity, total_price, status) 
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, product_id, quantity, total_price, status))
        self.connection.commit()
        return self.cursor.lastrowid

    def get_user_orders(self, user_id):
        self.cursor.execute('''
            SELECT o.*, p.product_name, p.product_price 
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC
        ''', (user_id,))
        return self.cursor.fetchall()

    def get_all_orders(self):
        self.cursor.execute('''
            SELECT o.*, u.name, u.phone, p.product_name 
            FROM orders o
            JOIN users u ON o.user_id = u.id
            JOIN products p ON o.product_id = p.id
            ORDER BY o.created_at DESC
        ''')
        return self.cursor.fetchall()

    def update_order_status(self, order_id, status):
        self.cursor.execute('''
            UPDATE orders SET status = ? WHERE id = ?
        ''', (status, order_id))
        self.connection.commit()

    def close(self):
        self.connection.close()


class Category:
    def __init__(self, db_name):
        self.db = Database(db_name)

    def create_table(self):
        pass

    def add_category(self, category_name):
        self.db.add_category(category_name)

    def check_category(self, category_name):
        return self.db.check_category(category_name)

    def get_all_categories(self):
        return self.db.get_all_categories()

    def close(self):
        self.db.close()

class Product:
    def __init__(self, db_name):
        self.db = Database(db_name)

    def create_table(self):
        pass

    def add_product(self, category_id, product_name, product_description, product_price, image_data=None):
        return self.db.add_product(category_id, product_name, product_description, product_price, image_data)

    def get_all_products(self):
        return self.db.get_all_products()

    def check_product(self, product_name):
        return self.db.check_product(product_name)

    def get_products_by_category(self, category_name):
        return self.db.get_products_by_category(category_name)

    def get_product_by_id(self, product_id):
        return self.db.get_product_by_id(product_id)

    def close(self):
        self.db.close()