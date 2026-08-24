import logging
import asyncio
import html
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
import database
from config import ADMIN_ID

logger = logging.getLogger(__name__)

# Admin Conversation States
(
    ADD_CAT_NAME, ADD_CAT_EMOJI,
    ADD_PROD_CAT, ADD_PROD_NAME, ADD_PROD_DESC, ADD_PROD_PRICE, ADD_PROD_TYPE, ADD_PROD_IMAGE,
    ADD_STOCK_PROD, ADD_STOCK_ITEMS,
    EDIT_PROD_PRICE, EDIT_PROD_DESC,
    ADMIN_USER_SEARCH, ADMIN_USER_BALANCE_ADJ,
    ADMIN_BROADCAST_MSG,
    SETTING_EDIT_KEY
) = range(16)

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

    text = (
        f"🛠 <b>Nexvora Admin Control Panel</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Total Users:</b> <code>{stats['total_users']}</code>\n"
        f"🛍 <b>Total Active Products:</b> <code>{stats['total_products']}</code>\n"
        f"🔑 <b>Total Available Stock:</b> <code>{stats['total_stock']}</code> items\n"
        f"📦 <b>Total Orders:</b> <code>{stats['total_orders']}</code> (<code>{currency}{stats['total_sales']:.2f}</code>)\n"
        f"📥 <b>Total Paid Deposits:</b> <code>{stats['total_deposits']}</code> (<code>{currency}{stats['total_deposited_amount']:.2f}</code>)\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <i>Select an administrative action:</i>"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add Product", callback_data="adm_add_product"),
            InlineKeyboardButton("📦 Manage Products", callback_data="adm_list_products")
        ],
        [
            InlineKeyboardButton("🔑 Add / Manage Stock", callback_data="adm_stock_menu"),
            InlineKeyboardButton("📂 Manage Categories", callback_data="adm_cat_menu")
        ],
        [
            InlineKeyboardButton("👥 Manage Users", callback_data="adm_users_menu"),
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
        "📝 <b>Add Category (Step 1/2)</b>\n\nPlease enter the Category Name (e.g. <code>VPN Accounts</code>, <code>Gift Cards</code>, <code>Software</code>):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_cat_menu")]]),
        parse_mode=ParseMode.HTML
    )
    return ADD_CAT_NAME

async def handle_add_cat_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["new_cat_name"] = update.message.text.strip()
    await update.message.reply_text(
        "🎨 <b>Add Category (Step 2/2)</b>\n\nPlease enter an emoji for this category (e.g. 🔒, 🎁, 💻) or send <code>-</code> for default:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_cat_menu")]]),
        parse_mode=ParseMode.HTML
    )
    return ADD_CAT_EMOJI

async def handle_add_cat_emoji(update: Update, context: ContextTypes.DEFAULT_TYPE):
    emoji_input = update.message.text.strip()
    emoji = "📁" if emoji_input == "-" else emoji_input
    name = context.user_data.get("new_cat_name", "General")

    cat_id = await database.add_category(name, emoji)
    context.user_data.pop("new_cat_name", None)

    await update.message.reply_text(
        f"✅ Category <b>{emoji} {escape(name)}</b> created successfully (ID: <code>{cat_id}</code>)!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📂 Category Menu", callback_data="adm_cat_menu")]])
    )
    return ConversationHandler.END

async def handle_del_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cat_id = int(query.data.split("_")[3])
    await query.answer()

    await database.delete_category(cat_id)
    await query.edit_message_text("✅ Category deleted.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="adm_cat_menu")]]))

# -------------------- PRODUCT CREATION WIZARD --------------------

async def start_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    categories = await database.get_categories()
    if not categories:
        await query.edit_message_text(
            "⚠️ Please create at least one category before adding products!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("➕ Add Category", callback_data="adm_add_cat_start")]])
        )
        return ConversationHandler.END

    buttons = []
    for cat in categories:
        buttons.append([InlineKeyboardButton(f"{cat.get('emoji', '📁')} {cat['name']}", callback_data=f"selcat_{cat['id']}")])
    buttons.append([InlineKeyboardButton("❌ Cancel", callback_data="admin_home")])

    await query.edit_message_text(
        "📦 <b>Add Product (Step 1/6)</b>\n\nSelect category for this product:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )
    return ADD_PROD_CAT

async def handle_prod_cat_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    cat_id = int(query.data.split("_")[1])
    await query.answer()

    context.user_data["add_prod_cat_id"] = cat_id
    await query.edit_message_text(
        "📝 <b>Add Product (Step 2/6)</b>\n\nEnter Product Title / Name (e.g. <code>Netflix Premium 1-Month</code>):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_home")]]),
        parse_mode=ParseMode.HTML
    )
    return ADD_PROD_NAME

async def handle_prod_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_prod_name"] = update.message.text.strip()
    await update.message.reply_text(
        "📄 <b>Add Product (Step 3/6)</b>\n\nEnter Product Description (features, terms, warranty):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_home")]]),
        parse_mode=ParseMode.HTML
    )
    return ADD_PROD_DESC

async def handle_prod_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["add_prod_desc"] = update.message.text.strip()
    currency = await database.get_setting("currency_symbol", "$")
    await update.message.reply_text(
        f"💵 <b>Add Product (Step 4/6)</b>\n\nEnter Price in {currency} (e.g. <code>9.99</code> or <code>25</code>):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="admin_home")]]),
        parse_mode=ParseMode.HTML
    )
    return ADD_PROD_PRICE

async def handle_prod_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.replace("$", "").strip()
    try:
        price = float(text)
        context.user_data["add_prod_price"] = price
    except ValueError:
        await update.message.reply_text("⚠️ Invalid price. Please enter a valid number (e.g. 15.00):")
        return ADD_PROD_PRICE

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Digital Auto-Stock (Keys / Accounts)", callback_data="prodtype_digital")],
        [InlineKeyboardButton("🛠 Manual Service / Custom Delivery", callback_data="prodtype_manual")],
        [InlineKeyboardButton("❌ Cancel", callback_data="admin_home")]
    ])
    await update.message.reply_text(
        "⚙️ <b>Add Product (Step 5/6)</b>\n\nSelect Delivery Type:\n\n"
        "• <b>Digital Auto-Stock:</b> Bot instantly delivers credentials/keys from stock.\n"
        "• <b>Manual Service:</b> Customer submits info, Admin manually fulfills.",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )
    return ADD_PROD_TYPE

async def handle_prod_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    del_type = query.data.split("_")[1]
    await query.answer()

    context.user_data["add_prod_type"] = del_type
    await query.edit_message_text(
        "🖼 <b>Add Product (Step 6/6)</b>\n\nSend a direct Image URL (e.g. <code>https://example.com/photo.png</code>) or send <code>-</code> to skip:",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⏭ Skip Image", callback_data="skip_prod_img")]]),
        parse_mode=ParseMode.HTML
    )
    return ADD_PROD_IMAGE

async def handle_prod_image_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    img_url = update.message.text.strip()
    if img_url == "-":
        img_url = None
    return await finalize_product_creation(update, context, img_url)

async def handle_skip_prod_img(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    return await finalize_product_creation(update, context, None, is_callback=True)

async def finalize_product_creation(update: Update, context: ContextTypes.DEFAULT_TYPE, img_url: str = None, is_callback: bool = False):
    cat_id = context.user_data.get("add_prod_cat_id")
    name = context.user_data.get("add_prod_name")
    desc = context.user_data.get("add_prod_desc")
    price = context.user_data.get("add_prod_price")
    del_type = context.user_data.get("add_prod_type", "digital")

    prod_id = await database.add_product(
        category_id=cat_id,
        name=name,
        description=desc,
        price=price,
        image_url=img_url,
        delivery_type=del_type
    )

    for k in ["add_prod_cat_id", "add_prod_name", "add_prod_desc", "add_prod_price", "add_prod_type"]:
        context.user_data.pop(k, None)

    currency = await database.get_setting("currency_symbol", "$")
    text = (
        f"✅ <b>Product Added Successfully!</b>\n\n"
        f"🏷 <b>Name:</b> <code>{escape(name)}</code> (ID: <code>{prod_id}</code>)\n"
        f"💵 <b>Price:</b> <code>{currency}{price:.2f}</code>\n"
        f"⚙️ <b>Type:</b> <code>{del_type.capitalize()}</code>\n\n"
        f"👉 <i>If this is a digital product, don't forget to add digital stock items!</i>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Add Stock Now", callback_data=f"adm_add_stock_{prod_id}")],
        [InlineKeyboardButton("📦 Product List", callback_data="adm_list_products"), InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_home")]
    ])

    if is_callback:
        await update.callback_query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

    return ConversationHandler.END

# -------------------- PRODUCT & STOCK MANAGEMENT --------------------

async def admin_list_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    products = await database.get_all_products(limit=50)
    currency = await database.get_setting("currency_symbol", "$")

    if not products:
        text = "📦 <b>Product Management</b>\n\n⚠️ No products created yet."
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("➕ Add Product", callback_data="adm_add_product")],
            [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")]
        ])
        await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return

    text = "📦 <b>Product Management</b>\n\nSelect a product to view options, edit price, or manage stock:"
    buttons = []
    for p in products:
        stock_count = await database.get_available_stock_count(p["id"]) if p["delivery_type"] == "digital" else "Manual"
        buttons.append([InlineKeyboardButton(f"{p['name']} - {currency}{p['price']:.2f} (Stock: {stock_count})", callback_data=f"adm_manage_p_{p['id']}")])

    buttons.append([InlineKeyboardButton("➕ Add New Product", callback_data="adm_add_product")])
    buttons.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")])

    keyboard = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def admin_view_product_ops(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    prod_id = int(query.data.split("_")[3])
    await query.answer()

    p = await database.get_product(prod_id)
    if not p:
        await query.edit_message_text("Product not found.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="adm_list_products")]]))
        return

    currency = await database.get_setting("currency_symbol", "$")
    stock_count = await database.get_available_stock_count(p["id"]) if p["delivery_type"] == "digital" else "N/A (Manual)"

    text = (
        f"📦 <b>Product Management:</b> <code>{escape(p['name'])}</code>\n\n"
        f"🆔 ID: <code>{p['id']}</code>\n"
        f"📂 Category: <code>{escape(p.get('category_name', 'None'))}</code>\n"
        f"💵 Price: <code>{currency}{p['price']:.2f}</code>\n"
        f"⚙️ Type: <code>{p['delivery_type']}</code>\n"
        f"📦 Current Stock: <code>{stock_count}</code>\n\n"
        f"📝 Description:\n<code>{escape(p.get('description') or 'None')}</code>"
    )

    buttons = [
        [InlineKeyboardButton("🔑 Add Stock Items", callback_data=f"adm_add_stock_{p['id']}")],
        [InlineKeyboardButton("🗑 Delete Product", callback_data=f"adm_del_prod_{p['id']}")],
        [InlineKeyboardButton("🔙 Back to Products", callback_data="adm_list_products")]
    ]

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=ParseMode.HTML)

async def admin_delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    prod_id = int(query.data.split("_")[3])
    await query.answer()

    await database.delete_product(prod_id)
    await query.edit_message_text("✅ Product deleted successfully.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Product List", callback_data="adm_list_products")]]))

# -------------------- BULK STOCK UPLOAD --------------------

async def admin_stock_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    products = await database.get_all_products(limit=50)
    digital_products = [p for p in products if p["delivery_type"] == "digital"]

    if not digital_products:
        await query.edit_message_text(
            "⚠️ No digital products found. Please add a product with 'Digital Auto-Stock' type first.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Admin Panel", callback_data="admin_home")]])
        )
        return

    buttons = []
    for p in digital_products:
        count = await database.get_available_stock_count(p["id"])
        buttons.append([InlineKeyboardButton(f"🔑 {p['name']} (Stock: {count})", callback_data=f"adm_add_stock_{p['id']}")])
    buttons.append([InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")])

    await query.edit_message_text(
        "🔑 <b>Stock Management</b>\n\nSelect a product to add / restock digital goods (Accounts, Keys, Codes):",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )

async def start_add_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    prod_id = int(query.data.split("_")[3])
    await query.answer()

    context.user_data["stock_target_prod_id"] = prod_id
    p = await database.get_product(prod_id)
    count = await database.get_available_stock_count(prod_id)

    text = (
        f"🔑 <b>Upload Digital Stock for: <code>{escape(p['name'])}</code></b>\n\n"
        f"Current Stock: <code>{count}</code> items\n\n"
        f"Please send the stock items.\n"
        f"💡 <b>Bulk Upload Supported:</b> You can send multiple accounts/keys separated by new lines.\n\n"
        f"<i>(Example:</i>\n<code>user1:pass1</code>\n<code>user2:pass2</code>\n<code>KEY-1234-5678</code><i>)</i>"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_stock_menu")]])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    return ADD_STOCK_ITEMS

async def handle_add_stock_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    prod_id = context.user_data.get("stock_target_prod_id")

    if not prod_id:
        await update.message.reply_text("Session expired. Please try again.")
        return ConversationHandler.END

    items = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not items:
        await update.message.reply_text("⚠️ No valid items detected. Please send at least one line with item data:")
        return ADD_STOCK_ITEMS

    added_count = await database.add_product_stock_bulk(prod_id, items)
    total_count = await database.get_available_stock_count(prod_id)

    await update.message.reply_text(
        f"✅ <b>Stock Updated!</b>\n\n"
        f"➕ Successfully added <code>{added_count}</code> items.\n"
        f"📦 <b>Total Available Stock:</b> <code>{total_count}</code> items.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔑 Add More Stock", callback_data=f"adm_add_stock_{prod_id}")],
            [InlineKeyboardButton("📦 Product List", callback_data="adm_list_products"), InlineKeyboardButton("🛠 Admin Panel", callback_data="admin_home")]
        ]),
        parse_mode=ParseMode.HTML
    )
    context.user_data.pop("stock_target_prod_id", None)
    return ConversationHandler.END

# -------------------- USER BALANCE MANAGEMENT --------------------

async def admin_users_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    total_users = await database.get_total_users_count()
    text = (
        f"👥 <b>User Management</b>\n\n"
        f"Total Registered Users: <code>{total_users}</code>\n\n"
        f"Send user Telegram ID to search profile and adjust balance."
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔍 Search User by ID", callback_data="adm_search_user_btn")],
        [InlineKeyboardButton("🔙 Back to Admin", callback_data="admin_home")]
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

async def prompt_search_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🔍 <b>Search User</b>\n\nPlease reply with the User's Telegram ID (e.g. <code>6575066703</code>):",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="adm_users_menu")]]),
        parse_mode=ParseMode.HTML
    )
    return ADMIN_USER_SEARCH

async def handle_user_search_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    try:
        target_id = int(text)
        user = await database.get_user(target_id)
        if not user:
            await update.message.reply_text("❌ User not found in database. Make sure they have interacted with the bot at least once.")
            return ConversationHandler.END

        context.user_data["target_user_id"] = target_id
        currency = await database.get_setting("currency_symbol", "$")

        info_text = (
            f"👤 <b>User Profile: {escape(user.get('first_name', 'N/A'))}</b>\n\n"
            f"🆔 Telegram ID: <code>{user['telegram_id']}</code>\n"
            f"🏷 Username: @{escape(user.get('username', 'N/A'))}\n"
            f"💰 Balance: <code>{currency}{user['balance']:.2f}</code>\n"
            f"📥 Total Deposited: <code>{currency}{user['total_deposited']:.2f}</code>\n"
            f"🛒 Total Spent: <code>{currency}{user['total_spent']:.2f}</code>\n"
        )
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back", callback_data="adm_users_menu")]
        ])
        await update.message.reply_text(info_text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("⚠️ Please enter a numeric Telegram ID:")
        return ADMIN_USER_SEARCH

# -------------------- BROADCAST ANNOUNCEMENT --------------------

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
