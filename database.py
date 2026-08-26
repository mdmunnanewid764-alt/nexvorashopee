import aiosqlite
import logging
from config import DATABASE_PATH, BINANCE_API_KEY, CURRENCY_NAME, CURRENCY_SYMBOL, SUPPORT_USERNAME, MIN_DEPOSIT

logger = logging.getLogger(__name__)

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("PRAGMA foreign_keys = ON;")
        
        # Users Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                balance REAL DEFAULT 0.0,
                total_deposited REAL DEFAULT 0.0,
                total_spent REAL DEFAULT 0.0,
                is_banned INTEGER DEFAULT 0,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration: add language column if missing
        try:
            await db.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'en'")
        except Exception:
            pass

        # Categories Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                emoji TEXT DEFAULT '📁',
                order_index INTEGER DEFAULT 0
            )
        """)

        # Products Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                image_url TEXT,
                delivery_type TEXT DEFAULT 'digital',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id) ON DELETE SET NULL
            )
        """)

        # Digital Stock Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS product_stock (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                item_data TEXT NOT NULL,
                is_sold INTEGER DEFAULT 0,
                sold_to_user_id INTEGER,
                sold_order_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sold_at TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
            )
        """)

        # Orders Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_code TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                total_price REAL NOT NULL,
                delivery_type TEXT DEFAULT 'digital',
                delivery_data TEXT,
                status TEXT DEFAULT 'COMPLETED',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        """)

        # Deposits Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                merchant_trade_no TEXT UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                order_amount REAL NOT NULL,
                currency TEXT DEFAULT 'USDT',
                status TEXT DEFAULT 'INITIAL',
                checkout_url TEXT,
                bep20_addr TEXT,
                trc20_addr TEXT,
                erc20_addr TEXT,
                paid_network TEXT,
                tx_hash TEXT,
                credited INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (telegram_id)
            )
        """)

        # Settings Table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)

        # Default Settings
        default_settings = [
            ("binance_api_key", BINANCE_API_KEY),
            ("currency_name", CURRENCY_NAME),
            ("currency_symbol", CURRENCY_SYMBOL),
            ("support_username", SUPPORT_USERNAME),
            ("min_deposit", str(MIN_DEPOSIT)),
            ("chatgpt_promo_enabled", "1"),
            ("chatgpt_promo_price", "1.00"),
            ("chatgpt_promo_title", "ChatGPT 3-Month Promo Offer"),
            ("chatgpt_promo_desc", "Special 3-Month ChatGPT Subscription Promo. Activate directly on your Gmail / Email.")
        ]
        for key, val in default_settings:
            await db.execute(
                "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                (key, val)
            )

        await db.commit()
    logger.info("Database initialized successfully.")


# --------------------- USER HELPERS ---------------------

async def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()
            if user:
                # Update username or first_name if changed
                if user["username"] != username or user["first_name"] != first_name:
                    await db.execute(
                        "UPDATE users SET username = ?, first_name = ? WHERE telegram_id = ?",
                        (username, first_name, telegram_id)
                    )
                    await db.commit()
                return dict(user)
            
            await db.execute(
                "INSERT INTO users (telegram_id, username, first_name, balance) VALUES (?, ?, ?, 0.0)",
                (telegram_id, username, first_name)
            )
            await db.commit()
            
            async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cur2:
                new_user = await cur2.fetchone()
                return dict(new_user)

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()
            return dict(user) if user else None

async def get_user_by_username(username: str):
    clean_user = username.replace("@", "").strip()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (clean_user,)) as cursor:
            user = await cursor.fetchone()
            return dict(user) if user else None

async def get_user_by_id_or_username(identifier: str):
    clean = str(identifier).replace("@", "").strip()
    if clean.isdigit():
        return await get_user(int(clean))
    return await get_user_by_username(clean)

async def get_user_language(telegram_id: int) -> str:
    user = await get_user(telegram_id)
    if user and user.get("language"):
        return user["language"]
    return "en"

async def set_user_language(telegram_id: int, language: str) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (language, telegram_id))
        await db.commit()
        return True

async def update_user_balance(telegram_id: int, amount: float, is_deposit: bool = False, is_spend: bool = False):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT balance, total_deposited, total_spent FROM users WHERE telegram_id = ?", (telegram_id,)) as cursor:
            user = await cursor.fetchone()
            if not user:
                return False
            
            new_balance = max(0.0, user["balance"] + amount)
            new_deposited = user["total_deposited"] + (amount if is_deposit and amount > 0 else 0)
            new_spent = user["total_spent"] + (abs(amount) if is_spend else 0)

            await db.execute("""
                UPDATE users 
                SET balance = ?, total_deposited = ?, total_spent = ? 
                WHERE telegram_id = ?
            """, (new_balance, new_deposited, new_spent, telegram_id))
            await db.commit()
            return True

async def get_all_users(limit: int = 50, offset: int = 0):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users ORDER BY id DESC LIMIT ? OFFSET ?", (limit, offset)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_total_users_count():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0

# --------------------- CATEGORY HELPERS ---------------------

async def add_category(name: str, emoji: str = "📁"):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("INSERT INTO categories (name, emoji) VALUES (?, ?)", (name, emoji))
        await db.commit()
        return cursor.lastrowid

async def get_categories():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM categories ORDER BY order_index ASC, id ASC") as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_category(category_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM categories WHERE id = ?", (category_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def delete_category(category_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        await db.commit()
        return True

# --------------------- PRODUCT HELPERS ---------------------

async def add_product(category_id: int, name: str, description: str, price: float, image_url: str = None, delivery_type: str = "digital"):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO products (category_id, name, description, price, image_url, delivery_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (category_id, name, description, price, image_url, delivery_type))
        await db.commit()
        return cursor.lastrowid

async def get_products_by_category(category_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM products WHERE category_id = ? AND is_active = 1 ORDER BY id ASC", (category_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_all_products(limit: int = 100):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            ORDER BY p.id DESC LIMIT ?
        """, (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_product(product_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            WHERE p.id = ?
        """, (product_id,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def update_product(product_id: int, name: str, description: str, price: float, image_url: str = None, delivery_type: str = "digital"):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE products 
            SET name = ?, description = ?, price = ?, image_url = ?, delivery_type = ?
            WHERE id = ?
        """, (name, description, price, image_url, delivery_type, product_id))
        await db.commit()
        return True

async def delete_product(product_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("DELETE FROM products WHERE id = ?", (product_id,))
        await db.commit()
        return True

# --------------------- STOCK HELPERS ---------------------

async def add_product_stock_bulk(product_id: int, items: list[str]):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        records = [(product_id, item.strip()) for item in items if item.strip()]
        if not records:
            return 0
        await db.executemany("INSERT INTO product_stock (product_id, item_data) VALUES (?, ?)", records)
        await db.commit()
        return len(records)

async def get_available_stock_count(product_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM product_stock WHERE product_id = ? AND is_sold = 0", (product_id,)) as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0

async def take_product_stock(product_id: int, quantity: int, user_id: int, order_code: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, item_data FROM product_stock WHERE product_id = ? AND is_sold = 0 LIMIT ?", (product_id, quantity)) as cursor:
            rows = await cursor.fetchall()
            if len(rows) < quantity:
                return None
            
            ids = [r["id"] for r in rows]
            items = [r["item_data"] for r in rows]

            placeholders = ",".join("?" for _ in ids)
            await db.execute(f"""
                UPDATE product_stock 
                SET is_sold = 1, sold_to_user_id = ?, sold_order_id = ?, sold_at = CURRENT_TIMESTAMP 
                WHERE id IN ({placeholders})
            """, [user_id, order_code] + ids)
            await db.commit()
            return items

# --------------------- ORDER HELPERS ---------------------

async def create_order(order_code: str, user_id: int, product_id: int, product_name: str, quantity: int, total_price: float, delivery_type: str, delivery_data: str, status: str = "COMPLETED"):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO orders (order_code, user_id, product_id, product_name, quantity, total_price, delivery_type, delivery_data, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (order_code, user_id, product_id, product_name, quantity, total_price, delivery_type, delivery_data, status))
        await db.commit()
        return cursor.lastrowid

async def get_user_orders(user_id: int, limit: int = 10):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC LIMIT ?", (user_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def get_order_by_code(order_code: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM orders WHERE order_code = ?", (order_code,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_all_orders(limit: int = 50):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def update_order_status(order_code: str, status: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("UPDATE orders SET status = ? WHERE order_code = ?", (status, order_code))
        await db.commit()
        return True

# --------------------- DEPOSIT HELPERS ---------------------

async def save_deposit(merchant_trade_no: str, user_id: int, order_amount: float, currency: str, checkout_url: str, bep20_addr: str, trc20_addr: str, erc20_addr: str, status: str = "INITIAL"):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO deposits (merchant_trade_no, user_id, order_amount, currency, checkout_url, bep20_addr, trc20_addr, erc20_addr, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (merchant_trade_no, user_id, order_amount, currency, checkout_url, bep20_addr, trc20_addr, erc20_addr, status))
        await db.commit()
        return cursor.lastrowid

async def get_deposit(merchant_trade_no: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM deposits WHERE merchant_trade_no = ?", (merchant_trade_no,)) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def get_pending_deposits(limit: int = 50):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM deposits WHERE status = 'INITIAL' AND credited = 0 ORDER BY id DESC LIMIT ?", (limit,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(r) for r in rows]

async def mark_deposit_paid(merchant_trade_no: str, paid_network: str = None, tx_hash: str = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE deposits 
            SET status = 'PAID', credited = 1, paid_network = ?, tx_hash = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE merchant_trade_no = ?
        """, (paid_network, tx_hash, merchant_trade_no))
        await db.commit()
        return True

async def update_deposit_tx_hash(merchant_trade_no: str, tx_hash: str, network: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE deposits 
            SET tx_hash = ?, paid_network = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE merchant_trade_no = ?
        """, (tx_hash, network, merchant_trade_no))
        await db.commit()
        return True

# --------------------- SETTINGS HELPERS ---------------------

async def get_setting(key: str, default: str = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT value FROM settings WHERE key = ?", (key,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else default

async def set_setting(key: str, value: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()
        return True

# --------------------- STATS HELPERS ---------------------

async def get_bot_stats():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c:
            total_users = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*), COALESCE(SUM(total_price), 0) FROM orders WHERE status = 'COMPLETED'") as c:
            r = await c.fetchone()
            total_orders, total_sales = r[0], r[1]
        async with db.execute("SELECT COUNT(*), COALESCE(SUM(order_amount), 0) FROM deposits WHERE status = 'PAID'") as c:
            r = await c.fetchone()
            total_deposits, total_deposited_amount = r[0], r[1]
        async with db.execute("SELECT COUNT(*) FROM products WHERE is_active = 1") as c:
            total_products = (await c.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM product_stock WHERE is_sold = 0") as c:
            total_stock = (await c.fetchone())[0]
            
        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "total_sales": total_sales,
            "total_deposits": total_deposits,
            "total_deposited_amount": total_deposited_amount,
            "total_products": total_products,
            "total_stock": total_stock
        }
