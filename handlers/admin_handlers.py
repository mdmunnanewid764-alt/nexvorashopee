import logging
import asyncio
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
import database
from config import ADMIN_ID, ADMIN_IDS
from locales import t, LANGUAGES

logger = logging.getLogger(__name__)

# Admin Conversation States
(
    ADD_CAT_NAME, ADD_CAT_EMOJI,
    ADD_PROD_CAT, ADD_PROD_NAME, ADD_PROD_DESC, ADD_PROD_PRICE, ADD_PROD_TYPE, ADD_PROD_IMAGE,
    ADD_STOCK_PROD, ADD_STOCK_ITEMS,
    EDIT_PROD_PRICE, EDIT_PROD_DESC,
    ADMIN_USER_SEARCH, ADMIN_USER_BALANCE_ADJ,
    ADMIN_BROADCAST_MSG,
    SETTING_EDIT_KEY,
    EDIT_PROMO_PRICE,
    ADMIN_PROMO_CONFIRM_LINK,
    EDIT_METH_DETAILS,
    EDIT_METH_RATE,
    EDIT_METH_INST
) = range(21)

def escape(text: str) -> str:
    return html.escape(str(text) if text is not None else "")

def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# -------------------- ADMIN DASHBOARD --------------------

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Renders Admin Panel Home.
    """
    user = update.effective_user
    if not is_admin(user.id):
        if update.callback_query:
            await update.callback_query.answer("⛔ Unauthorized. Admin access only.", show_alert=True)
        else:
            await update.message.reply_text("⛔ Unauthorized. Admin access only.")
        return

    stats = await database.get_bot_stats()
    currency = await database.get_setting("currency_symbol", "$")
    promo_price = await database.get_setting("chatgpt_promo_price", "1.00")
    promo_enabled = await database.get_setting("chatgpt_promo_enabled", "1")
    promo_status_icon = "🟢 Active" if promo_enabled == "1" else "🔴 Disabled"

    text = (
        f"🛠 <b>Nexvora Admin Control Panel</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Total Users:</b> <code>{stats['total_users']}</code>\n"
        f"🛍 <b>Total Active Products:</b> <code>{stats['total_products']}</code>\n"
        f"🔑 <b>Total Available Stock:</b> <code>{stats['total_stock']}</code> items\n"
        f"📦 <b>Total Orders:</b> <code>{stats['total_orders']}</code> (<code>{currency}{stats['total_sales']:.2f}</code>)\n"
        f"📥 <b>Total Paid Deposits:</b> <code>{stats['total_deposits']}</code> (<code>{currency}{stats['total_deposited_amount']:.2f}</code>)\n"
        f"🔥 <b>ChatGPT 3M Promo:</b> {promo_status_icon} (<code>{currency}{promo_price}</code>)\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <i>Select an administrative action:</i>"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Product", callback_data="adm_add_product"),
            InlineKeyboardButton("📬 Add Stock", callback_data="adm_stock_menu")
        ],
        [
            InlineKeyboardButton("📦 Manage Products", callback_data="adm_list_products"),
            InlineKeyboardButton("🔥 ChatGPT Promo Settings", callback_data="adm_promo_menu")
        ],
        [
            InlineKeyboardButton("💳 Payment Gateways", callback_data="adm_methods_menu"),
            InlineKeyboardButton("📂 Manage Categories", callback_data="adm_cat_menu")
        ],
        [
            InlineKeyboardButton("💵 Add / Remove Balance", callback_data="adm_users_menu"),
            InlineKeyboardButton("📢 Broadcast Message", callback_data="adm_broadcast_start")
        ],
        [
            InlineKeyboardButton("⚙️ Bot & API Settings", callback_data="adm_settings"),
            InlineKeyboardButton("🔙 User Store View", callback_data="user_menu")
        ]
    ])

    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# -------------------- CHATGPT PROMO OFFER MANAGEMENT --------------------

async def admin_promo_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    currency = await database.get_setting("currency_symbol", "$")
    promo_enabled = await database.get_setting("chatgpt_promo_enabled", "1")
    promo_price = await database.get_setting("chatgpt_promo_price", "1.00")
    promo_title = await database.get_setting("chatgpt_promo_title", "ChatGPT 3-Month Promo Offer")

    status_badge = "🟢 ENABLED (Visible to users)" if promo_enabled == "1" else "🔴 DISABLED (Hidden from users)"
    toggle_btn_text = "🔴 Disable Promo" if promo_enabled == "1" else "🟢 Enable Promo"

    text = (
        f"🔥 <b>ChatGPT 3-Month Promo Offer Settings</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷 <b>Title:</b> <code>{escape(promo_title)}</code>\n"
        f"💵 <b>Current Price:</b> <code>{currency}{promo_price}</code>\n"
        f"📊 <b>Status:</b> {status_badge}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 Choose an action to edit this offer:"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(toggle_btn_text, callback_data="adm_toggle_promo")],
        [InlineKeyboardButton("💵 Edit Promo Price", callback_data="adm_edit_promo_price_start")],
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")]
    ])

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def admin_toggle_promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    current_enabled = await database.get_setting("chatgpt_promo_enabled", "1")
    new_val = "0" if current_enabled == "1" else "1"
    await database.set_setting("chatgpt_promo_enabled", new_val)
    await query.answer("Status updated!")
    await admin_promo_menu(update, context)

async def start_edit_promo_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    currency = await database.get_setting("currency_symbol", "$")
    promo_price = await database.get_setting("chatgpt_promo_price", "1.00")

    text = (
        f"💵 <b>Edit ChatGPT Promo Price</b>\n\n"
        f"Current price: <code>{currency}{promo_price}</code>\n\n"
        f"Please reply with the new price in USDT (e.g. <code>1.00</code>, <code>1.50</code>, or <code>2.00</code>):"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_promo_menu")]])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return EDIT_PROMO_PRICE

async def handle_edit_promo_price_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("$", "").strip()
    try:
        price = float(text)
        if price <= 0:
            await update.message.reply_text("⚠️ Price must be greater than 0. Please enter a valid number (e.g. 1.00):")
            return EDIT_PROMO_PRICE
        
        await database.set_setting("chatgpt_promo_price", f"{price:.2f}")
        currency = await database.get_setting("currency_symbol", "$")
        await update.message.reply_text(
            f"✅ ChatGPT Promo Price updated to: <code>{currency}{price:.2f}</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔥 Promo Settings Menu", callback_data="adm_promo_menu")]])
        )
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("⚠️ Invalid price format. Please enter numbers only (e.g. 1.00):")
        return EDIT_PROMO_PRICE

# -------------------- PROMO ORDER CONFIRM & REFUND ACTIONS --------------------

async def start_adm_promo_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⛔ Unauthorized.", show_alert=True)
        return ConversationHandler.END

    order_code = query.data.replace("adm_promo_confirm_", "")
    order = await database.get_order_by_code(order_code)

    if not order:
        await query.answer("⚠️ Order not found.", show_alert=True)
        return ConversationHandler.END

    if order["status"] == "COMPLETED":
        await query.answer("✅ This order is already confirmed & completed!", show_alert=True)
        return ConversationHandler.END

    if order["status"] == "CANCELLED_REFUNDED":
        await query.answer("❌ This order was already cancelled and refunded.", show_alert=True)
        return ConversationHandler.END

    await query.answer()
    context.user_data["confirm_promo_order_code"] = order_code

    user_email = order.get("delivery_data", "N/A")
    prompt_text = (
        f"🔗 <b>ChatGPT 3-Month Promo Activation</b>\n\n"
        f"🔖 <b>Order Code:</b> <code>{order_code}</code>\n"
        f"👤 <b>Buyer ID:</b> <code>{order['user_id']}</code>\n"
        f"📧 <b>Target Email:</b> <code>{escape(user_email)}</code>\n\n"
        f"👉 <b>Please send / reply with the Promo Code / Activation Link / Credentials:</b>\n"
        f"<i>(The user will automatically receive this link/code in their Telegram chat)</i>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel", callback_data=f"adm_cancel_promo_{order_code}")]
    ])
    await query.edit_message_text(prompt_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return ADMIN_PROMO_CONFIRM_LINK

async def handle_adm_promo_link_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    promo_link = update.message.text.strip()
    order_code = context.user_data.get("confirm_promo_order_code")

    if not order_code:
        await update.message.reply_text("Session expired. Please click the button on the order alert again.")
        return ConversationHandler.END

    order = await database.get_order_by_code(order_code)
    if not order:
        await update.message.reply_text("⚠️ Order not found.")
        return ConversationHandler.END

    user_email = order.get("delivery_data", "N/A")

    # Update database
    new_delivery_data = f"Target Email: {user_email}\nPromo Code / Link: {promo_link}"
    await database.update_order_delivery_data(order_code, new_delivery_data, status="COMPLETED")

    currency = await database.get_setting("currency_symbol", "$")

    # Notify User in their chosen language with the promo link!
    try:
        user_lang = await database.get_user_language(order["user_id"])
        user_msg = t(
            "chatgpt_promo_activated_user", user_lang,
            code=order_code,
            email=escape(user_email),
            link=escape(promo_link)
        )
        user_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_orders", user_lang), callback_data="user_orders"), InlineKeyboardButton(t("btn_back_main", user_lang), callback_data="user_menu")]
        ])
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=user_msg,
            reply_markup=user_keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.warning(f"Failed to notify user of activation: {e}")

    # Send Success confirmation to Admin
    admin_success = (
        f"✅ <b>ChatGPT Promo Order Confirmed & Delivered!</b>\n\n"
        f"🔖 <b>Order Code:</b> <code>{order_code}</code>\n"
        f"👤 <b>Buyer ID:</b> <code>{order['user_id']}</code>\n"
        f"📧 <b>Target Email:</b> <code>{escape(user_email)}</code>\n"
        f"💰 <b>Amount:</b> <code>{currency}{order['total_price']:.2f}</code>\n\n"
        f"🎁 <b>Delivered Link / Code:</b>\n"
        f"<code>{escape(promo_link)}</code>\n\n"
        f"✨ <i>The buyer has automatically received the promo link in their chat!</i>"
    )
    await update.message.reply_text(admin_success, parse_mode=ParseMode.HTML)

    # Send Group Order Delivery Log
    try:
        group_id_str = await database.get_setting("order_log_group_id", "-1003721268860")
        if group_id_str:
            buyer_user = await database.get_user(order["user_id"])
            b_name = buyer_user.get("first_name", "Customer") if buyer_user else "Customer"
            b_user = buyer_user.get("username", "") if buyer_user else ""
            b_handle = f"(@{escape(b_user)})" if b_user else ""
            group_msg = (
                f"🛍 <b>🎉 ORDER DELIVERED & ACTIVATED!</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📦 <b>Product:</b> <code>ChatGPT 3-Month Promo Offer</code>\n"
                f"💵 <b>Price Paid:</b> <code>{currency}{order['total_price']:.2f}</code>\n"
                f"👤 <b>Buyer:</b> {escape(b_name)}\n"
                f"🔖 <b>Order Code:</b> <code>{order_code}</code>\n"
                f"📊 <b>Status:</b> <code>✅ COMPLETED & DELIVERED</code>\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"✨ <i>Enjoy your ChatGPT 3-Month Subscription!</i>"
            )
            
            bot_username = context.bot.username
            if not bot_username:
                me = await context.bot.get_me()
                bot_username = me.username

            bot_url = f"https://t.me/{bot_username}?start=shop"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🛒 Open Bot / Buy Now 🤖", url=bot_url)]
            ])

            await context.bot.send_message(
                chat_id=int(group_id_str),
                text=group_msg,
                reply_markup=keyboard,
                parse_mode=ParseMode.HTML
            )
    except Exception as e:
        logger.warning(f"Failed to send delivery log to group: {e}")

    context.user_data.pop("confirm_promo_order_code", None)
    return ConversationHandler.END

async def cancel_adm_promo_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Activation cancelled.")
    order_code = query.data.replace("adm_cancel_promo_", "")
    order = await database.get_order_by_code(order_code)
    currency = await database.get_setting("currency_symbol", "$")

    if order:
        user_email = order.get("delivery_data", "N/A")
        text = (
            f"🚨 <b>ChatGPT 3-Month Promo Order</b>\n\n"
            f"👤 <b>Buyer ID:</b> <code>{order['user_id']}</code>\n"
            f"🏷 <b>Offer:</b> <code>ChatGPT 3-Month Promo</code>\n"
            f"📧 <b>Target Email:</b> <code>{escape(user_email)}</code>\n"
            f"💵 <b>Price Paid:</b> <code>{currency}{order['total_price']:.2f}</code>\n"
            f"🔖 <b>Order Code:</b> <code>{order_code}</code>\n\n"
            f"👇 <i>Admin Action: Confirm activation or Cancel with refund:</i>"
        )
        admin_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Confirm & Activate", callback_data=f"adm_promo_confirm_{order_code}"),
                InlineKeyboardButton("❌ Cancel & Refund", callback_data=f"adm_promo_refund_{order_code}")
            ]
        ])
        await query.edit_message_text(text, reply_markup=admin_keyboard, parse_mode=ParseMode.HTML)

    context.user_data.pop("confirm_promo_order_code", None)
    return ConversationHandler.END

async def handle_adm_promo_refund(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        await query.answer("⛔ Unauthorized.", show_alert=True)
        return

    order_code = query.data.replace("adm_promo_refund_", "")
    order = await database.get_order_by_code(order_code)

    if not order:
        await query.answer("⚠️ Order not found.", show_alert=True)
        return

    if order["status"] == "CANCELLED_REFUNDED":
        await query.answer("❌ This order is already refunded!", show_alert=True)
        return

    if order["status"] == "COMPLETED":
        await query.answer("⚠️ This order was already marked completed.", show_alert=True)
        return

    # Refund the user balance
    refund_amount = float(order["total_price"])
    await database.update_user_balance(order["user_id"], refund_amount, is_deposit=True)
    await database.update_order_status(order_code, "CANCELLED_REFUNDED")

    await query.answer(f"❌ Order cancelled & ${refund_amount:.2f} refunded to user!", show_alert=True)

    # Update admin message
    currency = await database.get_setting("currency_symbol", "$")
    updated_admin_text = (
        f"❌ <b>ChatGPT Promo Order Cancelled & Refunded!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔖 <b>Order Code:</b> <code>{order_code}</code>\n"
        f"👤 <b>Buyer ID:</b> <code>{order['user_id']}</code>\n"
        f"📧 <b>Target Email:</b> <code>{escape(order['delivery_data'])}</code>\n"
        f"💰 <b>Refunded Amount:</b> <code>{currency}{refund_amount:.2f}</code> (Credited back to wallet)\n"
        f"📊 <b>Status:</b> <code>CANCELLED_REFUNDED</code>"
    )
    try:
        await query.edit_message_text(updated_admin_text, parse_mode=ParseMode.HTML)
    except Exception:
        pass

    # Notify User in their language
    try:
        user_lang = await database.get_user_language(order["user_id"])
        user_msg = t(
            "chatgpt_promo_refunded_user", user_lang,
            code=order_code,
            symbol=currency,
            price=refund_amount
        )
        user_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_wallet", user_lang), callback_data="user_wallet"), InlineKeyboardButton(t("btn_back_main", user_lang), callback_data="user_menu")]
        ])
        await context.bot.send_message(
            chat_id=order["user_id"],
            text=user_msg,
            reply_markup=user_keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.warning(f"Failed to notify user of refund: {e}")

# -------------------- CATEGORY MANAGEMENT --------------------

async def admin_cat_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    categories = await database.get_categories()
    text = "📂 <b>Category Management</b>\n\nExisting categories:\n"
    for cat in categories:
        text += f"• {cat.get('emoji', '📁')} <b>{escape(cat['name'])}</b> (ID: <code>{cat['id']}</code>)\n"

    buttons = [
        [InlineKeyboardButton("➕ Add New Category", callback_data="adm_add_cat_start")],
    ]
    for cat in categories:
        buttons.append([InlineKeyboardButton(f"🗑 Delete '{cat['name']}'", callback_data=f"adm_del_cat_{cat['id']}")])
    buttons.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")])

    keyboard = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def start_add_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📂 <b>Add New Category</b>\n\nPlease enter the Category Name (e.g. <i>VPN Accounts</i>):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_cat_menu")]]),
        parse_mode=ParseMode.HTML
    )
    return ADD_CAT_NAME

async def handle_add_cat_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_cat_name"] = update.message.text.strip()
    await update.message.reply_text(
        f"Great! Category Name: <b>{escape(context.user_data['new_cat_name'])}</b>\n\n"
        "Now reply with an Emoji for this category (e.g. 🛡️ or 🎮):",
        parse_mode=ParseMode.HTML
    )
    return ADD_CAT_EMOJI

async def handle_add_cat_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emoji = update.message.text.strip()
    name = context.user_data.get("new_cat_name")

    cat_id = await database.add_category(name=name, emoji=emoji)
    await update.message.reply_text(
        f"✅ Category <b>{emoji} {escape(name)}</b> created successfully! (ID: <code>{cat_id}</code>)",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📂 Category Menu", callback_data="adm_cat_menu")]]),
        parse_mode=ParseMode.HTML
    )
    context.user_data.pop("new_cat_name", None)
    return ConversationHandler.END

async def handle_del_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cat_id = int(query.data.split("_")[3])
    await database.delete_category(cat_id)
    await query.answer("Category deleted!", show_alert=True)
    await admin_cat_menu(update, context)

# -------------------- PRODUCT MANAGEMENT --------------------

async def admin_list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    products = await database.get_all_products(include_inactive=True)
    currency = await database.get_setting("currency_symbol", "$")

    text = "📦 <b>Product Management</b>\n\nAll existing products:\n"
    buttons = []

    for p in products:
        status_icon = "🟢" if p["is_active"] else "🔴"
        stock = await database.get_available_stock_count(p["id"]) if p["delivery_type"] == "digital" else "Service"
        text += f"{status_icon} <b>{escape(p['name'])}</b> | <code>{currency}{p['price']:.2f}</code> | Stock: <code>{stock}</code>\n"
        buttons.append([
            InlineKeyboardButton(f"⚙️ {p['name']} ({currency}{p['price']:.2f})", callback_data=f"adm_manage_prod_{p['id']}")
        ])

    buttons.append([InlineKeyboardButton("➕ Add New Product", callback_data="adm_add_product")])
    buttons.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")])

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def admin_manage_single_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    product_id = int(query.data.split("_")[3])
    await query.answer()

    product = await database.get_product(product_id)
    if not product:
        await query.edit_message_text("Product not found.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="adm_list_products")]]))
        return

    currency = await database.get_setting("currency_symbol", "$")
    stock = await database.get_available_stock_count(product["id"]) if product["delivery_type"] == "digital" else "Manual Service"
    status_str = "🟢 Active (Visible)" if product["is_active"] else "🔴 Inactive (Hidden)"

    text = (
        f"⚙️ <b>Manage Product: {escape(product['name'])}</b>\n\n"
        f"📁 <b>Category:</b> {escape(product.get('category_name', 'None'))}\n"
        f"💵 <b>Price:</b> <code>{currency}{product['price']:.2f}</code>\n"
        f"📦 <b>Delivery Type:</b> <code>{product['delivery_type']}</code>\n"
        f"🔑 <b>Stock:</b> <code>{stock}</code>\n"
        f"📊 <b>Status:</b> {status_str}\n\n"
        f"📝 <b>Description:</b>\n{escape(product.get('description') or 'N/A')}"
    )

    toggle_status_text = "🔴 Deactivate" if product["is_active"] else "🟢 Activate"
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Stock", callback_data=f"adm_add_stock_{product['id']}"),
            InlineKeyboardButton(toggle_status_text, callback_data=f"adm_toggle_prod_{product['id']}")
        ],
        [
            InlineKeyboardButton("🗑 Delete Product", callback_data=f"adm_del_prod_{product['id']}"),
            InlineKeyboardButton("🔙 Back to Products", callback_data="adm_list_products")
        ]
    ])

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def handle_toggle_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    product_id = int(query.data.split("_")[3])
    product = await database.get_product(product_id)
    if product:
        new_status = 0 if product["is_active"] else 1
        await database.update_product(product_id, is_active=new_status)
        await query.answer("Product status updated!")
    await admin_manage_single_product(update, context)

async def handle_delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    product_id = int(query.data.split("_")[3])
    await database.delete_product(product_id)
    await query.answer("Product deleted!", show_alert=True)
    await admin_list_products(update, context)

# Add Product Flow
async def start_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    categories = await database.get_categories()
    if not categories:
        await query.edit_message_text(
            "⚠️ Please create at least one Category before adding products.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ Add Category", callback_data="adm_add_cat_start")]])
        )
        return ConversationHandler.END

    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(f"{cat.get('emoji', '📁')} {cat['name']}", callback_data=f"selcat_{cat['id']}")])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="admin_home")])

    await query.edit_message_text(
        "🛍 <b>Add New Product: Step 1/6</b>\n\nSelect the Category for this product:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )
    return ADD_PROD_CAT

async def handle_prod_cat_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cat_id = int(query.data.split("_")[1])
    await query.answer()

    context.user_data["new_prod_cat_id"] = cat_id
    await query.edit_message_text(
        "🛍 <b>Add New Product: Step 2/6</b>\n\nReply with the <b>Product Name</b> (e.g. <i>NordVPN 1-Month Account</i>):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_home")]]),
        parse_mode=ParseMode.HTML
    )
    return ADD_PROD_NAME

async def handle_prod_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_prod_name"] = update.message.text.strip()
    await update.message.reply_text(
        "🛍 <b>Add New Product: Step 3/6</b>\n\nReply with a detailed <b>Product Description / Features</b>:",
        parse_mode=ParseMode.HTML
    )
    return ADD_PROD_DESC

async def handle_prod_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_prod_desc"] = update.message.text.strip()
    currency = await database.get_setting("currency_symbol", "$")
    await update.message.reply_text(
        f"🛍 <b>Add New Product: Step 4/6</b>\n\nReply with the <b>Price in {currency}</b> (e.g. <code>5.00</code> or <code>12.50</code>):",
        parse_mode=ParseMode.HTML
    )
    return ADD_PROD_PRICE

async def handle_prod_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("$", "").strip()
    try:
        price = float(text)
        context.user_data["new_prod_price"] = price

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("⚡ Instant Digital Key / Auto-Delivery", callback_data="prodtype_digital")],
            [InlineKeyboardButton("🛠 Manual Service / Custom Order", callback_data="prodtype_manual")],
            [InlineKeyboardButton("❌ Cancel", callback_data="admin_home")]
        ])

        await update.message.reply_text(
            "🛍 <b>Add New Product: Step 5/6</b>\n\nChoose the <b>Delivery Type</b>:",
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
        return ADD_PROD_TYPE
    except ValueError:
        await update.message.reply_text("⚠️ Invalid price. Please enter numbers only (e.g. 5.50):")
        return ADD_PROD_PRICE

async def handle_prod_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    dtype = query.data.split("_")[1]
    await query.answer()

    context.user_data["new_prod_dtype"] = dtype

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⏩ Skip Image", callback_data="skip_prod_img")],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_home")]
    ])

    await query.edit_message_text(
        "🛍 <b>Add New Product: Step 6/6</b>\n\nSend a direct Image URL (e.g. <code>https://i.imgur.com/...jpg</code>) or click Skip:",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    return ADD_PROD_IMAGE

async def handle_prod_image_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    img_url = update.message.text.strip()
    return await finish_add_product(update, context, img_url=img_url)

async def handle_skip_prod_img(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    return await finish_add_product(update, context, img_url=None, is_callback=True)

async def finish_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE, img_url: str = None, is_callback: bool = False):
    cat_id = context.user_data.get("new_prod_cat_id")
    name = context.user_data.get("new_prod_name")
    desc = context.user_data.get("new_prod_desc")
    price = context.user_data.get("new_prod_price")
    dtype = context.user_data.get("new_prod_dtype")

    currency = await database.get_setting("currency_symbol", "$")

    prod_id = await database.add_product(
        category_id=cat_id,
        name=name,
        description=desc,
        price=price,
        image_url=img_url,
        delivery_type=dtype
    )

    success_text = (
        f"🎉 <b>Product Added Successfully!</b>\n\n"
        f"🏷 <b>Name:</b> <code>{escape(name)}</code>\n"
        f"💵 <b>Price:</b> <code>{currency}{price:.2f}</code>\n"
        f"📦 <b>Type:</b> <code>{dtype}</code>\n"
        f"🆔 <b>Product ID:</b> <code>{prod_id}</code>\n\n"
        f"<i>You can now add stock items if this is an instant digital product.</i>"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Stock Items", callback_data=f"adm_add_stock_{prod_id}")],
        [InlineKeyboardButton("📦 Product List", callback_data="adm_list_products"), InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_home")]
    ])

    if is_callback:
        await update.callback_query.edit_message_text(success_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(success_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    context.user_data.clear()
    return ConversationHandler.END

# -------------------- STOCK MANAGEMENT --------------------

async def admin_stock_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    products = await database.get_all_products()
    digital_products = [p for p in products if p["delivery_type"] == "digital"]

    text = "🔑 <b>Digital Product Stock Management</b>\n\nSelect a product to view or upload digital stock items:\n\n"
    buttons = []
    for p in digital_products:
        count = await database.get_available_stock_count(p["id"])
        text += f"• <b>{escape(p['name'])}</b>: <code>{count}</code> items available\n"
        buttons.append([InlineKeyboardButton(f"➕ Add Stock to {p['name']} ({count})", callback_data=f"adm_add_stock_{p['id']}")])

    buttons.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")])
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def start_add_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    prod_id = int(query.data.split("_")[3])
    await query.answer()

    product = await database.get_product(prod_id)
    if not product:
        await query.edit_message_text("Product not found.")
        return ConversationHandler.END

    context.user_data["add_stock_prod_id"] = prod_id

    text = (
        f"🔑 <b>Upload Stock for: {escape(product['name'])}</b>\n\n"
        f"Please reply with your stock items/keys/accounts (<b>One item per line</b>):\n\n"
        f"<i>Example:</i>\n"
        f"<code>email1@test.com:pass123\nemail2@test.com:pass456\nlicense-key-789XYZ</code>"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_stock_menu")]])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return ADD_STOCK_ITEMS

async def handle_add_stock_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = [line.strip() for line in update.message.text.split("\n") if line.strip()]
    prod_id = context.user_data.get("add_stock_prod_id")

    if not prod_id:
        await update.message.reply_text("Session expired.")
        return ConversationHandler.END

    product = await database.get_product(prod_id)
    added_count = await database.add_product_stock_bulk(prod_id, lines)
    total_avail = await database.get_available_stock_count(prod_id)

    await update.message.reply_text(
        f"✅ <b>Successfully Added {added_count} Items!</b>\n\n"
        f"📦 Product: <b>{escape(product['name'])}</b>\n"
        f"🔑 Total In-Stock: <code>{total_avail}</code> items",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add More", callback_data=f"adm_add_stock_{prod_id}"), InlineKeyboardButton("🔑 Stock Menu", callback_data="adm_stock_menu")],
            [InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_home")]
        ]),
        parse_mode=ParseMode.HTML
    )
    context.user_data.pop("add_stock_prod_id", None)
    return ConversationHandler.END

# -------------------- USER MANAGEMENT --------------------

async def admin_users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

    currency = await database.get_setting("currency_symbol", "$")
    users = await database.get_all_users(limit=15)

    text = (
        f"💵 <b>User Balance Management</b>\n\n"
        f"Select a registered user below to Add (+) or Deduct (-) balance, or search by Username / ID:"
    )

    buttons = [
        [InlineKeyboardButton("🔍 Search User by Username / ID", callback_data="adm_search_user_btn")]
    ]

    for u in users:
        u_name = escape(u.get("first_name") or u.get("username") or str(u["telegram_id"]))
        u_handle = f"@{escape(u['username'])}" if u.get("username") else f"ID: {u['telegram_id']}"
        buttons.append([
            InlineKeyboardButton(f"👤 {u_name} ({u_handle}) — {currency}{u['balance']:.2f}", callback_data=f"adm_view_user_{u['telegram_id']}")
        ])

    buttons.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")])

    keyboard = InlineKeyboardMarkup(buttons)
    if query:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def admin_view_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[3])
    user = await database.get_user(user_id)
    currency = await database.get_setting("currency_symbol", "$")

    if not user:
        await query.answer("User not found.", show_alert=True)
        return

    text, keyboard = build_user_card(user, currency)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def prompt_search_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🔍 <b>Search User</b>\n\nPlease enter the user's Telegram ID (e.g. <code>123456789</code>) or @Username:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_users_menu")]]),
        parse_mode=ParseMode.HTML
    )
    return ADMIN_USER_SEARCH

def build_user_card(user: dict, currency: str) -> tuple[str, InlineKeyboardMarkup]:
    lang = user.get("language", "en")
    lang_info = LANGUAGES.get(lang, LANGUAGES["en"])
    user_info = (
        f"👤 <b>User Management Card</b>\n\n"
        f"🆔 <b>Telegram ID:</b> <code>{user['telegram_id']}</code>\n"
        f"👤 <b>Name:</b> {escape(user.get('first_name', 'N/A'))}\n"
        f"🏷 <b>Username:</b> @{escape(user.get('username', 'N/A'))}\n"
        f"🌐 <b>Language:</b> {lang_info['flag']} {lang_info['name']}\n"
        f"💰 <b>Wallet Balance:</b> <code>{currency}{user['balance']:.2f}</code>\n"
        f"📥 <b>Total Deposited:</b> <code>{currency}{user['total_deposited']:.2f}</code>\n"
        f"🛒 <b>Total Spent:</b> <code>{currency}{user['total_spent']:.2f}</code>\n"
        f"📅 <b>Joined:</b> <code>{user.get('created_at', 'N/A')}</code>\n\n"
        f"👇 <i>Choose a preset or enter a custom amount to Add (+) or Deduct (-):</i>"
    )

    uid = user["telegram_id"]
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"➕ {currency}5", callback_data=f"adm_adj_bal_{uid}_5"),
            InlineKeyboardButton(f"➕ {currency}10", callback_data=f"adm_adj_bal_{uid}_10"),
            InlineKeyboardButton(f"➕ {currency}25", callback_data=f"adm_adj_bal_{uid}_25"),
            InlineKeyboardButton(f"➕ {currency}50", callback_data=f"adm_adj_bal_{uid}_50")
        ],
        [
            InlineKeyboardButton(f"➖ {currency}5", callback_data=f"adm_adj_bal_{uid}_-5"),
            InlineKeyboardButton(f"➖ {currency}10", callback_data=f"adm_adj_bal_{uid}_-10"),
            InlineKeyboardButton(f"➖ {currency}25", callback_data=f"adm_adj_bal_{uid}_-25"),
            InlineKeyboardButton(f"➖ {currency}50", callback_data=f"adm_adj_bal_{uid}_-50")
        ],
        [
            InlineKeyboardButton("✏️ Custom Amount (+ / -)", callback_data=f"adm_custom_bal_{uid}")
        ],
        [
            InlineKeyboardButton("🔍 Search Another User", callback_data="adm_search_user_btn"),
            InlineKeyboardButton("👥 Users Menu", callback_data="adm_users_menu")
        ]
    ])
    return user_info, keyboard

async def handle_user_search_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.message.text.replace("@", "").strip()
    currency = await database.get_setting("currency_symbol", "$")

    user = await database.get_user_by_id_or_username(query_text)

    if not user:
        await update.message.reply_text(
            f"❌ <b>User Not Found!</b>\n\nNo user account found matching ID or Username: <code>{escape(query_text)}</code>\n<i>(Note: User must have started the bot at least once)</i>",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Try Again", callback_data="adm_search_user_btn")],
                [InlineKeyboardButton("👥 Back to Users", callback_data="adm_users_menu")]
            ]),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

    text, keyboard = build_user_card(user, currency)
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return ConversationHandler.END

async def handle_balance_adjust(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    parts = query.data.split("_")
    user_id = int(parts[3])
    amount = float(parts[4])
    currency = await database.get_setting("currency_symbol", "$")

    await database.update_user_balance(user_id, amount, is_deposit=(amount > 0))
    action_word = "Added" if amount > 0 else "Deducted"
    await query.answer(f"✅ Successfully {action_word} {currency}{abs(amount):.2f}!", show_alert=True)

    # Notify User in their language
    try:
        user_lang = await database.get_user_language(user_id)
        if amount > 0:
            notif = f"🎁 <b>Balance Added by Admin!</b>\n\n<code>+{currency}{amount:.2f}</code> has been added to your wallet balance."
        else:
            notif = f"⚠️ <b>Balance Adjustment by Admin:</b>\n\n<code>-{currency}{abs(amount):.2f}</code> was deducted from your wallet balance."
        await context.bot.send_message(chat_id=user_id, text=notif, parse_mode=ParseMode.HTML)
    except Exception:
        pass

    # Refresh user card in-place
    user = await database.get_user(user_id)
    if user:
        text, keyboard = build_user_card(user, currency)
        try:
            await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        except Exception:
            pass

async def start_custom_balance_adjust(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = int(query.data.split("_")[3])
    context.user_data["target_bal_user_id"] = user_id

    user = await database.get_user(user_id)
    currency = await database.get_setting("currency_symbol", "$")
    first_name = user.get("first_name", "User") if user else "User"
    current_bal = user["balance"] if user else 0.0

    prompt = (
        f"✏️ <b>Adjust Balance for {escape(first_name)}</b> (ID: <code>{user_id}</code>)\n\n"
        f"💰 <b>Current Balance:</b> <code>{currency}{current_bal:.2f}</code>\n\n"
        f"📌 <b>Enter Amount to Add or Deduct:</b>\n"
        f"• To Add balance: enter a positive number (e.g. <code>25</code> or <code>50.50</code>)\n"
        f"• To Deduct balance: enter a negative number (e.g. <code>-15</code> or <code>-30.00</code>)"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_users_menu")]])
    await query.edit_message_text(prompt, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return ADMIN_USER_BALANCE_ADJ

async def handle_custom_balance_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("$", "").replace("+", "").strip()
    user_id = context.user_data.get("target_bal_user_id")
    currency = await database.get_setting("currency_symbol", "$")

    if not user_id:
        await update.message.reply_text("Session expired. Please search for user again from /admin.")
        return ConversationHandler.END

    try:
        amount = float(text)
    except ValueError:
        await update.message.reply_text(
            "❌ <b>Invalid Input!</b>\nPlease enter a valid number (e.g. <code>25</code> to add, or <code>-10</code> to deduct):",
            parse_mode=ParseMode.HTML
        )
        return ADMIN_USER_BALANCE_ADJ

    await database.update_user_balance(user_id, amount, is_deposit=(amount > 0))
    action_word = "Added" if amount > 0 else "Deducted"

    # Notify User in their language
    try:
        user_lang = await database.get_user_language(user_id)
        if amount > 0:
            notif = f"🎁 <b>Balance Added by Admin!</b>\n\n<code>+{currency}{amount:.2f}</code> has been added to your wallet balance."
        else:
            notif = f"⚠️ <b>Balance Adjustment by Admin:</b>\n\n<code>-{currency}{abs(amount):.2f}</code> was deducted from your wallet balance."
        await context.bot.send_message(chat_id=user_id, text=notif, parse_mode=ParseMode.HTML)
    except Exception:
        pass

    user = await database.get_user(user_id)
    success_msg = f"✅ <b>Successfully {action_word} {currency}{abs(amount):.2f}!</b>\n\n"
    if user:
        card_text, keyboard = build_user_card(user, currency)
        await update.message.reply_text(success_msg + card_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(success_msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("👥 Users Menu", callback_data="adm_users_menu")]]), parse_mode=ParseMode.HTML)

    context.user_data.pop("target_bal_user_id", None)
    return ConversationHandler.END

# -------------------- DIRECT ADMIN BALANCE COMMANDS --------------------

async def add_balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /addbalance <USER_ID_OR_USERNAME> <AMOUNT>"""
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: <code>/addbalance &lt;telegram_id_or_@username&gt; &lt;amount&gt;</code>\nExample: <code>/addbalance 123456789 25</code> or <code>/addbalance @username 10</code>",
            parse_mode=ParseMode.HTML
        )
        return

    target_id_raw = context.args[0].strip()
    try:
        amount = float(context.args[1].replace("$", "").replace("+", "").strip())
        if amount <= 0:
            await update.message.reply_text("Amount must be greater than 0.")
            return
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Must be a number.")
        return

    user = await database.get_user_by_id_or_username(target_id_raw)
    if not user:
        await update.message.reply_text(f"❌ User not found with ID/Username: <code>{escape(target_id_raw)}</code>", parse_mode=ParseMode.HTML)
        return

    currency = await database.get_setting("currency_symbol", "$")
    user_id = user["telegram_id"]
    await database.update_user_balance(user_id, amount, is_deposit=True)

    # Notify User
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎁 <b>Balance Added by Admin!</b>\n\n<code>+{currency}{amount:.2f}</code> has been added to your wallet balance.",
            parse_mode=ParseMode.HTML
        )
    except Exception:
        pass

    updated_user = await database.get_user(user_id)
    await update.message.reply_text(
        f"✅ <b>Added {currency}{amount:.2f} to user!</b>\n\n"
        f"👤 User: <code>{updated_user.get('first_name', 'N/A')}</code> (@{updated_user.get('username', 'N/A')})\n"
        f"🆔 Telegram ID: <code>{user_id}</code>\n"
        f"💰 New Balance: <code>{currency}{updated_user['balance']:.2f}</code>",
        parse_mode=ParseMode.HTML
    )

async def deduct_balance_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Command: /deductbalance <USER_ID_OR_USERNAME> <AMOUNT>"""
    if not is_admin(update.effective_user.id):
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: <code>/deductbalance &lt;telegram_id_or_@username&gt; &lt;amount&gt;</code>\nExample: <code>/deductbalance 123456789 10</code> or <code>/deductbalance @username 5</code>",
            parse_mode=ParseMode.HTML
        )
        return

    target_id_raw = context.args[0].strip()
    try:
        amount = float(context.args[1].replace("$", "").replace("-", "").strip())
        if amount <= 0:
            await update.message.reply_text("Amount must be greater than 0.")
            return
    except ValueError:
        await update.message.reply_text("❌ Invalid amount. Must be a number.")
        return

    user = await database.get_user_by_id_or_username(target_id_raw)
    if not user:
        await update.message.reply_text(f"❌ User not found with ID/Username: <code>{escape(target_id_raw)}</code>", parse_mode=ParseMode.HTML)
        return

    currency = await database.get_setting("currency_symbol", "$")
    user_id = user["telegram_id"]
    await database.update_user_balance(user_id, -amount, is_spend=False)

    # Notify User
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"⚠️ <b>Balance Adjustment by Admin:</b>\n\n<code>-{currency}{amount:.2f}</code> was deducted from your wallet balance.",
            parse_mode=ParseMode.HTML
        )
    except Exception:
        pass

    updated_user = await database.get_user(user_id)
    await update.message.reply_text(
        f"✅ <b>Deducted {currency}{amount:.2f} from user!</b>\n\n"
        f"👤 User: <code>{updated_user.get('first_name', 'N/A')}</code> (@{updated_user.get('username', 'N/A')})\n"
        f"🆔 Telegram ID: <code>{user_id}</code>\n"
        f"💰 New Balance: <code>{currency}{updated_user['balance']:.2f}</code>",
        parse_mode=ParseMode.HTML
    )

# -------------------- BROADCAST --------------------

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "📢 <b>Broadcast Announcement</b>\n\n"
        "Please send the message you want to broadcast to all users.\n"
        "HTML formatting is supported.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_home")]]),
        parse_mode=ParseMode.HTML
    )
    return ADMIN_BROADCAST_MSG

async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    broadcast_text = update.message.text
    users = await database.get_all_users(limit=10000)

    status_msg = await update.message.reply_text(f"🚀 <i>Broadcasting to {len(users)} users...</i>", parse_mode=ParseMode.HTML)

    success, failed = 0, 0
    for u in users:
        try:
            await context.bot.send_message(
                chat_id=u["telegram_id"],
                text=broadcast_text,
                parse_mode=ParseMode.HTML
            )
            success += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await status_msg.edit_text(
        f"✅ <b>Broadcast Completed!</b>\n\n"
        f"📤 Total Sent: <code>{success}</code>\n"
        f"❌ Failed / Blocked: <code>{failed}</code>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_home")]]),
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

# -------------------- SETTINGS --------------------

async def admin_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    api_key = await database.get_setting("binance_api_key", "Not Set")
    masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else api_key
    currency = await database.get_setting("currency_symbol", "$")
    curr_name = await database.get_setting("currency_name", "USDT")
    support = await database.get_setting("support_username", "@Support")
    min_dep = await database.get_setting("min_deposit", "1.0")

    text = (
        f"⚙️ <b>Bot & Payment Configuration</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔑 <b>Binance API Key:</b> <code>{masked_key}</code>\n"
        f"💵 <b>Currency:</b> <code>{currency}</code> ({curr_name})\n"
        f"👨‍💻 <b>Support Username:</b> <code>{escape(support)}</code>\n"
        f"📥 <b>Min Deposit:</b> <code>{currency}{min_dep}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Click below to modify any setting:"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Change Binance API Key", callback_data="editset_binance_api_key")],
        [InlineKeyboardButton("👨‍💻 Change Support Handle", callback_data="editset_support_username")],
        [InlineKeyboardButton("📥 Change Min Deposit", callback_data="editset_min_deposit")],
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")]
    ])

    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def start_edit_setting(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    setting_key = query.data.replace("editset_", "")
    await query.answer()

    context.user_data["editing_setting_key"] = setting_key

    prompts = {
        "binance_api_key": "Please reply with your new Merchant API Key (e.g. <code>bg_live_...</code>):",
        "support_username": "Please reply with your support username (e.g. <code>@MySupportAdmin</code>):",
        "min_deposit": "Please reply with the new minimum deposit amount (e.g. <code>5</code>):"
    }

    await query.edit_message_text(
        f"⚙️ <b>Edit Setting:</b> <code>{setting_key}</code>\n\n{prompts.get(setting_key, 'Please enter new value:')}",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_settings")]]),
        parse_mode=ParseMode.HTML
    )
    return SETTING_EDIT_KEY

async def handle_edit_setting_val(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_val = update.message.text.strip()
    setting_key = context.user_data.get("editing_setting_key")

    if not setting_key:
        await update.message.reply_text("Session expired.")
        return ConversationHandler.END

    await database.set_setting(setting_key, new_val)
    await update.message.reply_text(
        f"✅ Setting <code>{setting_key}</code> updated to: <code>{escape(new_val)}</code>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⚙️ Settings Menu", callback_data="adm_settings")]])
    )
    context.user_data.pop("editing_setting_key", None)
    return ConversationHandler.END


# -------------------- MANUAL DEPOSIT ADMIN APPROVALS --------------------

async def handle_adm_appr_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Approves manual deposit, credits balance to user, sends user notification.
    """
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("⛔ Unauthorized.", show_alert=True)
        return

    dep_id = int(query.data.split("_")[3])
    deposit = await database.approve_manual_deposit(dep_id)

    if not deposit:
        await query.answer("⚠️ Deposit not found or already processed.", show_alert=True)
        return

    currency = await database.get_setting("currency_symbol", "$")
    target_user_id = deposit["user_id"]
    target_user = await database.get_user(target_user_id)
    user_lang = target_user.get("language", "en") if target_user else "en"
    amount = float(deposit["order_amount"])
    bdt_amount = float(deposit.get("bdt_amount", 0.0))
    method_type = deposit.get("method_type", "Manual")
    trade_no = deposit.get("merchant_trade_no", "")

    await query.answer(f"✅ Approved! ${amount:.2f} credited.", show_alert=True)

    # Update admin message
    approved_text = (
        f"{query.message.text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>STATUS: APPROVED & CREDITED</b>\n"
        f"👤 <b>Approved By:</b> Admin (<code>{user_id}</code>)\n"
        f"💰 <b>Credited Amount:</b> <code>{currency}{amount:.2f}</code>"
    )
    await query.edit_message_text(approved_text, parse_mode=ParseMode.HTML)

    # Send Notification to User in User's Language
    try:
        user_notify_text = t(
            "deposit_approved_user", user_lang,
            code=trade_no,
            symbol=currency,
            amount=amount,
            method=method_type.upper()
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_wallet", user_lang), callback_data="user_wallet")],
            [InlineKeyboardButton(t("btn_shop", user_lang), callback_data="user_categories")]
        ])
        await context.bot.send_message(
            chat_id=target_user_id,
            text=user_notify_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.warning(f"Could not send deposit approval notice to user {target_user_id}: {e}")

async def handle_adm_rej_deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Rejects manual deposit and notifies user.
    """
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        await query.answer("⛔ Unauthorized.", show_alert=True)
        return

    dep_id = int(query.data.split("_")[3])
    deposit = await database.reject_manual_deposit(dep_id)

    if not deposit:
        await query.answer("⚠️ Deposit not found.", show_alert=True)
        return

    target_user_id = deposit["user_id"]
    target_user = await database.get_user(target_user_id)
    user_lang = target_user.get("language", "en") if target_user else "en"
    trade_no = deposit.get("merchant_trade_no", "")
    method_type = deposit.get("method_type", "Manual")

    await query.answer("❌ Deposit rejected.", show_alert=True)

    # Update admin message
    rejected_text = (
        f"{query.message.text}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"❌ <b>STATUS: REJECTED</b>\n"
        f"👤 <b>Rejected By:</b> Admin (<code>{user_id}</code>)"
    )
    await query.edit_message_text(rejected_text, parse_mode=ParseMode.HTML)

    # Send Notification to User
    try:
        user_notify_text = t(
            "deposit_rejected_user", user_lang,
            code=trade_no,
            method=method_type.upper()
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("btn_support", user_lang), callback_data="user_support")]
        ])
        await context.bot.send_message(
            chat_id=target_user_id,
            text=user_notify_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.warning(f"Could not send deposit reject notice to user {target_user_id}: {e}")


# -------------------- PAYMENT METHODS (GATEWAYS) MANAGEMENT --------------------

async def admin_methods_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Lists all payment gateways (Crypto, bKash, Nagad, etc.) for admin to manage.
    """
    query = update.callback_query
    user_id = query.from_user.id if query else update.effective_user.id
    if not is_admin(user_id):
        return

    if query:
        await query.answer()

    methods = await database.get_payment_methods(active_only=False)

    text = (
        f"💳 <b>Payment Gateways & Deposit Configuration</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Manage all payment methods (Crypto Auto, bKash, Nagad, etc.).\n"
        f"Tap on any method to edit number, exchange rate, instructions, or toggle on/off:\n"
    )

    buttons = []
    for m in methods:
        status_icon = "🟢" if m.get("is_active") == 1 else "🔴"
        rate_info = f" (1$ = {m.get('exchange_rate', 125.0):.0f} BDT)" if m.get("method_type") != "crypto_auto" else ""
        btn_title = f"{status_icon} {m.get('name')}{rate_info}"
        buttons.append([InlineKeyboardButton(btn_title, callback_data=f"adm_manage_meth_{m['id']}")])

    buttons.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")])
    keyboard = InlineKeyboardMarkup(buttons)

    if query:
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def admin_manage_single_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows detail of a single method with options to edit number, rate, instructions, or toggle.
    """
    query = update.callback_query
    user_id = query.from_user.id
    if not is_admin(user_id):
        return

    await query.answer()
    method_id = int(query.data.split("_")[3])
    method = await database.get_payment_method(method_id)

    if not method:
        await query.answer("⚠️ Method not found.", show_alert=True)
        return await admin_methods_menu(update, context)

    status_str = "🟢 Active (Visible to Users)" if method.get("is_active") == 1 else "🔴 Disabled (Hidden from Users)"

    text = (
        f"💳 <b>Manage Gateway: {escape(method.get('name'))}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>Status:</b> {status_str}\n"
        f"🏷 <b>Type:</b> <code>{method.get('method_type')}</code>\n"
        f"📌 <b>Account Details / Number:</b> <code>{escape(method.get('details', 'N/A'))}</code>\n"
        f"💵 <b>Exchange Rate:</b> <code>1 USD = {method.get('exchange_rate', 125.0):.2f} BDT</code>\n"
        f"📥 <b>Min Deposit:</b> <code>${method.get('min_deposit', 1.0):.2f}</code>\n"
        f"📝 <b>Instructions:</b> <i>{escape(method.get('instructions', 'N/A'))}</i>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <i>Select an action to modify:</i>"
    )

    toggle_btn_text = "🔴 Disable Gateway" if method.get("is_active") == 1 else "🟢 Enable Gateway"

    buttons = [
        [InlineKeyboardButton(toggle_btn_text, callback_data=f"adm_toggle_meth_{method_id}")],
        [
            InlineKeyboardButton("✏️ Edit Number / Details", callback_data=f"adm_edit_mdet_{method_id}"),
            InlineKeyboardButton("💵 Edit Exchange Rate", callback_data=f"adm_edit_mrate_{method_id}")
        ],
        [
            InlineKeyboardButton("📝 Edit Instructions", callback_data=f"adm_edit_minst_{method_id}")
        ],
        [InlineKeyboardButton("🔙 Back to Gateways", callback_data="adm_methods_menu")]
    ]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def handle_toggle_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return

    method_id = int(query.data.split("_")[3])
    new_status = await database.toggle_payment_method(method_id)
    status_msg = "🟢 Method Enabled" if new_status == 1 else "🔴 Method Disabled"
    await query.answer(status_msg, show_alert=True)
    return await admin_manage_single_method(update, context)

# -------------------- EDIT METHOD CONVERSATIONS --------------------

async def start_edit_method_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return

    await query.answer()
    method_id = int(query.data.split("_")[3])
    method = await database.get_payment_method(method_id)
    if not method:
        return ConversationHandler.END

    context.user_data["editing_meth_id"] = method_id
    text = (
        f"✏️ <b>Edit Number / Details for {escape(method.get('name'))}</b>\n\n"
        f"Current: <code>{escape(method.get('details', 'N/A'))}</code>\n\n"
        f"👉 Please reply with the new Phone Number / Account Details (e.g. <code>017XXXXXXXX (Personal)</code>):"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data=f"adm_manage_meth_{method_id}")]])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return EDIT_METH_DETAILS

async def handle_edit_method_details_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_details = update.message.text.strip()
    method_id = context.user_data.get("editing_meth_id")
    if not method_id:
        return ConversationHandler.END

    method = await database.get_payment_method(method_id)
    if method:
        await database.update_payment_method(
            method_id=method_id,
            name=method["name"],
            details=new_details,
            instructions=method["instructions"],
            exchange_rate=method["exchange_rate"],
            min_deposit=method["min_deposit"]
        )

    await update.message.reply_text(
        f"✅ Account details updated to: <code>{escape(new_details)}</code>",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Manage Gateway", callback_data=f"adm_manage_meth_{method_id}")]])
    )
    context.user_data.pop("editing_meth_id", None)
    return ConversationHandler.END

async def start_edit_method_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return

    await query.answer()
    method_id = int(query.data.split("_")[3])
    method = await database.get_payment_method(method_id)
    if not method:
        return ConversationHandler.END

    context.user_data["editing_meth_id"] = method_id
    text = (
        f"💵 <b>Edit Exchange Rate for {escape(method.get('name'))}</b>\n\n"
        f"Current Rate: <code>1 USD = {method.get('exchange_rate', 125.0):.2f} BDT</code>\n\n"
        f"👉 Please reply with the new exchange rate in BDT per 1 USD (e.g. <code>125.00</code> or <code>130.00</code>):"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data=f"adm_manage_meth_{method_id}")]])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return EDIT_METH_RATE

async def handle_edit_method_rate_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text.strip()
    method_id = context.user_data.get("editing_meth_id")
    if not method_id:
        return ConversationHandler.END

    try:
        rate = float(raw_text)
        if rate <= 0:
            raise ValueError()

        method = await database.get_payment_method(method_id)
        if method:
            await database.update_payment_method(
                method_id=method_id,
                name=method["name"],
                details=method["details"],
                instructions=method["instructions"],
                exchange_rate=rate,
                min_deposit=method["min_deposit"]
            )

        await update.message.reply_text(
            f"✅ Exchange rate updated to: <code>1 USD = {rate:.2f} BDT</code>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Manage Gateway", callback_data=f"adm_manage_meth_{method_id}")]])
        )
        context.user_data.pop("editing_meth_id", None)
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("⚠️ Please enter a valid number (e.g. <code>125.00</code>):", parse_mode=ParseMode.HTML)
        return EDIT_METH_RATE

async def start_edit_method_inst(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not is_admin(query.from_user.id):
        return

    await query.answer()
    method_id = int(query.data.split("_")[3])
    method = await database.get_payment_method(method_id)
    if not method:
        return ConversationHandler.END

    context.user_data["editing_meth_id"] = method_id
    text = (
        f"📝 <b>Edit Instructions for {escape(method.get('name'))}</b>\n\n"
        f"Current: <i>{escape(method.get('instructions', 'N/A'))}</i>\n\n"
        f"👉 Please reply with the new deposit instructions for users:"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data=f"adm_manage_meth_{method_id}")]])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return EDIT_METH_INST

async def handle_edit_method_inst_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_inst = update.message.text.strip()
    method_id = context.user_data.get("editing_meth_id")
    if not method_id:
        return ConversationHandler.END

    method = await database.get_payment_method(method_id)
    if method:
        await database.update_payment_method(
            method_id=method_id,
            name=method["name"],
            details=method["details"],
            instructions=new_inst,
            exchange_rate=method["exchange_rate"],
            min_deposit=method["min_deposit"]
        )

    await update.message.reply_text(
        f"✅ Instructions updated successfully!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Manage Gateway", callback_data=f"adm_manage_meth_{method_id}")]])
    )
    context.user_data.pop("editing_meth_id", None)
    return ConversationHandler.END

