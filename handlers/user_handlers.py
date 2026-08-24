import logging
import time
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
import database
from payment_service import payment_gateway, generate_qr_image
from config import ADMIN_ID
from locales import t, LANGUAGES

logger = logging.getLogger(__name__)

# Conversation states for User
CUSTOM_DEPOSIT_AMOUNT, SUBMIT_TX_NETWORK, SUBMIT_TX_HASH, MANUAL_ORDER_INPUT = range(4)

def escape(text: str) -> str:
    return html.escape(str(text) if text is not None else "")

def get_main_menu_keyboard(lang: str = "en", is_admin: bool = False):
    keyboard = [
        [
            InlineKeyboardButton(t("btn_shop", lang), callback_data="user_categories"),
            InlineKeyboardButton(t("btn_wallet", lang), callback_data="user_wallet")
        ],
        [
            InlineKeyboardButton(t("btn_orders", lang), callback_data="user_orders"),
            InlineKeyboardButton(t("btn_profile", lang), callback_data="user_profile")
        ],
        [
            InlineKeyboardButton(t("btn_support", lang), callback_data="user_support"),
            InlineKeyboardButton(t("btn_language", lang), callback_data="user_language_menu")
        ]
    ]
    if is_admin:
        keyboard.append([InlineKeyboardButton(t("btn_admin", lang), callback_data="admin_home")])
    return InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /start command. Registers user and shows the main menu in their chosen language.
    """
    user = update.effective_user

    # Register or get user
    db_user = await database.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name
    )

    lang = db_user.get("language") or "en"
    currency = await database.get_setting("currency_symbol", "$")
    is_admin = (user.id == ADMIN_ID)
    first_name_safe = escape(user.first_name)

    welcome_title = t("welcome_title", lang, name=first_name_safe)
    welcome_sub = t("welcome_sub", lang)
    balance_label = t("balance", lang)
    user_id_label = t("user_id", lang)
    choose_label = t("choose_option", lang)

    welcome_text = (
        f"👋 <b>{welcome_title}</b>\n\n"
        f"✨ <i>{welcome_sub}</i>\n\n"
        f"💰 <b>{balance_label}:</b> <code>{currency}{db_user['balance']:.2f}</code>\n"
        f"🆔 <b>{user_id_label}:</b> <code>{user.id}</code>\n\n"
        f"👇 <i>{choose_label}</i>"
    )

    keyboard = get_main_menu_keyboard(lang, is_admin)

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

# -------------------- LANGUAGE SELECTION --------------------

async def show_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id if query else update.effective_user.id
    lang = await database.get_user_language(user_id)

    if query:
        await query.answer()

    curr_lang_name = f"{LANGUAGES.get(lang, {}).get('flag', '')} {LANGUAGES.get(lang, {}).get('name', 'English')}"
    text = t("language_menu", lang, current=curr_lang_name)

    buttons = [
        [
            InlineKeyboardButton("🇬🇧 English (Default)", callback_data="setlang_en"),
            InlineKeyboardButton("🇵🇰 اردو (Pakistan)", callback_data="setlang_ur")
        ],
        [
            InlineKeyboardButton("🇮🇷 فارسی (Iran)", callback_data="setlang_fa"),
            InlineKeyboardButton("🇵🇸 العربية (Palestine)", callback_data="setlang_ar")
        ],
        [InlineKeyboardButton(t("btn_back_main", lang), callback_data="user_menu")]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    if query:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def handle_set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    new_lang = query.data.split("_")[1]
    user_id = query.from_user.id

    await database.set_user_language(user_id, new_lang)
    lang_info = LANGUAGES.get(new_lang, LANGUAGES["en"])
    lang_name = f"{lang_info['flag']} {lang_info['name']}"

    await query.answer(f"Language set to {lang_info['name']}")

    # Refresh start menu in new language
    await start_command(update, context)

# -------------------- SHOP & PRODUCT BROWSING --------------------

async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id if query else update.effective_user.id
    lang = await database.get_user_language(user_id)

    if query:
        await query.answer()

    categories = await database.get_categories()
    if not categories:
        text = f"🛍 <b>{t('catalog_title', lang)}</b>\n\n{t('catalog_empty', lang)}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_back_main", lang), callback_data="user_menu")]
        ])
        if query:
            await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return

    text = f"🛍 <b>{t('catalog_title', lang)}</b>\n\n{t('select_cat', lang)}"
    buttons = []
    for cat in categories:
        products = await database.get_products_by_category(cat["id"])
        stock_indicator = f"({len(products)})"
        buttons.append([InlineKeyboardButton(f"{cat.get('emoji', '📁')} {cat['name']} {stock_indicator}", callback_data=f"cat_{cat['id']}")])

    buttons.append([InlineKeyboardButton(t("btn_back_main", lang), callback_data="user_menu")])
    keyboard = InlineKeyboardMarkup(buttons)

    if query:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
    category_id = int(query.data.split("_")[1])
    category = await database.get_category(category_id)
    products = await database.get_products_by_category(category_id)
    currency = await database.get_setting("currency_symbol", "$")

    if not category:
        await query.edit_message_text("Category not found.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_back", lang), callback_data="user_categories")]]))
        return

    cat_name_safe = escape(category["name"])
    if not products:
        text = f"📂 <b>{category.get('emoji', '📁')} {cat_name_safe}</b>\n\n{t('category_empty', lang)}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_back_categories", lang), callback_data="user_categories")]
        ])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return

    text = f"📂 <b>{category.get('emoji', '📁')} {cat_name_safe}</b>\n\n{t('select_product', lang)}"
    buttons = []
    for prod in products:
        if prod["delivery_type"] == "digital":
            stock_count = await database.get_available_stock_count(prod["id"])
            stock_badge = f"📦 {stock_count} {t('in_stock', lang)}" if stock_count > 0 else f"❌ {t('out_of_stock', lang)}"
        else:
            stock_badge = f"⚡ {t('instant_service', lang)}"
        
        buttons.append([
            InlineKeyboardButton(f"🛒 {prod['name']} - {currency}{prod['price']:.2f} ({stock_badge})", callback_data=f"prod_{prod['id']}")
        ])

    buttons.append([InlineKeyboardButton(t("btn_back_categories", lang), callback_data="user_categories")])
    keyboard = InlineKeyboardMarkup(buttons)

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
    product_id = int(query.data.split("_")[1])
    product = await database.get_product(product_id)
    currency = await database.get_setting("currency_symbol", "$")

    if not product:
        await query.edit_message_text("Product not found.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_back", lang), callback_data="user_categories")]]))
        return

    user = await database.get_user(user_id)
    user_balance = user["balance"] if user else 0.0

    if product["delivery_type"] == "digital":
        stock_count = await database.get_available_stock_count(product["id"])
        stock_text = f"📦 <b>{t('in_stock', lang)}:</b> <code>{stock_count}</code>"
        delivery_info = t("instant_delivery_info", lang)
    else:
        stock_count = 999
        stock_text = f"📦 <b>{t('available_request', lang)}</b>"
        delivery_info = t("manual_delivery_info", lang)

    prod_name_safe = escape(product['name'])
    cat_name_safe = escape(product.get('category_name', 'General'))
    desc_safe = escape(product.get('description') or 'N/A')

    text = (
        f"🏷 <b>{t('product_label', lang)}:</b> <code>{prod_name_safe}</code>\n"
        f"📁 <b>{t('category_label', lang)}:</b> <code>{cat_name_safe}</code>\n"
        f"💵 <b>{t('price', lang)}:</b> <code>{currency}{product['price']:.2f}</code>\n"
        f"{stock_text}\n\n"
        f"📝 <b>{t('description_label', lang)}:</b>\n{desc_safe}\n\n"
        f"{delivery_info}\n\n"
        f"💰 <b>{t('balance', lang)}:</b> <code>{currency}{user_balance:.2f}</code>"
    )

    buttons = []
    if stock_count > 0:
        buttons.append([InlineKeyboardButton(t("btn_buy_balance", lang, symbol=currency, price=product['price']), callback_data=f"buybal_{product['id']}")])
        buttons.append([InlineKeyboardButton(t("btn_buy_crypto", lang, symbol=currency, price=product['price']), callback_data=f"buycrypto_{product['id']}")])
    else:
        buttons.append([InlineKeyboardButton(f"❌ {t('out_of_stock', lang)}", callback_data="noop")])

    cat_id = product.get("category_id")
    back_target = f"cat_{cat_id}" if cat_id else "user_categories"
    buttons.append([InlineKeyboardButton(t("btn_back_products", lang), callback_data=back_target)])

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

    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
    product_id = int(query.data.split("_")[1])
    product = await database.get_product(product_id)
    user = await database.get_user(user_id)
    currency = await database.get_setting("currency_symbol", "$")

    if not product or not user:
        await query.edit_message_text("❌ Product or User not found.")
        return

    # Check balance
    if user["balance"] < product["price"]:
        shortage = product["price"] - user["balance"]
        text = t("insufficient_balance", lang, symbol=currency, price=product["price"], balance=user["balance"], shortage=shortage)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_deposit_now", lang), callback_data="user_deposit")],
            [InlineKeyboardButton(t("btn_back_products", lang), callback_data=f"prod_{product['id']}")]
        ])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return

    # Process Digital Delivery
    if product["delivery_type"] == "digital":
        order_code = f"ORD_{int(time.time())}_{user_id % 10000}"
        items = await database.take_product_stock(product_id=product["id"], quantity=1, user_id=user_id, order_code=order_code)
        
        if not items:
            await query.edit_message_text(
                f"❌ <b>{t('out_of_stock', lang)}</b>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_back_categories", lang), callback_data="user_categories")]]),
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

        success_text = t(
            "purchase_success", lang,
            name=escape(product['name']),
            code=order_code,
            symbol=currency,
            price=product['price'],
            item=escape(delivered_item)
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_orders", lang), callback_data="user_orders"), InlineKeyboardButton(t("btn_continue_shopping", lang), callback_data="user_categories")],
            [InlineKeyboardButton(t("btn_back_main", lang), callback_data="user_menu")]
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
        
        prompt_text = t("manual_prompt", lang, name=escape(product['name']), symbol=currency, price=product['price'])
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel", callback_data=f"prod_{product['id']}")]
        ])
        await query.edit_message_text(prompt_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return MANUAL_ORDER_INPUT

async def handle_manual_order_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await database.get_user_language(user_id)
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

    success_text = t(
        "manual_submitted", lang,
        name=escape(product['name']),
        code=order_code,
        symbol=currency,
        price=product['price'],
        details=escape(user_text)
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_orders", lang), callback_data="user_orders"), InlineKeyboardButton(t("btn_back_main", lang), callback_data="user_menu")]
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
    user_id = query.from_user.id if query else update.effective_user.id
    lang = await database.get_user_language(user_id)

    if query:
        await query.answer()

    user = await database.get_or_create_user(user_id, update.effective_user.username, update.effective_user.first_name)
    currency = await database.get_setting("currency_symbol", "$")
    curr_name = await database.get_setting("currency_name", "USDT")

    text = t(
        "wallet_title", lang,
        symbol=currency,
        balance=user['balance'],
        currency=curr_name,
        deposited=user['total_deposited'],
        spent=user['total_spent']
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_deposit", lang), callback_data="user_deposit")],
        [InlineKeyboardButton(t("btn_back_main", lang), callback_data="user_menu")]
    ])

    if query:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def show_deposit_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
    await query.answer()

    currency = await database.get_setting("currency_symbol", "$")
    min_dep = float(await database.get_setting("min_deposit", "1.0"))

    text = t("deposit_menu", lang, symbol=currency, min_dep=min_dep)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"{currency}5", callback_data="create_dep_5"),
            InlineKeyboardButton(f"{currency}10", callback_data="create_dep_10"),
            InlineKeyboardButton(f"{currency}25", callback_data="create_dep_25")
        ],
        [
            InlineKeyboardButton(f"{currency}50", callback_data="create_dep_50"),
            InlineKeyboardButton(f"{currency}100", callback_data="create_dep_100"),
            InlineKeyboardButton(t("btn_custom_amount", lang), callback_data="custom_deposit_btn")
        ],
        [InlineKeyboardButton(t("btn_wallet", lang), callback_data="user_wallet")]
    ])

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def prompt_custom_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
    await query.answer()

    min_dep = float(await database.get_setting("min_deposit", "1.0"))
    currency = await database.get_setting("currency_symbol", "$")

    text = t("custom_amount_prompt", lang, symbol=currency, min_dep=min_dep)
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="user_deposit")]])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return CUSTOM_DEPOSIT_AMOUNT

async def process_custom_deposit_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await database.get_user_language(user_id)
    text = update.message.text.replace("$", "").strip()
    min_dep = float(await database.get_setting("min_deposit", "1.0"))
    currency = await database.get_setting("currency_symbol", "$")

    try:
        amount = float(text)
        if amount < min_dep:
            await update.message.reply_text(
                t("invalid_amount_min", lang, symbol=currency, amount=amount, min_dep=min_dep),
                parse_mode=ParseMode.HTML
            )
            return CUSTOM_DEPOSIT_AMOUNT
        
        return await execute_create_deposit(update, context, amount=amount, user_id=user_id)
    except ValueError:
        await update.message.reply_text(
            t("invalid_amount_number", lang),
            parse_mode=ParseMode.HTML
        )
        return CUSTOM_DEPOSIT_AMOUNT

async def handle_preset_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    amount = float(query.data.split("_")[2])
    user_id = query.from_user.id
    await execute_create_deposit(update, context, amount=amount, user_id=user_id, is_callback=True)

async def execute_create_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE, amount: float, user_id: int, is_callback: bool = False):
    lang = await database.get_user_language(user_id)
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
        err_text = (
            f"❌ <b>Payment Gateway Error</b>\n\n"
            f"⚠️ {escape(res.get('message', 'Unable to create payment invoice.'))}\n\nPlease try again later."
        )
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(t("btn_wallet", lang), callback_data="user_wallet")]])
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

    invoice_text = t(
        "invoice_title", lang,
        code=merchant_trade_no,
        symbol=currency,
        amount=amount,
        bep20=bep20,
        trc20=trc20,
        erc20=erc20
    )

    buttons = []
    if checkout_url:
        buttons.append([InlineKeyboardButton(t("btn_pay_binance", lang), url=checkout_url)])
    
    buttons.append([
        InlineKeyboardButton(t("btn_check_status", lang), callback_data=f"chkdep_{merchant_trade_no}"),
        InlineKeyboardButton(t("btn_submit_tx", lang), callback_data=f"txstart_{merchant_trade_no}")
    ])
    buttons.append([
        InlineKeyboardButton(t("btn_show_qr", lang), callback_data=f"qrdep_{merchant_trade_no}"),
        InlineKeyboardButton(t("btn_wallet", lang), callback_data="user_wallet")
    ])

    keyboard = InlineKeyboardMarkup(buttons)

    if is_callback:
        await update.callback_query.edit_message_text(invoice_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    elif loading_msg:
        await loading_msg.edit_text(invoice_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    return ConversationHandler.END

async def check_deposit_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
    merchant_trade_no = query.data.split("_")[1]
    
    await query.answer("🔍 Checking payment status...")

    status_res = await payment_gateway.get_payment_status(merchant_trade_no)
    currency = await database.get_setting("currency_symbol", "$")

    if not status_res.get("success"):
        await query.answer(f"⚠️ {status_res.get('message', 'Failed to fetch status')}", show_alert=True)
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

            success_text = t(
                "deposit_confirmed", lang,
                code=merchant_trade_no,
                symbol=currency,
                amount=amount,
                network=paid_net
            )
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton(t("btn_shop", lang), callback_data="user_categories"), InlineKeyboardButton(t("btn_wallet", lang), callback_data="user_wallet")]
            ])
            await query.edit_message_text(success_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
            return
        else:
            await query.answer(t("deposit_already_credited", lang), show_alert=True)
            return
    elif status == "INITIAL":
        await query.answer(t("deposit_pending", lang), show_alert=True)
    else:
        await query.answer(f"ℹ️ Status: {status}", show_alert=True)

async def show_deposit_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
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
        [InlineKeyboardButton(t("btn_check_status", lang), callback_data=f"chkdep_{merchant_trade_no}")],
        [InlineKeyboardButton(t("btn_wallet", lang), callback_data="user_wallet")]
    ])

    await query.message.reply_photo(photo=qr_bio, caption=caption, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# -------------------- SUBMIT TX HASH CONVERSATION --------------------

async def start_submit_tx(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
    merchant_trade_no = query.data.split("_")[1]
    await query.answer()

    context.user_data["submit_tx_merchant_trade_no"] = merchant_trade_no

    text = t("submit_tx_select_net", lang, code=merchant_trade_no)

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
    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
    network = query.data.split("_")[1]
    await query.answer()

    context.user_data["submit_tx_network"] = network
    trade_no = context.user_data.get("submit_tx_merchant_trade_no", "")

    text = t("submit_tx_prompt", lang, code=trade_no, network=network)

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="user_wallet")]])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return SUBMIT_TX_HASH

def is_valid_tx_hash_format(tx_hash: str) -> bool:
    """Checks if a string looks like a genuine blockchain transaction hash."""
    import re
    cleaned = tx_hash.strip().lower()
    if len(cleaned) < 32 or len(cleaned) > 70:
        return False
    if " " in cleaned or ".." in cleaned:
        return False
    if re.fullmatch(r"^(0x)?[0-9a-fA-F]{32,66}$", cleaned):
        return True
    return False

async def handle_submit_tx_hash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = await database.get_user_language(user_id)
    tx_hash = update.message.text.strip()
    trade_no = context.user_data.get("submit_tx_merchant_trade_no")
    network = context.user_data.get("submit_tx_network", "BEP20")

    if not trade_no:
        await update.message.reply_text("Session expired. Please start again from /start.")
        return ConversationHandler.END

    # 1. Validate TxHash Format
    if not is_valid_tx_hash_format(tx_hash):
        warn_text = t("fake_tx_hash_warn", lang, hash=escape(tx_hash))
        await update.message.reply_text(warn_text, parse_mode=ParseMode.HTML)
        return SUBMIT_TX_HASH

    loading = await update.message.reply_text("⏳ <i>Verifying transaction with blockchain gateway...</i>", parse_mode=ParseMode.HTML)

    res = await payment_gateway.submit_tx_hash(merchant_trade_no=trade_no, network=network, tx_hash=tx_hash)

    if res.get("success"):
        text = t("tx_submitted_success", lang, code=trade_no, network=network, hash=escape(tx_hash))
    else:
        err_raw = res.get("message", "Order not found")
        text = t("tx_verification_failed", lang, reason=escape(err_raw), network=network)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_check_status", lang), callback_data=f"chkdep_{trade_no}")],
        [InlineKeyboardButton(t("btn_wallet", lang), callback_data="user_wallet")]
    ])

    await loading.edit_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    context.user_data.pop("submit_tx_merchant_trade_no", None)
    context.user_data.pop("submit_tx_network", None)
    return ConversationHandler.END

# -------------------- ORDERS & PROFILE --------------------

async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
    await query.answer()

    orders = await database.get_user_orders(user_id, limit=10)
    currency = await database.get_setting("currency_symbol", "$")

    if not orders:
        text = t("orders_empty", lang)
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_shop", lang), callback_data="user_categories")],
            [InlineKeyboardButton(t("btn_back_main", lang), callback_data="user_menu")]
        ])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return

    text = t("orders_title", lang)
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
        [InlineKeyboardButton(t("btn_continue_shopping", lang), callback_data="user_categories"), InlineKeyboardButton(t("btn_back_main", lang), callback_data="user_menu")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
    await query.answer()

    user = await database.get_user(user_id)
    currency = await database.get_setting("currency_symbol", "$")

    first_name_safe = escape(user.get('first_name', 'N/A'))
    username_safe = escape(user.get('username', 'N/A'))
    lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
    lang_display = f"{lang_info['flag']} {lang_info['name']}"

    text = t(
        "profile_title", lang,
        id=user['telegram_id'],
        name=first_name_safe,
        username=username_safe,
        symbol=currency,
        balance=user['balance'],
        deposited=user['total_deposited'],
        spent=user['total_spent'],
        language=lang_display,
        date=user.get('created_at', 'N/A')
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_deposit", lang), callback_data="user_deposit"), InlineKeyboardButton(t("btn_orders", lang), callback_data="user_orders")],
        [InlineKeyboardButton(t("btn_language", lang), callback_data="user_language_menu")],
        [InlineKeyboardButton(t("btn_back_main", lang), callback_data="user_menu")]
    ])

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    lang = await database.get_user_language(user_id)
    await query.answer()

    support_user = escape(await database.get_setting("support_username", "@Support"))
    text = t("support_text", lang, support=support_user)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_back_main", lang), callback_data="user_menu")]
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
