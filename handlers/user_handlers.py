import logging
import time
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
import database
from payment_service import payment_gateway, generate_qr_image
from config import ADMIN_ID

logger = logging.getLogger(__name__)

# Conversation states for User
CUSTOM_DEPOSIT_AMOUNT, SUBMIT_TX_NETWORK, SUBMIT_TX_HASH, MANUAL_ORDER_INPUT = range(4)

def escape(text: str) -> str:
    return html.escape(str(text) if text is not None else "")

def get_main_menu_keyboard(is_admin: bool = False):
    keyboard = [
        [InlineKeyboardButton("🛍 Shop / Products", callback_data="user_categories"), InlineKeyboardButton("💳 My Wallet", callback_data="user_wallet")],
        [InlineKeyboardButton("📦 My Orders", callback_data="user_orders"), InlineKeyboardButton("👤 My Profile", callback_data="user_profile")],
        [InlineKeyboardButton("💬 Support & Help", callback_data="user_support")]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton("🛠 Admin Control Panel", callback_data="admin_home")])
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /start command. Registers user and shows the main menu.
    """
    user = update.effective_user

    # Register or get user
    db_user = await database.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name
    )

    currency = await database.get_setting("currency_symbol", "$")
    is_admin = (user.id == ADMIN_ID)
    first_name_safe = escape(user.first_name)

    welcome_text = (
        f"👋 <b>Welcome to Nexvora Shop, {first_name_safe}!</b>\n\n"
        f"✨ <i>Your premier automated marketplace for premium digital goods, subscriptions, and instant services.</i>\n\n"
        f"💰 <b>Your Balance:</b> <code>{currency}{db_user['balance']:.2f}</code>\n"
        f"🆔 <b>Your User ID:</b> <code>{user.id}</code>\n\n"
        f"👇 <i>Choose an option below to get started:</i>"
    )

    keyboard = get_main_menu_keyboard(is_admin)

    if update.callback_query:
        await update.callback_query.answer()
        try:
            await update.callback_query.edit_message_text(
                welcome_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
        except Exception:
            await update.effective_chat.send_message(
                welcome_text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    else:
        await update.message.reply_text(
            welcome_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

# -------------------- SHOP & PRODUCT BROWSING --------------------

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    categories = await database.get_categories()
    if not categories:
        text = "🛍 <b>Store Catalog</b>\n\n⚠️ No categories available at the moment. Please check back soon!"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="user_menu")]
        ])
        if query:
            await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return

    text = "🛍 <b>Store Catalog - Categories</b>\n\nSelect a category to browse products:"
    buttons = []
    for cat in categories:
        products = await database.get_products_by_category(cat["id"])
        stock_indicator = f"({len(products)} items)"
        buttons.append([InlineKeyboardButton(f"{cat.get('emoji', '📁')} {cat['name']} {stock_indicator}", callback_data=f"cat_{cat['id']}")])

    buttons.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="user_menu")])
    keyboard = InlineKeyboardMarkup(buttons)

    if query:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    category_id = int(query.data.split("_")[1])
    category = await database.get_category(category_id)
    products = await database.get_products_by_category(category_id)
    currency = await database.get_setting("currency_symbol", "$")

    if not category:
        await query.edit_message_text("Category not found.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="user_categories")]]))
        return

    cat_name_safe = escape(category["name"])
    if not products:
        text = f"📂 <b>{category.get('emoji', '📁')} {cat_name_safe}</b>\n\n⚠️ No products available in this category."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Categories", callback_data="user_categories")]
        ])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return

    text = f"📂 <b>{category.get('emoji', '📁')} {cat_name_safe}</b>\n\nSelect a product to view details & buy:"
    buttons = []
    for prod in products:
        if prod["delivery_type"] == "digital":
            stock_count = await database.get_available_stock_count(prod["id"])
            stock_badge = f"📦 {stock_count} left" if stock_count > 0 else "❌ Out of Stock"
        else:
            stock_badge = "⚡ Instant Service"
        
        buttons.append([
            InlineKeyboardButton(f"🛒 {prod['name']} - {currency}{prod['price']:.2f} ({stock_badge})", callback_data=f"prod_{prod['id']}")
        ])

    buttons.append([InlineKeyboardButton("🔙 Back to Categories", callback_data="user_categories")])
    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[1])
    product = await database.get_product(product_id)
    currency = await database.get_setting("currency_symbol", "$")

    if not product:
        await query.edit_message_text("Product not found.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="user_categories")]]))
        return

    user = await database.get_user(query.from_user.id)
    user_balance = user["balance"] if user else 0.0

    if product["delivery_type"] == "digital":
        stock_count = await database.get_available_stock_count(product["id"])
        stock_text = f"📦 <b>In Stock:</b> <code>{stock_count}</code> units available"
        delivery_info = "⚡ <b>Instant Digital Delivery</b> <i>(Item/Key will be delivered directly in chat immediately after purchase)</i>"
    else:
        stock_count = 999
        stock_text = "📦 <b>Availability:</b> <code>Available on Request</code>"
        delivery_info = "🛠 <b>Manual Service / Order</b> <i>(Admin will fulfill upon order)</i>"

    prod_name_safe = escape(product['name'])
    cat_name_safe = escape(product.get('category_name', 'General'))
    desc_safe = escape(product.get('description') or 'No detailed description.')

    text = (
        f"🏷 <b>Product:</b> <code>{prod_name_safe}</code>\n"
        f"📁 <b>Category:</b> <code>{cat_name_safe}</code>\n"
        f"💵 <b>Price:</b> <code>{currency}{product['price']:.2f}</code>\n"
        f"{stock_text}\n\n"
        f"📝 <b>Description:</b>\n{desc_safe}\n\n"
        f"{delivery_info}\n\n"
        f"💰 <b>Your Balance:</b> <code>{currency}{user_balance:.2f}</code>"
    )

    buttons = []
    if stock_count > 0:
        buttons.append([InlineKeyboardButton(f"💳 Buy with Balance ({currency}{product['price']:.2f})", callback_data=f"buybal_{product['id']}")])
        buttons.append([InlineKeyboardButton(f"🪙 Direct Crypto Invoice ({currency}{product['price']:.2f})", callback_data=f"buycrypto_{product['id']}")])
    else:
        buttons.append([InlineKeyboardButton("❌ Out of Stock", callback_data="noop")])

    cat_id = product.get("category_id")
    back_target = f"cat_{cat_id}" if cat_id else "user_categories"
    buttons.append([InlineKeyboardButton("🔙 Back to Products", callback_data=back_target)])

    keyboard = InlineKeyboardMarkup(buttons)

    if product.get("image_url") and product["image_url"].startswith("http"):
        try:
            await query.message.delete()
            await query.message.chat.send_photo(
                photo=product["image_url"],
                caption=text,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
            return
        except Exception as e:
            logger.warning(f"Failed to send product photo: {e}")

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# -------------------- PRODUCT PURCHASE --------------------

async def handle_buy_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[1])
    product = await database.get_product(product_id)
    user_id = query.from_user.id
    user = await database.get_user(user_id)
    currency = await database.get_setting("currency_symbol", "$")

    if not product or not user:
        await query.edit_message_text("❌ Product or User not found.")
        return

    # Check balance
    if user["balance"] < product["price"]:
        shortage = product["price"] - user["balance"]
        text = (
            f"❌ <b>Insufficient Balance</b>\n\n"
            f"Required: <code>{currency}{product['price']:.2f}</code>\n"
            f"Your Balance: <code>{currency}{user['balance']:.2f}</code>\n"
            f"You need <code>{currency}{shortage:.2f}</code> more.\n\n"
            f"👇 Click below to deposit funds via Binance Pay or Crypto!"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💳 Deposit Balance Now", callback_data="user_deposit")],
            [InlineKeyboardButton("🔙 Back to Product", callback_data=f"prod_{product['id']}")]
        ])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return

    # Process Digital Delivery
    if product["delivery_type"] == "digital":
        order_code = f"ORD_{int(time.time())}_{user_id % 10000}"
        items = await database.take_product_stock(product_id=product["id"], quantity=1, user_id=user_id, order_code=order_code)
        
        if not items:
            await query.edit_message_text(
                "❌ <b>Sorry, this item just ran out of stock!</b>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Catalog", callback_data="user_categories")]]),
                parse_mode=ParseMode.HTML
            )
            return

        # Deduct balance
        await database.update_user_balance(user_id, -product["price"], is_spend=True)

        delivered_item = items[0]
        # Save order
        await database.create_order(
            order_code=order_code,
            user_id=user_id,
            product_id=product["id"],
            product_name=product["name"],
            quantity=1,
            total_price=product["price"],
            delivery_type="digital",
            delivery_data=delivered_item,
            status="COMPLETED"
        )

        success_text = (
            f"🎉 <b>Purchase Successful!</b>\n\n"
            f"📦 <b>Product:</b> <code>{escape(product['name'])}</code>\n"
            f"🔖 <b>Order Code:</b> <code>{order_code}</code>\n"
            f"💰 <b>Amount Paid:</b> <code>{currency}{product['price']:.2f}</code>\n\n"
            f"🔑 <b>Delivered Item / Code / Access:</b>\n"
            f"<pre>{escape(delivered_item)}</pre>\n\n"
            f"💡 <i>You can also view this anytime in 'My Orders'.</i>"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📦 My Orders", callback_data="user_orders"), InlineKeyboardButton("🛍 Continue Shopping", callback_data="user_categories")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="user_menu")]
        ])
        await query.edit_message_text(success_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

        # Notify Admin
        try:
            admin_msg = (
                f"🛍 <b>New Digital Sale!</b>\n"
                f"👤 Buyer: <a href='tg://user?id={user_id}'>{escape(query.from_user.first_name)}</a> (<code>{user_id}</code>)\n"
                f"🏷 Product: <code>{escape(product['name'])}</code>\n"
                f"💵 Price: <code>{currency}{product['price']:.2f}</code>\n"
                f"🔖 Order: <code>{order_code}</code>"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.warning(f"Failed to notify admin of sale: {e}")

    else:
        # Manual Delivery Flow
        context.user_data["pending_manual_product_id"] = product["id"]
        context.user_data["pending_manual_price"] = product["price"]
        
        prompt_text = (
            f"📝 <b>Manual Service Order: {escape(product['name'])}</b>\n\n"
            f"Price: <code>{currency}{product['price']:.2f}</code>\n\n"
            f"Please enter any required details for your order (e.g. Email, Username, or specifications) to complete purchase:"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data=f"prod_{product['id']}")]
        ])
        await query.edit_message_text(prompt_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return MANUAL_ORDER_INPUT

async def handle_manual_order_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text
    product_id = context.user_data.get("pending_manual_product_id")
    currency = await database.get_setting("currency_symbol", "$")

    if not product_id:
        await update.message.reply_text("Session expired. Please start over from /start.")
        return ConversationHandler.END

    product = await database.get_product(product_id)
    user = await database.get_user(user_id)

    if not product or not user:
        await update.message.reply_text("Error loading product. Please try again.")
        return ConversationHandler.END

    if user["balance"] < product["price"]:
        await update.message.reply_text("Insufficient balance. Please deposit funds first.")
        return ConversationHandler.END

    # Deduct balance
    await database.update_user_balance(user_id, -product["price"], is_spend=True)

    order_code = f"ORD_{int(time.time())}_{user_id % 10000}"
    await database.create_order(
        order_code=order_code,
        user_id=user_id,
        product_id=product["id"],
        product_name=product["name"],
        quantity=1,
        total_price=product["price"],
        delivery_type="manual",
        delivery_data=user_text,
        status="PENDING_MANUAL"
    )

    success_text = (
        f"✅ <b>Order Submitted Successfully!</b>\n\n"
        f"📦 <b>Product:</b> <code>{escape(product['name'])}</code>\n"
        f"🔖 <b>Order Code:</b> <code>{order_code}</code>\n"
        f"💰 <b>Amount Paid:</b> <code>{currency}{product['price']:.2f}</code>\n"
        f"📝 <b>Your Details:</b>\n<code>{escape(user_text)}</code>\n\n"
        f"⏳ <i>Our team has received your order and is processing it. You will be updated here once fulfilled.</i>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📦 My Orders", callback_data="user_orders"), InlineKeyboardButton("🔙 Main Menu", callback_data="user_menu")]
    ])
    await update.message.reply_text(success_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    # Notify Admin
    try:
        admin_msg = (
            f"🚨 <b>New Manual Order Pending!</b>\n\n"
            f"👤 Buyer: <a href='tg://user?id={user_id}'>{escape(update.effective_user.first_name)}</a> (<code>{user_id}</code>)\n"
            f"🏷 Product: <code>{escape(product['name'])}</code>\n"
            f"🔖 Order Code: <code>{order_code}</code>\n"
            f"💵 Price: <code>{currency}{product['price']:.2f}</code>\n"
            f"📝 <b>User Input Details:</b>\n<code>{escape(user_text)}</code>"
        )
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_msg, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.warning(f"Failed to notify admin of manual order: {e}")

    context.user_data.pop("pending_manual_product_id", None)
    return ConversationHandler.END

# -------------------- WALLET & DEPOSIT FLOW --------------------

async def show_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    user_id = query.from_user.id if query else update.effective_user.id
    user = await database.get_or_create_user(user_id, update.effective_user.username, update.effective_user.first_name)
    currency = await database.get_setting("currency_symbol", "$")
    curr_name = await database.get_setting("currency_name", "USDT")

    text = (
        f"💳 <b>My Wallet & Balance</b>\n\n"
        f"💰 <b>Current Balance:</b> <code>{currency}{user['balance']:.2f} {curr_name}</code>\n"
        f"📥 <b>Total Deposited:</b> <code>{currency}{user['total_deposited']:.2f}</code>\n"
        f"🛒 <b>Total Spent:</b> <code>{currency}{user['total_spent']:.2f}</code>\n\n"
        f"⚡ <i>All deposits are automatically processed via Binance Pay and Multi-Chain crypto networks (BEP20, TRC20, ERC20).</i>"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Deposit Balance", callback_data="user_deposit")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="user_menu")]
    ])

    if query:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def show_deposit_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    currency = await database.get_setting("currency_symbol", "$")
    min_dep = float(await database.get_setting("min_deposit", "1.0"))

    text = (
        f"📥 <b>Add Funds / Deposit Balance</b>\n\n"
        f"🪙 <b>Supported Gateways:</b>\n"
        f"• <b>Binance Pay</b> (0% Gas Fee, Instant)\n"
        f"• <b>USDT - BEP20</b> (BNB Smart Chain)\n"
        f"• <b>USDT - TRC20</b> (TRON Network)\n"
        f"• <b>USDT - ERC20</b> (Ethereum)\n\n"
        f"📌 <i>Minimum deposit:</i> <code>{currency}{min_dep:.2f}</code>\n\n"
        f"Select a preset amount or choose custom:"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{currency}5", callback_data="create_dep_5"),
            InlineKeyboardButton(f"{currency}10", callback_data="create_dep_10"),
            InlineKeyboardButton(f"{currency}25", callback_data="create_dep_25")
        ],
        [
            InlineKeyboardButton(f"{currency}50", callback_data="create_dep_50"),
            InlineKeyboardButton(f"{currency}100", callback_data="create_dep_100"),
            InlineKeyboardButton("✏️ Custom Amount", callback_data="custom_deposit_btn")
        ],
        [InlineKeyboardButton("🔙 Back to Wallet", callback_data="user_wallet")]
    ])

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def prompt_custom_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    min_dep = float(await database.get_setting("min_deposit", "1.0"))
    currency = await database.get_setting("currency_symbol", "$")

    text = (
        f"✏️ <b>Enter Custom Deposit Amount</b>\n\n"
        f"Please reply with the exact amount in USDT (minimum <code>{currency}{min_dep:.2f}</code>):\n"
        f"<i>(Example: <code>15</code> or <code>35.50</code>)</i>"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="user_deposit")]])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return CUSTOM_DEPOSIT_AMOUNT

async def process_custom_deposit_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.replace("$", "").strip()

    try:
        amount = float(text)
        min_dep = float(await database.get_setting("min_deposit", "1.0"))
        if amount < min_dep:
            await update.message.reply_text(f"⚠️ Minimum deposit amount is ${min_dep:.2f}. Please try again:")
            return CUSTOM_DEPOSIT_AMOUNT
        
        return await execute_create_deposit(update, context, amount=amount, user_id=user_id)
    except ValueError:
        await update.message.reply_text("⚠️ Invalid number. Please enter a valid amount (e.g. 20):")
        return CUSTOM_DEPOSIT_AMOUNT

async def handle_preset_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    amount = float(query.data.split("_")[2])
    user_id = query.from_user.id
    await execute_create_deposit(update, context, amount=amount, user_id=user_id, is_callback=True)

async def execute_create_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float, user_id: int, is_callback: bool = False):
    currency = await database.get_setting("currency_symbol", "$")
    
    loading_msg = None
    if is_callback:
        await update.callback_query.edit_message_text("⏳ <i>Generating Binance Pay & Multi-Chain invoice...</i>", parse_mode=ParseMode.HTML)
    else:
        loading_msg = await update.message.reply_text("⏳ <i>Generating Binance Pay & Multi-Chain invoice...</i>", parse_mode=ParseMode.HTML)

    res = await payment_gateway.create_payment(
        amount=amount,
        user_id=user_id,
        goods_name=f"Deposit {currency}{amount:.2f}",
        goods_detail=f"Nexvora Telegram Bot Balance Deposit"
    )

    if not res.get("success"):
        err_text = f"❌ <b>Payment Gateway Error</b>\n\n{escape(res.get('message', 'Unable to create payment invoice.'))}\n\nPlease contact support if this persists."
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Wallet", callback_data="user_wallet")]])
        if is_callback:
            await update.callback_query.edit_message_text(err_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        elif loading_msg:
            await loading_msg.edit_text(err_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    order = res["order"]
    merchant_trade_no = order.get("merchantTradeNo")
    checkout_url = order.get("checkoutUrl", "")
    crypto_wallets = order.get("cryptoWallets", {})
    bep20 = crypto_wallets.get("bep20", "N/A")
    trc20 = crypto_wallets.get("trc20", "N/A")
    erc20 = crypto_wallets.get("erc20", "N/A")

    invoice_text = (
        f"🪙 <b>Payment Invoice Generated</b>\n\n"
        f"🔖 <b>Invoice ID:</b> <code>{merchant_trade_no}</code>\n"
        f"💵 <b>Amount:</b> <code>{currency}{amount:.2f} USDT</code>\n"
        f"⏳ <b>Status:</b> <code>Awaiting Payment (INITIAL)</code>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ <b>Method 1: Binance Pay (0% Gas, Instant)</b>\n"
        f"Click the button below to pay directly inside Binance App or Browser.\n\n"
        f"🌐 <b>Method 2: Multi-Chain Crypto Transfer</b>\n"
        f"Send exact <code>{amount:.2f} USDT</code> to any address below:\n\n"
        f"🟡 <b>BEP20 (BNB Smart Chain):</b>\n<code>{bep20}</code>\n\n"
        f"🔴 <b>TRC20 (TRON Network):</b>\n<code>{trc20}</code>\n\n"
        f"🔵 <b>ERC20 (Ethereum):</b>\n<code>{erc20}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 <i>After transferring, click 'Check Payment' or submit your TxHash for instant confirmation!</i>"
    )

    buttons = []
    if checkout_url:
        buttons.append([InlineKeyboardButton("🚀 Pay with Binance Pay (App / Web)", url=checkout_url)])
    
    buttons.append([
        InlineKeyboardButton("🔄 Check Payment Status", callback_data=f"chkdep_{merchant_trade_no}"),
        InlineKeyboardButton("⚡ Submit TxHash", callback_data=f"txstart_{merchant_trade_no}")
    ])
    buttons.append([
        InlineKeyboardButton("🖼 Show QR Codes", callback_data=f"qrdep_{merchant_trade_no}"),
        InlineKeyboardButton("🔙 Wallet", callback_data="user_wallet")
    ])

    keyboard = InlineKeyboardMarkup(buttons)

    if is_callback:
        await update.callback_query.edit_message_text(invoice_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    elif loading_msg:
        await loading_msg.edit_text(invoice_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    return ConversationHandler.END

async def check_deposit_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    merchant_trade_no = query.data.split("_")[1]
    
    await query.answer("🔍 Checking payment status with gateway...")

    status_res = await payment_gateway.get_payment_status(merchant_trade_no)
    currency = await database.get_setting("currency_symbol", "$")

    if not status_res.get("success"):
        await query.answer(f"⚠️ Status: {status_res.get('message', 'Failed to fetch status')}", show_alert=True)
        return

    order_info = status_res.get("order", {})
    status = order_info.get("status", "INITIAL").upper()

    if status == "PAID":
        db_dep = await database.get_deposit(merchant_trade_no)
        if db_dep and not db_dep["credited"]:
            amount = float(order_info.get("orderAmount", db_dep["order_amount"]))
            paid_net = order_info.get("paidNetwork", "Multi-Chain")
            tx_id = order_info.get("transactionId", "")
            
            await database.update_user_balance(db_dep["user_id"], amount, is_deposit=True)
            await database.mark_deposit_paid(merchant_trade_no, paid_network=paid_net, tx_hash=tx_id)

            success_text = (
                f"🎉 <b>Deposit Confirmed & Credited!</b>\n\n"
                f"🔖 <b>Invoice ID:</b> <code>{merchant_trade_no}</code>\n"
                f"💰 <b>Amount Credited:</b> <code>{currency}{amount:.2f} USDT</code>\n"
                f"🌐 <b>Network:</b> <code>{paid_net}</code>\n\n"
                f"✨ <i>Your new wallet balance is ready for shopping!</i>"
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛍 Browse Shop", callback_data="user_categories"), InlineKeyboardButton("💳 My Wallet", callback_data="user_wallet")]
            ])
            await query.edit_message_text(success_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            return
        else:
            await query.answer("✅ This deposit is already verified and credited to your wallet!", show_alert=True)
            return
    elif status == "INITIAL":
        await query.answer("⏳ Payment not detected yet. If you just sent the transaction, please allow 1-2 minutes for blockchain confirmations.", show_alert=True)
    else:
        await query.answer(f"ℹ️ Order status: {status}", show_alert=True)

async def show_deposit_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    merchant_trade_no = query.data.split("_")[1]
    await query.answer()

    db_dep = await database.get_deposit(merchant_trade_no)
    if not db_dep:
        await query.answer("Deposit not found.", show_alert=True)
        return

    target_qr_text = db_dep["checkout_url"] or db_dep["bep20_addr"] or "https://binance.com"
    qr_bio = generate_qr_image(target_qr_text)

    caption = (
        f"📱 <b>Scan to Pay</b>\n\n"
        f"🔖 Invoice: <code>{merchant_trade_no}</code>\n"
        f"💰 Amount: <code>${db_dep['order_amount']:.2f} USDT</code>\n\n"
        f"🟡 <b>BEP20 Address:</b>\n<code>{db_dep['bep20_addr']}</code>\n\n"
        f"🔴 <b>TRC20 Address:</b>\n<code>{db_dep['trc20_addr']}</code>"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Check Status", callback_data=f"chkdep_{merchant_trade_no}")],
        [InlineKeyboardButton("🔙 Back to Wallet", callback_data="user_wallet")]
    ])

    await query.message.reply_photo(photo=qr_bio, caption=caption, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# -------------------- SUBMIT TX HASH CONVERSATION --------------------

async def start_submit_tx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    merchant_trade_no = query.data.split("_")[1]
    await query.answer()

    context.user_data["submit_tx_merchant_trade_no"] = merchant_trade_no

    text = (
        f"⚡ <b>Submit On-Chain TxHash Verification</b>\n\n"
        f"Invoice: <code>{merchant_trade_no}</code>\n\n"
        f"Select the blockchain network you transferred on:"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🟡 BEP20 (BSC)", callback_data="txnet_BEP20"),
            InlineKeyboardButton("🔴 TRC20 (TRON)", callback_data="txnet_TRC20"),
            InlineKeyboardButton("🔵 ERC20 (ETH)", callback_data="txnet_ERC20")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="user_wallet")]
    ])

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return SUBMIT_TX_NETWORK

async def handle_submit_tx_network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    network = query.data.split("_")[1]
    await query.answer()

    context.user_data["submit_tx_network"] = network
    trade_no = context.user_data.get("submit_tx_merchant_trade_no", "")

    text = (
        f"⚡ <b>Submit TxHash ({network})</b>\n\n"
        f"Invoice: <code>{trade_no}</code>\n\n"
        f"Please reply with your Transaction Hash / Hash ID (e.g. <code>0x78ab9c...</code> or <code>a1b2c3...</code>):"
    )

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="user_wallet")]])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return SUBMIT_TX_HASH

async def handle_submit_tx_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tx_hash = update.message.text.strip()
    trade_no = context.user_data.get("submit_tx_merchant_trade_no")
    network = context.user_data.get("submit_tx_network", "BEP20")

    if not trade_no:
        await update.message.reply_text("Session expired. Please start again from /start.")
        return ConversationHandler.END

    loading = await update.message.reply_text("⏳ <i>Submitting TxHash for gateway verification...</i>", parse_mode=ParseMode.HTML)

    res = await payment_gateway.submit_tx_hash(merchant_trade_no=trade_no, network=network, tx_hash=tx_hash)

    if res.get("success"):
        text = (
            f"✅ <b>TxHash Submitted Successfully!</b>\n\n"
            f"🔖 <b>Invoice:</b> <code>{trade_no}</code>\n"
            f"🌐 <b>Network:</b> <code>{network}</code>\n"
            f"🔗 <b>TxHash:</b> <code>{escape(tx_hash)}</code>\n\n"
            f"⏳ <i>The system is verifying your blockchain transaction. Your balance will be credited automatically within a few minutes.</i>"
        )
    else:
        text = (
            f"⚠️ <b>Notice:</b> {escape(res.get('message', 'Submitted, awaiting confirmation'))}\n\n"
            f"Our system will continue checking for block confirmations."
        )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Check Status", callback_data=f"chkdep_{trade_no}")],
        [InlineKeyboardButton("💳 My Wallet", callback_data="user_wallet")]
    ])

    await loading.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    context.user_data.pop("submit_tx_merchant_trade_no", None)
    context.user_data.pop("submit_tx_network", None)
    return ConversationHandler.END

# -------------------- ORDERS & PROFILE --------------------

async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    orders = await database.get_user_orders(user_id, limit=10)
    currency = await database.get_setting("currency_symbol", "$")

    if not orders:
        text = "📦 <b>My Orders</b>\n\n⚠️ You haven't made any purchases yet."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🛍 Browse Store", callback_data="user_categories")],
            [InlineKeyboardButton("🔙 Main Menu", callback_data="user_menu")]
        ])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return

    text = "📦 <b>Your Recent Orders:</b>\n\n"
    for o in orders:
        status_icon = "✅" if o["status"] == "COMPLETED" else "⏳"
        text += (
            f"{status_icon} <b>{escape(o['product_name'])}</b>\n"
            f"🔖 Code: <code>{o['order_code']}</code> | Price: <code>{currency}{o['total_price']:.2f}</code>\n"
            f"📅 Date: <code>{o['created_at']}</code>\n"
        )
        if o["delivery_type"] == "digital" and o.get("delivery_data"):
            text += f"🔑 Item: <code>{escape(o['delivery_data'])}</code>\n"
        text += "────────────────────\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 Shop More", callback_data="user_categories"), InlineKeyboardButton("🔙 Main Menu", callback_data="user_menu")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = await database.get_user(query.from_user.id)
    currency = await database.get_setting("currency_symbol", "$")

    first_name_safe = escape(user.get('first_name', 'N/A'))
    username_safe = escape(user.get('username', 'N/A'))

    text = (
        f"👤 <b>User Profile</b>\n\n"
        f"🆔 <b>Telegram ID:</b> <code>{user['telegram_id']}</code>\n"
        f"👤 <b>Name:</b> {first_name_safe}\n"
        f"🏷 <b>Username:</b> @{username_safe}\n"
        f"💰 <b>Wallet Balance:</b> <code>{currency}{user['balance']:.2f}</code>\n"
        f"📥 <b>Total Deposited:</b> <code>{currency}{user['total_deposited']:.2f}</code>\n"
        f"🛒 <b>Total Spent:</b> <code>{currency}{user['total_spent']:.2f}</code>\n"
        f"📅 <b>Member Since:</b> <code>{user.get('created_at', 'N/A')}</code>"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📥 Add Balance", callback_data="user_deposit"), InlineKeyboardButton("📦 My Orders", callback_data="user_orders")],
        [InlineKeyboardButton("🔙 Main Menu", callback_data="user_menu")]
    ])

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    support_user = escape(await database.get_setting("support_username", "@Support"))

    text = (
        f"💬 <b>Nexvora Support & Help</b>\n\n"
        f"Need assistance with an order, deposit, or custom inquiry?\n\n"
        f"👨‍💻 <b>Direct Admin Support:</b> {support_user}\n"
        f"⚡ <b>Available:</b> 24/7 Fast Response"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="user_menu")]
    ])

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def handle_direct_crypto_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    product_id = int(query.data.split("_")[1])
    product = await database.get_product(product_id)
    user_id = query.from_user.id

    if not product:
        await query.edit_message_text("Product not found.")
        return

    await execute_create_deposit(update, context, amount=product["price"], user_id=user_id, is_callback=True)
