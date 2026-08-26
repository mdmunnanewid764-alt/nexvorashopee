import logging
import asyncio
import time
from contextlib import asynccontextmanager
import asyncpg
from config import (
    DATABASE_URL,
    SUPABASE_HOST,
    SUPABASE_PORT,
    SUPABASE_USER,
    SUPABASE_PASS,
    SUPABASE_DB,
    BINANCE_API_KEY,
    CURRENCY_NAME,
    CURRENCY_SYMBOL,
    SUPPORT_USERNAME,
    MIN_DEPOSIT,
    ORDER_LOG_GROUP_ID
)

logger = logging.getLogger(__name__)

_pool: asyncpg.Pool = None

# High-speed in-memory caches (0ms instant RAM access)
_settings_cache: dict[str, str] = {}
_user_lang_cache: dict[int, str] = {}
_categories_cache: list[dict] = None
_categories_cache_time: float = 0
_products_by_cat_cache: dict[int, list[dict]] = {}
_products_by_cat_time: dict[int, float] = {}
_methods_cache: list[dict] = None
_methods_cache_time: float = 0

async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None or _pool._closed:
        try:
            _pool = await asyncpg.create_pool(
                dsn=DATABASE_URL,
                min_size=3,
                max_size=20,
                ssl="require",
                statement_cache_size=0,
                command_timeout=20
            )
            logger.info("Supabase PostgreSQL pool created via DATABASE_URL.")
        except Exception as e:
            logger.warning(f"Could not connect via DATABASE_URL, attempting host parameters: {e}")
            _pool = await asyncpg.create_pool(
                host=SUPABASE_HOST,
                port=SUPABASE_PORT,
                user=SUPABASE_USER,
                password=SUPABASE_PASS,
                database=SUPABASE_DB,
                min_size=3,
                max_size=20,
                ssl="require",
                statement_cache_size=0,
                command_timeout=20
            )
            logger.info("Supabase PostgreSQL pool created via host parameters.")
    return _pool

@asynccontextmanager
async def get_connection():
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn

def invalidate_category_cache():
    global _categories_cache, _categories_cache_time
    _categories_cache = None
    _categories_cache_time = 0

def invalidate_product_cache():
    global _products_by_cat_cache, _products_by_cat_time
    _products_by_cat_cache.clear()
    _products_by_cat_time.clear()

def invalidate_methods_cache():
    global _methods_cache, _methods_cache_time
    _methods_cache = None
    _methods_cache_time = 0

async def init_db():
    """
    Initializes PostgreSQL tables in Supabase, loads default settings, and pre-warms cache.
    """
    global _settings_cache
    async with get_connection() as conn:
        # Users Table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                balance DOUBLE PRECISION DEFAULT 0.0,
                total_deposited DOUBLE PRECISION DEFAULT 0.0,
                total_spent DOUBLE PRECISION DEFAULT 0.0,
                is_banned INTEGER DEFAULT 0,
                language TEXT DEFAULT 'en',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)

        # Categories Table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                emoji TEXT DEFAULT '📁',
                order_index INTEGER DEFAULT 0
            );
        """)

        # Products Table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
                name TEXT NOT NULL,
                description TEXT,
                price DOUBLE PRECISION NOT NULL,
                image_url TEXT,
                delivery_type TEXT DEFAULT 'digital',
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)

        # Digital Stock Table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS product_stock (
                id SERIAL PRIMARY KEY,
                product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
                item_data TEXT NOT NULL,
                is_sold INTEGER DEFAULT 0,
                sold_to_user_id BIGINT,
                sold_order_id TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                sold_at TIMESTAMP WITH TIME ZONE
            );
        """)

        # Orders Table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                order_code TEXT UNIQUE NOT NULL,
                user_id BIGINT NOT NULL,
                product_id INTEGER,
                product_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1,
                total_price DOUBLE PRECISION NOT NULL,
                delivery_type TEXT DEFAULT 'digital',
                delivery_data TEXT,
                status TEXT DEFAULT 'COMPLETED',
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)

        # Deposits Table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS deposits (
                id SERIAL PRIMARY KEY,
                merchant_trade_no TEXT UNIQUE NOT NULL,
                user_id BIGINT NOT NULL,
                order_amount DOUBLE PRECISION NOT NULL,
                currency TEXT DEFAULT 'USDT',
                status TEXT DEFAULT 'INITIAL',
                checkout_url TEXT,
                bep20_addr TEXT,
                trc20_addr TEXT,
                erc20_addr TEXT,
                paid_network TEXT,
                tx_hash TEXT,
                credited INTEGER DEFAULT 0,
                method_type TEXT DEFAULT 'crypto',
                sender_number TEXT,
                trx_id TEXT,
                bdt_amount DOUBLE PRECISION DEFAULT 0.0,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)

        # Ensure columns exist on deposits table if already created
        await conn.execute("""
            ALTER TABLE deposits ADD COLUMN IF NOT EXISTS method_type TEXT DEFAULT 'crypto';
            ALTER TABLE deposits ADD COLUMN IF NOT EXISTS sender_number TEXT;
            ALTER TABLE deposits ADD COLUMN IF NOT EXISTS trx_id TEXT;
            ALTER TABLE deposits ADD COLUMN IF NOT EXISTS bdt_amount DOUBLE PRECISION DEFAULT 0.0;
        """)

        # Payment Methods Table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS payment_methods (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                method_type TEXT NOT NULL,
                details TEXT,
                instructions TEXT,
                exchange_rate DOUBLE PRECISION DEFAULT 125.0,
                min_deposit DOUBLE PRECISION DEFAULT 1.0,
                is_active INTEGER DEFAULT 1,
                order_index INTEGER DEFAULT 0
            );
        """)

        # Seed Default Payment Methods if none exist
        count_methods = await conn.fetchval("SELECT COUNT(*) FROM payment_methods")
        if count_methods == 0:
            default_methods = [
                ("🪙 Crypto / USDT (Auto Verify)", "crypto_auto", "BEP20 / TRC20 / ERC20", "Automatic Instant API Verification via Binance Pay & Multi-Chain", 1.0, 1.0, 1, 1),
                ("📱 bKash Personal", "manual_bkash", "017XXXXXXXX", "Send Money to Personal bKash Number", 125.0, 1.0, 1, 2),
                ("📱 Nagad Personal", "manual_nagad", "017XXXXXXXX", "Send Money to Personal Nagad Number", 125.0, 1.0, 1, 3),
            ]
            for name, mtype, details, inst, rate, min_d, is_act, ord_idx in default_methods:
                await conn.execute("""
                    INSERT INTO payment_methods (name, method_type, details, instructions, exchange_rate, min_deposit, is_active, order_index)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """, name, mtype, details, inst, float(rate), float(min_d), is_act, ord_idx)

        # Settings Table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
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
            ("chatgpt_promo_desc", "Special 3-Month ChatGPT Subscription Promo. Activate directly on your Gmail / Email."),
            ("order_log_group_id", str(ORDER_LOG_GROUP_ID)),
            ("bep20_address", "0xb6944a334e57b50be1b854c5e7e0a55b5754383e"),
            ("trc20_address", "TYasdf123456789TronUSDTAddress9988"),
            ("erc20_address", "0x386Ac338C488F61a9B4810fe17Fa2a78BE456108")
        ]
        for key, val in default_settings:
            await conn.execute(
                "INSERT INTO settings (key, value) VALUES ($1, $2) ON CONFLICT (key) DO NOTHING",
                key, str(val)
            )

        # Pre-load settings into RAM for 0ms access
        rows = await conn.fetch("SELECT key, value FROM settings")
        for r in rows:
            _settings_cache[r["key"]] = r["value"]

    logger.info(f"Supabase PostgreSQL initialized & {len(_settings_cache)} settings cached.")


# --------------------- USER HELPERS ---------------------

async def get_or_create_user(telegram_id: int, username: str = None, first_name: str = None):
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        if row:
            if row["username"] != username or row["first_name"] != first_name:
                await conn.execute(
                    "UPDATE users SET username = $1, first_name = $2 WHERE telegram_id = $3",
                    username, first_name, telegram_id
                )
            if row.get("language"):
                _user_lang_cache[telegram_id] = row["language"]
            return dict(row)

        new_row = await conn.fetchrow("""
            INSERT INTO users (telegram_id, username, first_name, balance)
            VALUES ($1, $2, $3, 0.0)
            RETURNING *
        """, telegram_id, username, first_name)
        _user_lang_cache[telegram_id] = "en"
        return dict(new_row)

async def get_user(telegram_id: int):
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE telegram_id = $1", telegram_id)
        if row and row.get("language"):
            _user_lang_cache[telegram_id] = row["language"]
        return dict(row) if row else None

async def get_user_by_username(username: str):
    clean_user = username.replace("@", "").strip()
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE LOWER(username) = LOWER($1)", clean_user)
        return dict(row) if row else None

async def get_user_by_id_or_username(identifier: str):
    clean = str(identifier).replace("@", "").strip()
    if clean.isdigit():
        return await get_user(int(clean))
    return await get_user_by_username(clean)

_banned_users_cache: set[int] = set()

async def is_user_banned(telegram_id: int) -> bool:
    if telegram_id in _banned_users_cache:
        return True
    async with get_connection() as conn:
        val = await conn.fetchval("SELECT is_banned FROM users WHERE telegram_id = $1", telegram_id)
        if val == 1:
            _banned_users_cache.add(telegram_id)
            return True
        return False

async def toggle_user_ban(telegram_id: int) -> int:
    async with get_connection() as conn:
        val = await conn.fetchval("SELECT is_banned FROM users WHERE telegram_id = $1", telegram_id)
        new_ban = 0 if val == 1 else 1
        await conn.execute("UPDATE users SET is_banned = $1 WHERE telegram_id = $2", new_ban, telegram_id)
        if new_ban == 1:
            _banned_users_cache.add(telegram_id)
        else:
            _banned_users_cache.discard(telegram_id)
        return new_ban

async def get_user_language(telegram_id: int) -> str:
    # Instant memory cache lookup (0ms)
    if telegram_id in _user_lang_cache:
        return _user_lang_cache[telegram_id]
    user = await get_user(telegram_id)
    if user and user.get("language"):
        _user_lang_cache[telegram_id] = user["language"]
        return user["language"]
    _user_lang_cache[telegram_id] = "en"
    return "en"

async def set_user_language(telegram_id: int, language: str) -> bool:
    _user_lang_cache[telegram_id] = language
    async with get_connection() as conn:
        await conn.execute("UPDATE users SET language = $1 WHERE telegram_id = $2", language, telegram_id)
        return True

async def update_user_balance(telegram_id: int, amount: float, is_deposit: bool = False, is_spend: bool = False):
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT balance, total_deposited, total_spent FROM users WHERE telegram_id = $1", telegram_id)
        if not row:
            return False

        new_balance = max(0.0, float(row["balance"]) + float(amount))
        new_deposited = float(row["total_deposited"]) + (float(amount) if is_deposit and amount > 0 else 0.0)
        new_spent = float(row["total_spent"]) + (abs(float(amount)) if is_spend else 0.0)

        await conn.execute("""
            UPDATE users 
            SET balance = $1, total_deposited = $2, total_spent = $3 
            WHERE telegram_id = $4
        """, new_balance, new_deposited, new_spent, telegram_id)
        return True

async def get_all_users(limit: int = 50, offset: int = 0):
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM users ORDER BY id DESC LIMIT $1 OFFSET $2", limit, offset)
        return [dict(r) for r in rows]

async def get_total_users_count():
    async with get_connection() as conn:
        val = await conn.fetchval("SELECT COUNT(*) FROM users")
        return val or 0


# --------------------- CATEGORY HELPERS ---------------------

async def add_category(name: str, emoji: str = "📁"):
    invalidate_category_cache()
    async with get_connection() as conn:
        return await conn.fetchval("INSERT INTO categories (name, emoji) VALUES ($1, $2) RETURNING id", name, emoji)

async def get_categories():
    global _categories_cache, _categories_cache_time
    now = time.time()
    if _categories_cache is not None and (now - _categories_cache_time) < 45:
        return _categories_cache
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM categories ORDER BY order_index ASC, id ASC")
        _categories_cache = [dict(r) for r in rows]
        _categories_cache_time = now
        return _categories_cache

async def get_category(category_id: int):
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM categories WHERE id = $1", category_id)
        return dict(row) if row else None

async def delete_category(category_id: int):
    invalidate_category_cache()
    invalidate_product_cache()
    async with get_connection() as conn:
        await conn.execute("DELETE FROM categories WHERE id = $1", category_id)
        return True


# --------------------- PRODUCT HELPERS ---------------------

async def add_product(category_id: int, name: str, description: str, price: float, image_url: str = None, delivery_type: str = "digital"):
    invalidate_product_cache()
    async with get_connection() as conn:
        return await conn.fetchval("""
            INSERT INTO products (category_id, name, description, price, image_url, delivery_type)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """, category_id, name, description, float(price), image_url, delivery_type)

async def get_products_by_category(category_id: int):
    global _products_by_cat_cache, _products_by_cat_time
    now = time.time()
    if category_id in _products_by_cat_cache and (now - _products_by_cat_time.get(category_id, 0)) < 30:
        return _products_by_cat_cache[category_id]
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM products WHERE category_id = $1 AND is_active = 1 ORDER BY id ASC", category_id)
        res = [dict(r) for r in rows]
        _products_by_cat_cache[category_id] = res
        _products_by_cat_time[category_id] = now
        return res

async def get_all_products(limit: int = 100):
    async with get_connection() as conn:
        rows = await conn.fetch("""
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            ORDER BY p.id DESC LIMIT $1
        """, limit)
        return [dict(r) for r in rows]

async def get_product(product_id: int):
    async with get_connection() as conn:
        row = await conn.fetchrow("""
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            WHERE p.id = $1
        """, product_id)
        return dict(row) if row else None

async def update_product(product_id: int, name: str, description: str, price: float, image_url: str = None, delivery_type: str = "digital"):
    invalidate_product_cache()
    async with get_connection() as conn:
        await conn.execute("""
            UPDATE products 
            SET name = $1, description = $2, price = $3, image_url = $4, delivery_type = $5
            WHERE id = $6
        """, name, description, float(price), image_url, delivery_type, product_id)
        return True

async def delete_product(product_id: int):
    invalidate_product_cache()
    async with get_connection() as conn:
        await conn.execute("DELETE FROM products WHERE id = $1", product_id)
        return True


# --------------------- STOCK HELPERS ---------------------

async def add_product_stock_bulk(product_id: int, items: list[str]):
    records = [(product_id, item.strip()) for item in items if item.strip()]
    if not records:
        return 0
    async with get_connection() as conn:
        await conn.executemany("INSERT INTO product_stock (product_id, item_data) VALUES ($1, $2)", records)
        return len(records)

async def get_available_stock_count(product_id: int):
    async with get_connection() as conn:
        val = await conn.fetchval("SELECT COUNT(*) FROM product_stock WHERE product_id = $1 AND is_sold = 0", product_id)
        return val or 0

async def take_product_stock(product_id: int, quantity: int, user_id: int, order_code: str):
    async with get_connection() as conn:
        async with conn.transaction():
            rows = await conn.fetch(
                "SELECT id, item_data FROM product_stock WHERE product_id = $1 AND is_sold = 0 LIMIT $2 FOR UPDATE",
                product_id, quantity
            )
            if len(rows) < quantity:
                return None

            ids = [r["id"] for r in rows]
            items = [r["item_data"] for r in rows]

            await conn.execute("""
                UPDATE product_stock 
                SET is_sold = 1, sold_to_user_id = $1, sold_order_id = $2, sold_at = NOW() 
                WHERE id = ANY($3::int[])
            """, user_id, order_code, ids)
            return items


# --------------------- ORDER HELPERS ---------------------

async def create_order(order_code: str, user_id: int, product_id: int, product_name: str, quantity: int, total_price: float, delivery_type: str, delivery_data: str, status: str = "COMPLETED"):
    async with get_connection() as conn:
        return await conn.fetchval("""
            INSERT INTO orders (order_code, user_id, product_id, product_name, quantity, total_price, delivery_type, delivery_data, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id
        """, order_code, user_id, product_id, product_name, quantity, float(total_price), delivery_type, delivery_data, status)

async def get_user_orders(user_id: int, limit: int = 10):
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM orders WHERE user_id = $1 ORDER BY id DESC LIMIT $2", user_id, limit)
        return [dict(r) for r in rows]

async def get_order_by_code(order_code: str):
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM orders WHERE order_code = $1", order_code)
        return dict(row) if row else None

async def get_all_orders(limit: int = 50):
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM orders ORDER BY id DESC LIMIT $1", limit)
        return [dict(r) for r in rows]

async def update_order_status(order_code: str, status: str):
    async with get_connection() as conn:
        await conn.execute("UPDATE orders SET status = $1 WHERE order_code = $2", status, order_code)
        return True

async def update_order_delivery_data(order_code: str, delivery_data: str, status: str = None):
    async with get_connection() as conn:
        if status:
            await conn.execute("UPDATE orders SET delivery_data = $1, status = $2 WHERE order_code = $3", delivery_data, status, order_code)
        else:
            await conn.execute("UPDATE orders SET delivery_data = $1 WHERE order_code = $2", delivery_data, order_code)
        return True


# --------------------- PAYMENT METHODS (GATEWAYS) ---------------------

async def get_payment_methods(active_only: bool = False) -> list[dict]:
    global _methods_cache, _methods_cache_time
    now = time.time()
    if active_only and _methods_cache is not None and (now - _methods_cache_time) < 30:
        return _methods_cache

    async with get_connection() as conn:
        if active_only:
            rows = await conn.fetch("SELECT * FROM payment_methods WHERE is_active = 1 ORDER BY order_index ASC, id ASC")
            res = [dict(r) for r in rows]
            _methods_cache = res
            _methods_cache_time = now
            return res
        else:
            rows = await conn.fetch("SELECT * FROM payment_methods ORDER BY order_index ASC, id ASC")
            return [dict(r) for r in rows]

async def get_payment_method(method_id: int):
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM payment_methods WHERE id = $1", method_id)
        return dict(row) if row else None

async def add_payment_method(name: str, method_type: str, details: str, instructions: str, exchange_rate: float = 125.0, min_deposit: float = 1.0):
    invalidate_methods_cache()
    async with get_connection() as conn:
        return await conn.fetchval("""
            INSERT INTO payment_methods (name, method_type, details, instructions, exchange_rate, min_deposit, is_active, order_index)
            VALUES ($1, $2, $3, $4, $5, $6, 1, 10)
            RETURNING id
        """, name, method_type, details, instructions, float(exchange_rate), float(min_deposit))

async def update_payment_method(method_id: int, name: str, details: str, instructions: str, exchange_rate: float, min_deposit: float):
    invalidate_methods_cache()
    async with get_connection() as conn:
        await conn.execute("""
            UPDATE payment_methods 
            SET name = $1, details = $2, instructions = $3, exchange_rate = $4, min_deposit = $5
            WHERE id = $6
        """, name, details, instructions, float(exchange_rate), float(min_deposit), method_id)
        return True

async def toggle_payment_method(method_id: int):
    invalidate_methods_cache()
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT is_active FROM payment_methods WHERE id = $1", method_id)
        if not row:
            return False
        new_active = 0 if row["is_active"] == 1 else 1
        await conn.execute("UPDATE payment_methods SET is_active = $1 WHERE id = $2", new_active, method_id)
        return new_active

async def delete_payment_method(method_id: int):
    invalidate_methods_cache()
    async with get_connection() as conn:
        await conn.execute("DELETE FROM payment_methods WHERE id = $1", method_id)
        return True


# --------------------- DEPOSIT HELPERS ---------------------

async def save_deposit(merchant_trade_no: str, user_id: int, order_amount: float, currency: str, checkout_url: str, bep20_addr: str, trc20_addr: str, erc20_addr: str, status: str = "INITIAL", method_type: str = "crypto"):
    async with get_connection() as conn:
        return await conn.fetchval("""
            INSERT INTO deposits (merchant_trade_no, user_id, order_amount, currency, checkout_url, bep20_addr, trc20_addr, erc20_addr, status, method_type)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING id
        """, merchant_trade_no, user_id, float(order_amount), currency, checkout_url, bep20_addr, trc20_addr, erc20_addr, status, method_type)

async def save_manual_deposit(merchant_trade_no: str, user_id: int, order_amount: float, currency: str, method_type: str, sender_number: str, trx_id: str, bdt_amount: float = 0.0):
    async with get_connection() as conn:
        return await conn.fetchval("""
            INSERT INTO deposits (merchant_trade_no, user_id, order_amount, currency, status, method_type, sender_number, trx_id, bdt_amount)
            VALUES ($1, $2, $3, $4, 'PENDING_MANUAL', $5, $6, $7, $8)
            RETURNING id
        """, merchant_trade_no, user_id, float(order_amount), currency, method_type, sender_number, trx_id, float(bdt_amount))

async def get_deposit(merchant_trade_no: str):
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM deposits WHERE merchant_trade_no = $1", merchant_trade_no)
        return dict(row) if row else None

async def get_deposit_by_id(deposit_id: int):
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM deposits WHERE id = $1", deposit_id)
        return dict(row) if row else None

async def get_pending_deposits(limit: int = 50):
    async with get_connection() as conn:
        rows = await conn.fetch("SELECT * FROM deposits WHERE status = 'INITIAL' AND credited = 0 ORDER BY id DESC LIMIT $1", limit)
        return [dict(r) for r in rows]

async def mark_deposit_paid(merchant_trade_no: str, paid_network: str = None, tx_hash: str = None):
    async with get_connection() as conn:
        await conn.execute("""
            UPDATE deposits 
            SET status = 'PAID', credited = 1, paid_network = $1, tx_hash = $2, updated_at = NOW() 
            WHERE merchant_trade_no = $3
        """, paid_network, tx_hash, merchant_trade_no)
        return True

async def approve_manual_deposit(deposit_id: int):
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM deposits WHERE id = $1", deposit_id)
        if not row or row["credited"] == 1:
            return None
        await conn.execute("""
            UPDATE deposits 
            SET status = 'PAID', credited = 1, updated_at = NOW() 
            WHERE id = $1
        """, deposit_id)
        # Update user balance
        await update_user_balance(row["user_id"], float(row["order_amount"]), is_deposit=True)
        return dict(row)

async def reject_manual_deposit(deposit_id: int):
    async with get_connection() as conn:
        row = await conn.fetchrow("SELECT * FROM deposits WHERE id = $1", deposit_id)
        if not row:
            return None
        await conn.execute("""
            UPDATE deposits 
            SET status = 'REJECTED', updated_at = NOW() 
            WHERE id = $1
        """, deposit_id)
        return dict(row)

async def update_deposit_tx_hash(merchant_trade_no: str, tx_hash: str, network: str):
    async with get_connection() as conn:
        await conn.execute("""
            UPDATE deposits 
            SET tx_hash = $1, paid_network = $2, updated_at = NOW() 
            WHERE merchant_trade_no = $3
        """, tx_hash, network, merchant_trade_no)
        return True

async def update_deposit_network(merchant_trade_no: str, network: str):
    async with get_connection() as conn:
        await conn.execute("""
            UPDATE deposits 
            SET paid_network = $1, updated_at = NOW() 
            WHERE merchant_trade_no = $2
        """, network, merchant_trade_no)
        return True


# --------------------- SETTINGS HELPERS ---------------------

async def get_setting(key: str, default: str = None):
    # 0ms Instant in-memory cache lookup
    if key in _settings_cache:
        return _settings_cache[key]
    async with get_connection() as conn:
        val = await conn.fetchval("SELECT value FROM settings WHERE key = $1", key)
        if val is not None:
            _settings_cache[key] = val
            return val
        return default

async def set_setting(key: str, value: str):
    _settings_cache[key] = str(value)
    async with get_connection() as conn:
        await conn.execute("""
            INSERT INTO settings (key, value)
            VALUES ($1, $2)
            ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value
        """, key, str(value))
        return True


# --------------------- STATS HELPERS ---------------------

async def get_bot_stats():
    async with get_connection() as conn:
        total_users = await conn.fetchval("SELECT COUNT(*) FROM users") or 0
        r_orders = await conn.fetchrow("SELECT COUNT(*), COALESCE(SUM(total_price), 0) FROM orders WHERE status = 'COMPLETED'")
        total_orders = r_orders[0] if r_orders else 0
        total_sales = float(r_orders[1]) if r_orders else 0.0
        
        r_deposits = await conn.fetchrow("SELECT COUNT(*), COALESCE(SUM(order_amount), 0) FROM deposits WHERE status = 'PAID'")
        total_deposits = r_deposits[0] if r_deposits else 0
        total_deposited_amount = float(r_deposits[1]) if r_deposits else 0.0

        total_products = await conn.fetchval("SELECT COUNT(*) FROM products WHERE is_active = 1") or 0
        total_stock = await conn.fetchval("SELECT COUNT(*) FROM product_stock WHERE is_sold = 0") or 0

        return {
            "total_users": total_users,
            "total_orders": total_orders,
            "total_sales": total_sales,
            "total_deposits": total_deposits,
            "total_deposited_amount": total_deposited_amount,
            "total_products": total_products,
            "total_stock": total_stock
        }
