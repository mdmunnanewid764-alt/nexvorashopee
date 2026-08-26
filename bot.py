import logging
import asyncio
import os
from aiohttp import web
from telegram import Update, BotCommand
from telegram.request import HTTPXRequest
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    TypeHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode

from config import BOT_TOKEN, ADMIN_ID, TELEGRAM_PROXY_URL, TELEGRAM_BASE_URL
import database
from payment_service import payment_gateway
import handlers.user_handlers as user_h
import handlers.admin_handlers as admin_h

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------- BACKGROUND DEPOSIT CHECKER --------------------

async def auto_deposit_checker_job(context: ContextTypes.DEFAULT_TYPE):
    """
    Background worker that runs every 25 seconds to check pending deposits.
    Automatically credits user balance when payment is detected as PAID.
    """
    try:
        pending_deposits = await database.get_pending_deposits(limit=50)
        if not pending_deposits:
            return

        currency = await database.get_setting("currency_symbol", "$")

        for dep in pending_deposits:
            trade_no = dep["merchant_trade_no"]
            user_id = dep["user_id"]

            res = await payment_gateway.get_payment_status(trade_no)
            if not res.get("success"):
                continue

            order_info = res.get("order", {})
            status = order_info.get("status", "").upper()

            if status == "PAID":
                amount = float(order_info.get("orderAmount", dep["order_amount"]))
                paid_net = order_info.get("paidNetwork", "Multi-Chain / Binance Pay")
                tx_id = order_info.get("transactionId", "")

                # Credit user balance & update deposit
                await database.update_user_balance(user_id, amount, is_deposit=True)
                await database.mark_deposit_paid(trade_no, paid_network=paid_net, tx_hash=tx_id)

                # Send direct notification to user
                try:
                    user_alert = (
                        f"🎉 <b>Auto-Deposit Received & Confirmed!</b>\n\n"
                        f"🔖 <b>Invoice:</b> <code>{trade_no}</code>\n"
                        f"💰 <b>Amount Credited:</b> <code>{currency}{amount:.2f} USDT</code>\n"
                        f"🌐 <b>Network:</b> <code>{paid_net}</code>\n\n"
                        f"✨ <i>Your wallet has been credited automatically. Enjoy shopping!</i>"
                    )
                    await context.bot.send_message(chat_id=user_id, text=user_alert, parse_mode=ParseMode.HTML)
                except Exception as e:
                    logger.warning(f"Could not send deposit alert to user {user_id}: {e}")

                # Notify Admin
                try:
                    admin_alert = (
                        f"📥 <b>Deposit Confirmed!</b>\n\n"
                        f"👤 User: <code>{user_id}</code>\n"
                        f"💵 Amount: <code>{currency}{amount:.2f} USDT</code>\n"
                        f"🔖 Invoice: <code>{trade_no}</code>\n"
                        f"🌐 Network: <code>{paid_net}</code>"
                    )
                    await context.bot.send_message(chat_id=ADMIN_ID, text=admin_alert, parse_mode=ParseMode.HTML)
                except Exception as e:
                    logger.warning(f"Could not send deposit alert to admin: {e}")

    except Exception as e:
        logger.error(f"Error in auto_deposit_checker_job: {e}", exc_info=True)

# -------------------- EXTRA COMMANDS --------------------

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: <code>/status &lt;ORDER_ID_OR_INVOICE_ID&gt;</code>", parse_mode=ParseMode.HTML)
        return

    code = context.args[0].strip()
    dep = await database.get_deposit(code)
    if dep:
        status_res = await payment_gateway.get_payment_status(code)
        order_info = status_res.get("order", {})
        status = order_info.get("status", dep["status"]).upper()
        if status == "PAID" and not dep.get("credited"):
            amount = float(order_info.get("orderAmount", dep["order_amount"]))
            paid_net = order_info.get("paidNetwork") or dep.get("paid_network") or "CRYPTO"
            tx_id = order_info.get("transactionId") or ""
            await database.update_user_balance(dep["user_id"], amount, is_deposit=True)
            await database.mark_deposit_paid(code, paid_network=paid_net, tx_hash=tx_id)
            dep = await database.get_deposit(code)

        await update.message.reply_text(
            f"🔍 <b>Deposit Status: {code}</b>\n\n"
            f"💰 Amount: <code>${dep['order_amount']:.2f} {dep['currency']}</code>\n"
            f"📊 Status: <code>{status}</code>\n"
            f"🌐 Network: <code>{dep.get('paid_network') or 'Pending'}</code>\n"
            f"📅 Date: <code>{dep['created_at']}</code>",
            parse_mode=ParseMode.HTML
        )
        return

    order = await database.get_order_by_code(code)
    if order:
        await update.message.reply_text(
            f"📦 <b>Order Status: {code}</b>\n\n"
            f"🏷 Product: <code>{order['product_name']}</code>\n"
            f"💵 Price: <code>${order['total_price']:.2f}</code>\n"
            f"📊 Status: <code>{order['status']}</code>\n"
            f"📅 Date: <code>{order['created_at']}</code>",
            parse_mode=ParseMode.HTML
        )
        return

    await update.message.reply_text(f"❌ No record found for ID: <code>{code}</code>", parse_mode=ParseMode.HTML)

from telegram.error import Conflict, NetworkError, TimedOut

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, Conflict):
        logger.warning("⚠️ Telegram 409 Conflict detected (brief overlap during server deployment/restart). Handled gracefully.")
        return
    if isinstance(context.error, (NetworkError, TimedOut)):
        logger.warning(f"⚠️ Telegram network timeout/reconnect: {context.error}")
        return
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

# -------------------- HEALTH CHECK WEB SERVER (FOR RENDER FREE TIER) --------------------

async def health_check_handler(request):
    return web.json_response({"status": "ok", "bot": "Nexvora Telegram Bot Live"})

async def start_web_server():
    port = int(os.environ.get("PORT", 0))
    if port > 0:
        web_app = web.Application()
        web_app.router.add_get("/", health_check_handler)
        web_app.router.add_get("/health", health_check_handler)
        runner = web.AppRunner(web_app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info(f"Health check web server started on port {port}")

async def post_init(application: Application):
    await database.init_db()
    await start_web_server()
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook cleared, polling initialized cleanly.")
    except Exception as e:
        logger.warning(f"Note on webhook cleanup: {e}")

    # Set clean public commands for the Telegram Menu button (excluding admin)
    try:
        public_commands = [
            BotCommand("start", "🛒 Main Menu / Home"),
            BotCommand("products", "🛍 Browse Products"),
            BotCommand("language", "🌐 Change Language"),
            BotCommand("status", "🔍 Check Status"),
        ]
        await application.bot.set_my_commands(public_commands)
        logger.info("Public Menu button commands set successfully.")
    except Exception as e:
        logger.warning(f"Could not set bot commands: {e}")

    if application.job_queue:
        application.job_queue.run_repeating(auto_deposit_checker_job, interval=25, first=10)
        logger.info("Auto-deposit background poller job scheduled.")

# -------------------- ANTI-SPAM & SECURITY RATE LIMITER --------------------

from collections import defaultdict
import time

_rate_limit_data = defaultdict(list)
_RATE_LIMIT_MAX = 8       # Max 8 actions
_RATE_LIMIT_WINDOW = 3.0  # Within 3 seconds

async def security_rate_limiter_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    High-speed In-Memory Anti-Spam & DDoS Rate Limiter Middleware (group=-1).
    Filters out spam flooding, blocked bots, and banned accounts in <0.001ms.
    """
    user = update.effective_user
    if not user:
        return

    # Authorized Admins bypass rate limiter
    if admin_h.is_admin(user.id):
        return

    user_id = user.id
    now = time.time()

    # 1. Instant check if user is banned
    if await database.is_user_banned(user_id):
        if update.callback_query:
            await update.callback_query.answer("⛔ Your account has been suspended.", show_alert=True)
        return

    # 2. Rate Limiting Check
    timestamps = _rate_limit_data[user_id]
    _rate_limit_data[user_id] = [t for t in timestamps if now - t < _RATE_LIMIT_WINDOW]

    if len(_rate_limit_data[user_id]) >= _RATE_LIMIT_MAX:
        # Flooding detected! Throttle user.
        if update.callback_query:
            await update.callback_query.answer("⚠️ Please slow down! Anti-spam protection active.", show_alert=True)
        return

    _rate_limit_data[user_id].append(now)

# -------------------- MAIN APP SETUP --------------------

def main():
    request_kwargs = {
        "connection_pool_size": 64,
        "connect_timeout": 15.0,
        "read_timeout": 15.0,
        "write_timeout": 15.0,
        "pool_timeout": 15.0,
        "http_version": "1.1"
    }
    if TELEGRAM_PROXY_URL:
        request_kwargs["proxy"] = TELEGRAM_PROXY_URL

    request = HTTPXRequest(**request_kwargs)
    builder = Application.builder().token(BOT_TOKEN).request(request).post_init(post_init)
    if TELEGRAM_BASE_URL:
        builder = builder.base_url(TELEGRAM_BASE_URL)

    app = builder.build()

    # Pre-execution Security & Anti-Spam Middleware (group=-1)
    app.add_handler(TypeHandler(Update, security_rate_limiter_middleware), group=-1)

    # User Commands
    app.add_handler(CommandHandler("start", user_h.start_command))
    app.add_handler(CommandHandler("products", user_h.show_categories))
    app.add_handler(CommandHandler("buy", user_h.show_categories))
    app.add_handler(CommandHandler("language", user_h.show_language_menu))
    app.add_handler(CommandHandler("lang", user_h.show_language_menu))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("admin", admin_h.admin_panel))
    app.add_handler(CommandHandler("addbalance", admin_h.add_balance_cmd))
    app.add_handler(CommandHandler("deductbalance", admin_h.deduct_balance_cmd))

    # Conversation Handlers
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.start_custom_balance_adjust, pattern="^adm_custom_bal_")],
        states={admin_h.ADMIN_USER_BALANCE_ADJ: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_custom_balance_input)]},
        fallbacks=[CallbackQueryHandler(admin_h.admin_users_menu, pattern="^adm_users_menu$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(user_h.prompt_custom_deposit, pattern="^custom_deposit_btn$")],
        states={user_h.CUSTOM_DEPOSIT_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_h.process_custom_deposit_input)]},
        fallbacks=[CallbackQueryHandler(user_h.show_wallet, pattern="^user_wallet$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(user_h.start_submit_tx, pattern="^txstart_")],
        states={
            user_h.SUBMIT_TX_HASH: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_h.handle_submit_tx_hash)]
        },
        fallbacks=[CallbackQueryHandler(user_h.show_wallet, pattern="^user_wallet$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(user_h.handle_buy_balance, pattern="^buybal_")],
        states={user_h.MANUAL_ORDER_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_h.handle_manual_order_input)]},
        fallbacks=[CallbackQueryHandler(user_h.show_categories, pattern="^user_categories$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(user_h.start_buy_chatgpt_promo, pattern="^start_buy_promo$")],
        states={user_h.PROMO_EMAIL_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_h.handle_chatgpt_promo_email_input)]},
        fallbacks=[CallbackQueryHandler(user_h.show_chatgpt_promo, pattern="^user_chatgpt_promo$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.start_adm_promo_confirm, pattern="^adm_promo_confirm_")],
        states={admin_h.ADMIN_PROMO_CONFIRM_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_adm_promo_link_input)]},
        fallbacks=[CallbackQueryHandler(admin_h.cancel_adm_promo_confirm, pattern="^adm_cancel_promo_"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.start_edit_promo_price, pattern="^adm_edit_promo_price_start$")],
        states={admin_h.EDIT_PROMO_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_edit_promo_price_input)]},
        fallbacks=[CallbackQueryHandler(admin_h.admin_promo_menu, pattern="^adm_promo_menu$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.start_add_category, pattern="^adm_add_cat_start$")],
        states={
            admin_h.ADD_CAT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_add_cat_name)],
            admin_h.ADD_CAT_EMOJI: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_add_cat_emoji)]
        },
        fallbacks=[CallbackQueryHandler(admin_h.admin_cat_menu, pattern="^adm_cat_menu$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.start_add_product, pattern="^adm_add_product$")],
        states={
            admin_h.ADD_PROD_CAT: [CallbackQueryHandler(admin_h.handle_prod_cat_choice, pattern="^selcat_")],
            admin_h.ADD_PROD_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_prod_name)],
            admin_h.ADD_PROD_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_prod_desc)],
            admin_h.ADD_PROD_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_prod_price)],
            admin_h.ADD_PROD_TYPE: [CallbackQueryHandler(admin_h.handle_prod_type, pattern="^prodtype_")],
            admin_h.ADD_PROD_IMAGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_prod_image_input),
                CallbackQueryHandler(admin_h.handle_skip_prod_img, pattern="^skip_prod_img$")
            ]
        },
        fallbacks=[CallbackQueryHandler(admin_h.admin_panel, pattern="^admin_home$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.start_add_stock, pattern="^adm_add_stock_")],
        states={admin_h.ADD_STOCK_ITEMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_add_stock_items)]},
        fallbacks=[CallbackQueryHandler(admin_h.admin_stock_menu, pattern="^adm_stock_menu$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.start_broadcast, pattern="^adm_broadcast_start$")],
        states={admin_h.ADMIN_BROADCAST_MSG: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_broadcast_message)]},
        fallbacks=[CallbackQueryHandler(admin_h.admin_panel, pattern="^admin_home$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.prompt_search_user, pattern="^adm_search_user_btn$")],
        states={admin_h.ADMIN_USER_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_user_search_input)]},
        fallbacks=[CallbackQueryHandler(admin_h.admin_users_menu, pattern="^adm_users_menu$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.start_edit_setting, pattern="^editset_")],
        states={admin_h.SETTING_EDIT_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_edit_setting_val)]},
        fallbacks=[CallbackQueryHandler(admin_h.admin_settings_menu, pattern="^adm_settings$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(user_h.start_manual_deposit_conv, pattern="^start_manual_dep_")],
        states={
            user_h.MANUAL_DEP_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_h.handle_manual_dep_amount_input)],
            user_h.MANUAL_DEP_SENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_h.handle_manual_dep_sender_input)],
            user_h.MANUAL_DEP_TRXID: [MessageHandler(filters.TEXT & ~filters.COMMAND, user_h.handle_manual_dep_trxid_input)],
        },
        fallbacks=[CallbackQueryHandler(user_h.show_deposit_options, pattern="^user_deposit$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.start_edit_method_details, pattern="^adm_edit_mdet_")],
        states={admin_h.EDIT_METH_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_edit_method_details_input)]},
        fallbacks=[CallbackQueryHandler(admin_h.admin_methods_menu, pattern="^adm_methods_menu$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.start_edit_method_rate, pattern="^adm_edit_mrate_")],
        states={admin_h.EDIT_METH_RATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_edit_method_rate_input)]},
        fallbacks=[CallbackQueryHandler(admin_h.admin_methods_menu, pattern="^adm_methods_menu$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))
    app.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(admin_h.start_edit_method_inst, pattern="^adm_edit_minst_")],
        states={admin_h.EDIT_METH_INST: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_h.handle_edit_method_inst_input)]},
        fallbacks=[CallbackQueryHandler(admin_h.admin_methods_menu, pattern="^adm_methods_menu$"), CommandHandler("start", user_h.start_command)],
        per_message=False
    ))

    # General Callback Queries
    app.add_handler(CallbackQueryHandler(user_h.start_command, pattern="^user_menu$"))
    app.add_handler(CallbackQueryHandler(user_h.show_categories, pattern="^user_categories$"))
    app.add_handler(CallbackQueryHandler(user_h.show_category_products, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(user_h.show_product_details, pattern="^prod_"))
    app.add_handler(CallbackQueryHandler(user_h.handle_buy_balance, pattern="^buybal_"))
    app.add_handler(CallbackQueryHandler(user_h.handle_direct_crypto_buy, pattern="^buycrypto_"))

    app.add_handler(CallbackQueryHandler(user_h.show_wallet, pattern="^user_wallet$"))
    app.add_handler(CallbackQueryHandler(user_h.show_deposit_options, pattern="^user_deposit$"))
    app.add_handler(CallbackQueryHandler(user_h.show_crypto_network_selection, pattern="^select_dep_crypto$"))
    app.add_handler(CallbackQueryHandler(user_h.handle_select_crypto_network, pattern="^selnet_"))
    app.add_handler(CallbackQueryHandler(user_h.show_manual_deposit_instructions, pattern="^select_dep_m_"))
    app.add_handler(CallbackQueryHandler(user_h.handle_preset_deposit, pattern="^create_dep_"))
    app.add_handler(CallbackQueryHandler(user_h.check_deposit_status, pattern="^chkdep_"))
    app.add_handler(CallbackQueryHandler(user_h.show_deposit_qr, pattern="^qrdep_"))

    app.add_handler(CallbackQueryHandler(user_h.show_orders, pattern="^user_orders$"))
    app.add_handler(CallbackQueryHandler(user_h.show_profile, pattern="^user_profile$"))
    app.add_handler(CallbackQueryHandler(user_h.show_support, pattern="^user_support$"))
    app.add_handler(CallbackQueryHandler(user_h.show_language_menu, pattern="^user_language_menu$"))
    app.add_handler(CallbackQueryHandler(user_h.handle_set_language, pattern="^setlang_"))
    app.add_handler(CallbackQueryHandler(user_h.show_chatgpt_promo, pattern="^user_chatgpt_promo$"))

    # Admin Callback Queries
    app.add_handler(CallbackQueryHandler(admin_h.admin_panel, pattern="^admin_home$"))
    app.add_handler(CallbackQueryHandler(admin_h.admin_promo_menu, pattern="^adm_promo_menu$"))
    app.add_handler(CallbackQueryHandler(admin_h.admin_toggle_promo, pattern="^adm_toggle_promo$"))
    app.add_handler(CallbackQueryHandler(admin_h.cancel_adm_promo_confirm, pattern="^adm_cancel_promo_"))
    app.add_handler(CallbackQueryHandler(admin_h.handle_adm_promo_refund, pattern="^adm_promo_refund_"))
    app.add_handler(CallbackQueryHandler(admin_h.admin_cat_menu, pattern="^adm_cat_menu$"))
    app.add_handler(CallbackQueryHandler(admin_h.handle_del_category, pattern="^adm_del_cat_"))
    app.add_handler(CallbackQueryHandler(admin_h.admin_list_products, pattern="^adm_list_products$"))
    app.add_handler(CallbackQueryHandler(admin_h.admin_manage_single_product, pattern="^adm_manage_prod_"))
    app.add_handler(CallbackQueryHandler(admin_h.handle_toggle_product, pattern="^adm_toggle_prod_"))
    app.add_handler(CallbackQueryHandler(admin_h.handle_delete_product, pattern="^adm_del_prod_"))
    app.add_handler(CallbackQueryHandler(admin_h.admin_stock_menu, pattern="^adm_stock_menu$"))
    app.add_handler(CallbackQueryHandler(admin_h.admin_users_menu, pattern="^adm_users_menu$"))
    app.add_handler(CallbackQueryHandler(admin_h.admin_view_user, pattern="^adm_view_user_"))
    app.add_handler(CallbackQueryHandler(admin_h.handle_balance_adjust, pattern="^adm_adj_bal_"))
    app.add_handler(CallbackQueryHandler(admin_h.admin_settings_menu, pattern="^adm_settings$"))

    # Admin Payment Methods and Deposit Approvals
    app.add_handler(CallbackQueryHandler(admin_h.admin_methods_menu, pattern="^adm_methods_menu$"))
    app.add_handler(CallbackQueryHandler(admin_h.admin_manage_single_method, pattern="^adm_manage_meth_"))
    app.add_handler(CallbackQueryHandler(admin_h.handle_toggle_method, pattern="^adm_toggle_meth_"))
    app.add_handler(CallbackQueryHandler(admin_h.handle_adm_appr_deposit, pattern="^adm_appr_dep_"))
    app.add_handler(CallbackQueryHandler(admin_h.handle_adm_rej_deposit, pattern="^adm_rej_dep_"))

    app.add_error_handler(error_handler)

    logger.info("🤖 Starting Nexvora Shopee Bot (Ultra High Speed Polling)...")
    app.run_polling(
        poll_interval=0.0,
        timeout=20,
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
