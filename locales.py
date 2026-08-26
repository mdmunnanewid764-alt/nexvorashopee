# Multilingual Localization Strings (English, Bengali/Bangladesh, Urdu/Pakistan, Persian/Iran, Arabic/Palestine)

LANGUAGES = {
    "en": {"name": "English", "flag": "🇬🇧"},
    "bn": {"name": "বাংলা (Bangladesh)", "flag": "🇧🇩"},
    "ur": {"name": "اردو (Pakistan)", "flag": "🇵🇰"},
    "fa": {"name": "فارسی (Iran)", "flag": "🇮🇷"},
    "ar": {"name": "العربية (Palestine)", "flag": "🇵🇸"}
}

STRINGS = {
    "en": {
        # Main Menu
        "welcome_title": "Welcome to Nexvora Shop, {name}!",
        "welcome_sub": "Your premier automated marketplace for premium digital goods, subscriptions, and instant services.",
        "balance": "Your Balance",
        "user_id": "Your User ID",
        "choose_option": "Choose an option below to get started:",
        "btn_shop": "🛍 Shop / Products",
        "btn_wallet": "💳 My Wallet",
        "btn_orders": "📦 My Orders",
        "btn_profile": "👤 My Profile",
        "btn_support": "💬 Support & Help",
        "btn_language": "🌐 Language",
        "btn_admin": "🛠 Admin Control Panel",
        "btn_back_main": "🔙 Back to Main Menu",
        "btn_back": "🔙 Back",
        
        # Promo Offer
        "btn_chatgpt_promo": "🔥 ChatGPT 3-Month Promo ({symbol}{price:.2f})",
        "chatgpt_promo_title": "🤖 <b>ChatGPT 3-Month Subscription Promo Offer</b>",
        "chatgpt_promo_desc": "Get a special 3-Month ChatGPT Subscription activated directly on your personal Gmail / Email address.",
        "chatgpt_promo_disabled": "⚠️ The ChatGPT 3-Month Promo offer is currently unavailable. Please check back later!",
        "chatgpt_promo_ask_email": "🤖 <b>ChatGPT 3-Month Promo Offer Activation</b>\n\n💵 Price: <code>{symbol}{price:.2f}</code>\n\n📧 <b>Please reply with your Gmail / Email address:</b>\n<i>(We will activate the 3-month subscription on this email)</i>",
        "chatgpt_promo_invalid_email": "❌ <b>Invalid Email Address!</b>\n\n⚠️ Please enter a valid Gmail / Email address (e.g. <code>example@gmail.com</code>):",
        "chatgpt_promo_order_submitted": "✅ <b>ChatGPT Promo Order Submitted!</b>\n\n📦 <b>Offer:</b> <code>ChatGPT 3-Month Promo</code>\n🔖 <b>Order Code:</b> <code>{code}</code>\n📧 <b>Target Gmail/Email:</b> <code>{email}</code>\n💰 <b>Paid:</b> <code>{symbol}{price:.2f}</code>\n\n⏳ <i>Our admin team is processing your activation on your email. You will receive an instant notification once activated (or automatic refund if cancelled).</i>",
        "chatgpt_promo_activated_user": "🎉 <b>ChatGPT 3-Month Subscription Activated!</b>\n\n🔖 <b>Order:</b> <code>{code}</code>\n📧 <b>Target Email:</b> <code>{email}</code>\n\n🎁 <b>Your Promo Code / Activation Link:</b>\n<code>{link}</code>\n\n✨ <i>Your ChatGPT 3-Month subscription has been successfully activated by Admin! Enjoy your service.</i>",
        "chatgpt_promo_refunded_user": "❌ <b>ChatGPT Promo Order Cancelled & Refunded</b>\n\n🔖 <b>Order:</b> <code>{code}</code>\n💰 <b>Refunded Amount:</b> <code>{symbol}{price:.2f}</code>\n\n💡 <i>The full amount has been refunded back to your wallet balance.</i>",

        # Shop / Catalog
        "catalog_title": "Store Catalog - Categories",
        "catalog_empty": "⚠️ No categories available at the moment. Please check back soon!",
        "select_cat": "Select a category to browse products:",
        "category_empty": "⚠️ No products available in this category.",
        "select_product": "Select a product to view details & buy:",
        "in_stock": "In Stock",
        "out_of_stock": "Out of Stock",
        "instant_service": "Instant Service",
        "available_request": "Available on Request",
        "instant_delivery_info": "⚡ <b>Instant Digital Delivery</b> <i>(Item/Key will be delivered directly in chat immediately after purchase)</i>",
        "manual_delivery_info": "🛠 <b>Manual Service / Order</b> <i>(Admin will fulfill upon order)</i>",
        "price": "Price",
        "product_label": "Product",
        "category_label": "Category",
        "description_label": "Description",
        "btn_buy_balance": "💳 Buy with Balance ({symbol}{price:.2f})",
        "btn_buy_crypto": "🪙 Direct Crypto Invoice ({symbol}{price:.2f})",
        "btn_back_products": "🔙 Back to Products",
        "btn_back_categories": "🔙 Back to Categories",
        
        # Purchase
        "insufficient_balance": "❌ <b>Insufficient Balance</b>\n\nRequired: <code>{symbol}{price:.2f}</code>\nYour Balance: <code>{symbol}{balance:.2f}</code>\nYou need <code>{symbol}{shortage:.2f}</code> more.\n\n👇 Click below to deposit funds via Crypto, bKash, or Nagad!",
        "btn_deposit_now": "📥 Deposit Balance Now",
        "purchase_success": "🎉 <b>Purchase Successful!</b>\n\n📦 <b>Product:</b> <code>{name}</code>\n🔖 <b>Order Code:</b> <code>{code}</code>\n💰 <b>Amount Paid:</b> <code>{symbol}{price:.2f}</code>\n\n🔑 <b>Delivered Item / Code / Access:</b>\n<pre>{item}</pre>\n\n💡 <i>You can also view this anytime in 'My Orders'.</i>",
        "btn_continue_shopping": "🛍 Continue Shopping",
        "manual_prompt": "📝 <b>Manual Service Order: {name}</b>\n\nPrice: <code>{symbol}{price:.2f}</code>\n\nPlease enter any required details for your order (e.g. Email, Username, or specifications) to complete purchase:",
        "manual_submitted": "✅ <b>Order Submitted Successfully!</b>\n\n📦 <b>Product:</b> <code>{name}</code>\n🔖 <b>Order Code:</b> <code>{code}</code>\n💰 <b>Amount Paid:</b> <code>{symbol}{price:.2f}</code>\n📝 <b>Your Details:</b>\n<code>{details}</code>\n\n⏳ <i>Our team has received your order and is processing it. You will be updated here once fulfilled.</i>",

        # Wallet & Deposit Gateways
        "wallet_title": "💳 <b>My Wallet & Balance</b>\n\n💰 <b>Current Balance:</b> <code>{symbol}{balance:.2f} {currency}</code>\n📥 <b>Total Deposited:</b> <code>{symbol}{deposited:.2f}</code>\n🛒 <b>Total Spent:</b> <code>{symbol}{spent:.2f}</code>\n\n⚡ <i>Fast deposit options: Crypto (Auto Verify), bKash, Nagad, and local gateways.</i>",
        "btn_deposit": "📥 Deposit Balance",
        "deposit_select_method": "📥 <b>Select Payment / Deposit Method</b>\n\nChoose your preferred payment method below to add funds to your wallet:",
        "btn_crypto_gateway": "🪙 USDT / Crypto (Auto Instant)",
        "deposit_menu": "📥 <b>Crypto Deposit (USDT Multi-Chain)</b>\n\n🪙 <b>Supported Networks:</b>\n• <b>USDT - BEP20</b> (BNB Smart Chain)\n• <b>USDT - TRC20</b> (TRON Network)\n• <b>USDT - ERC20</b> (Ethereum)\n\n📌 <i>Minimum deposit:</i> <code>{symbol}{min_dep:.2f}</code>\n\nSelect a preset amount or enter custom:",
        "btn_custom_amount": "✏️ Custom Amount",
        "custom_amount_prompt": "✏️ <b>Enter Custom Deposit Amount</b>\n\nPlease reply with the exact amount in USDT (minimum <code>{symbol}{min_dep:.2f}</code>):\n<i>(Example: <code>15</code> or <code>35.50</code>)</i>",
        "invalid_amount_min": "❌ <b>Invalid Amount!</b>\n\n⚠️ You entered <code>{symbol}{amount:.2f}</code>, but minimum deposit is <code>{symbol}{min_dep:.2f}</code>.\n\n👉 Please enter <code>{min_dep:.2f}</code> or more (e.g. <code>10</code> or <code>25.50</code>):",
        "invalid_amount_number": "❌ <b>Invalid Input!</b>\n\n⚠️ Letters or special symbols are not allowed.\n👉 Please enter a valid number only (e.g. <code>10</code>, <code>20</code> or <code>50</code>):",
        
        # Crypto Invoice
        "invoice_title": "🪙 <b>Payment Invoice Generated</b>\n\n🔖 <b>Invoice ID:</b> <code>{code}</code>\n💵 <b>Amount:</b> <code>{symbol}{amount:.2f} USDT</code>\n⏳ <b>Status:</b> <code>Awaiting Payment (INITIAL)</code>\n\n━━━━━━━━━━━━━━━━━━━━\n🌐 <b>Multi-Chain USDT Transfer Addresses:</b>\nSend exact <code>{amount:.2f} USDT</code> to any address below:\n\n🟡 <b>BEP20 (BNB Smart Chain):</b>\n<code>{bep20}</code>\n\n🔴 <b>TRC20 (TRON Network):</b>\n<code>{trc20}</code>\n\n🔵 <b>ERC20 (Ethereum):</b>\n<code>{erc20}</code>\n━━━━━━━━━━━━━━━━━━━━\n💡 <i>After transferring, click 'Check Payment Status' or submit your TxHash for instant confirmation!</i>",
        "btn_check_status": "🔄 Check Payment Status",
        "btn_submit_tx": "⚡ Submit TxHash",
        "deposit_confirmed": "🎉 <b>Deposit Confirmed & Credited!</b>\n\n🔖 <b>Invoice ID:</b> <code>{code}</code>\n💰 <b>Amount Credited:</b> <code>{symbol}{amount:.2f} USDT</code>\n🌐 <b>Network:</b> <code>{network}</code>\n\n✨ <i>Your wallet balance has been updated. Happy shopping!</i>",
        "deposit_already_credited": "✅ This deposit is already verified and credited to your wallet!",
        "deposit_pending": "⏳ Payment not detected yet on blockchain. If you just transferred, please allow 1-2 minutes for network confirmations.",
        
        # Manual Deposit Flow (bKash / Nagad / Local)
        "manual_dep_info": "📱 <b>{name} Deposit Instructions</b>\n\n📌 <b>Account Details:</b>\n<code>{details}</code> <i>(Tap to copy)</i>\n\n📝 <b>Instructions:</b> {instructions}\n💵 <b>Exchange Rate:</b> <code>$1.00 = {rate:.2f} BDT</code>\n📌 <b>Minimum Deposit:</b> <code>{symbol}{min_dep:.2f} ({min_bdt:.2f} BDT)</code>\n\n👉 <i>After sending money, click the button below to submit your payment details for instant Admin verification:</i>",
        "btn_submit_manual_dep": "📝 Submit Payment Details",
        "manual_dep_ask_amount": "💵 <b>Enter Deposit Amount:</b>\n\nExchange Rate: <code>$1.00 = {rate:.2f} BDT</code>\n\nPlease reply with the amount in <b>USD</b> (e.g. <code>10</code>) or in <b>BDT</b> (e.g. <code>1250</code>):\n<i>(Minimum: {symbol}{min_dep:.2f})</i>",
        "manual_dep_ask_sender": "📱 <b>Enter Sender Phone Number:</b>\n\nPlease reply with your phone number from which you made the payment (e.g. <code>017XXXXXXXX</code>):",
        "manual_dep_ask_trxid": "🔖 <b>Enter Transaction ID (TrxID):</b>\n\nPlease reply with the <b>TrxID / Transaction ID</b> from your payment SMS or statement (e.g. <code>9J87HG65D4</code>):",
        "manual_dep_submitted": "✅ <b>Deposit Request Submitted Successfully!</b>\n\n🔖 <b>Deposit ID:</b> <code>{code}</code>\n💳 <b>Method:</b> <code>{method}</code>\n💵 <b>Amount:</b> <code>{symbol}{amount:.2f} ({bdt:.2f} BDT)</code>\n📱 <b>Sender Number:</b> <code>{sender}</code>\n🔖 <b>TrxID:</b> <code>{trx_id}</code>\n\n⏳ <i>Our admin team has received your deposit request. Your balance will be credited as soon as payment is verified.</i>",
        "deposit_approved_user": "🎉 <b>Deposit Approved & Credited!</b>\n\n🔖 <b>Deposit ID:</b> <code>{code}</code>\n💰 <b>Amount Credited:</b> <code>{symbol}{amount:.2f}</code>\n💳 <b>Method:</b> <code>{method}</code>\n\n✨ <i>Your wallet balance has been updated successfully!</i>",
        "deposit_rejected_user": "❌ <b>Deposit Request Rejected</b>\n\n🔖 <b>Deposit ID:</b> <code>{code}</code>\n💳 <b>Method:</b> <code>{method}</code>\n\n⚠️ <i>Reason: Payment could not be verified with the provided TrxID / Sender number. Please contact Support if you need assistance.</i>",

        # TxHash Validation
        "submit_tx_select_net": "⚡ <b>Submit On-Chain TxHash Verification</b>\n\n🔖 Invoice ID: <code>{code}</code>\n\n👇 Select the blockchain network you transferred on:",
        "submit_tx_prompt": "⚡ <b>Submit TxHash ({network})</b>\n\n🔖 Invoice: <code>{code}</code>\n🌐 Network: <code>{network}</code>\n\n📌 <b>How to get your TxHash:</b>\n1. Open your Binance App or Crypto Wallet -> <b>Withdrawal History</b>.\n2. Tap the transfer and copy the <b>TxID / TxHash</b> (64 or 66 character code).\n3. Send the copied code here.\n\n💡 <i>(Example: <code>0x78ab9c456...</code>)</i>",
        "fake_tx_hash_warn": "❌ <b>Invalid or Fake Transaction Hash (TxHash)!</b>\n\n⚠️ The text you provided: <code>{hash}</code> is not a valid blockchain transaction hash.\n\n📌 <b>How to find genuine TxHash:</b>\n• Go to your Binance / Wallet <b>Withdrawal History</b>.\n• Click on the transaction and copy the <b>TxID</b>.\n\n👉 Please reply with the genuine 64/66 character TxHash (or Cancel):",
        "tx_submitted_success": "✅ <b>TxHash Submitted Successfully!</b>\n\n🔖 <b>Invoice:</b> <code>{code}</code>\n🌐 <b>Network:</b> <code>{network}</code>\n🔗 <b>TxHash:</b> <code>{hash}</code>\n\n⏳ <i>The system is verifying your blockchain transaction. Your balance will be credited automatically once confirmed.</i>",
        "tx_verification_failed": "⚠️ <b>Transaction Verification Failed!</b>\n\n❌ <b>Reason:</b> <i>{reason}</i>\n\n💡 <b>Tips:</b>\n1. If you just sent the transaction, please wait 1-2 minutes for blockchain confirmations.\n2. Ensure you sent to the correct address on the <code>{network}</code> network.\n3. Click 'Check Payment Status' after a few moments.",

        # Orders & Profile & Language
        "orders_title": "📦 <b>Your Recent Orders:</b>\n\n",
        "orders_empty": "📦 <b>My Orders</b>\n\n⚠️ You haven't made any purchases yet.",
        "profile_title": "👤 <b>User Profile</b>\n\n🆔 <b>Telegram ID:</b> <code>{id}</code>\n👤 <b>Name:</b> {name}\n🏷 <b>Username:</b> @{username}\n💰 <b>Wallet Balance:</b> <code>{symbol}{balance:.2f}</code>\n📥 <b>Total Deposited:</b> <code>{symbol}{deposited:.2f}</code>\n🛒 <b>Total Spent:</b> <code>{symbol}{spent:.2f}</code>\n🌐 <b>Language:</b> {language}\n📅 <b>Member Since:</b> <code>{date}</code>",
        "support_text": "💬 <b>Nexvora Support & Help</b>\n\nNeed assistance with an order, deposit, or custom inquiry?\n\n👨‍💻 <b>Direct Admin Support:</b> {support}\n⚡ <b>Available:</b> 24/7 Fast Response",
        "language_menu": "🌐 <b>Select Your Language / ভাষা নির্বাচন করুন / زبان منتخب کریں / زبان خود را انتخاب کنید / اختر لغتك:</b>\n\nCurrent: <b>{current}</b>",
        "language_changed": "✅ Language changed to <b>{name}</b> successfully!"
    },

    "bn": {
        # Bengali / Bangladesh (বাংলা)
        "welcome_title": "নক্সভোরা শপে স্বাগতম, {name}!",
        "welcome_sub": "প্রিমিয়াম ডিজিটাল পণ্য, সাবস্ক্রিপশন এবং ইনস্ট্যান্ট সার্ভিসের স্বয়ংক্রিয় মার্কেটপ্লেস।",
        "balance": "আপনার বর্তমান ব্যালেন্স",
        "user_id": "আপনার ইউজার আইডি",
        "choose_option": "শুরু করতে নিচের যেকোনো অপশন বেছে নিন:",
        "btn_shop": "🛍 শপ / প্রোডাক্টস",
        "btn_wallet": "💳 আমার ওয়ালেট",
        "btn_orders": "📦 আমার অর্ডারসমূহ",
        "btn_profile": "👤 আমার প্রোফাইল",
        "btn_support": "💬 সাপোর্ট ও সাহায্য",
        "btn_language": "🌐 ভাষা (Language)",
        "btn_admin": "🛠 এডমিন প্যানেল",
        "btn_back_main": "🔙 মেইন মেনু",
        "btn_back": "🔙 পিছনে যান",
        
        # Promo Offer
        "btn_chatgpt_promo": "🔥 ChatGPT ৩-মাসের অফার ({symbol}{price:.2f})",
        "chatgpt_promo_title": "🤖 <b>ChatGPT ৩-মাসের স্পেশাল প্রোমো অফার</b>",
        "chatgpt_promo_desc": "আপনার ব্যক্তিগত জিমেইল / ইমেইলে সরাসরি ChatGPT ৩ মাসের প্রিমিয়াম সাবস্ক্রিপশন একটিভ করে নিন।",
        "chatgpt_promo_disabled": "⚠️ ChatGPT ৩-মাসের প্রোমো অফারটি বর্তমানে বন্ধ রয়েছে। অনুগ্রহ করে পরে চেক করুন!",
        "chatgpt_promo_ask_email": "🤖 <b>ChatGPT ৩-মাসের প্রোমো এক্টিভেশন</b>\n\n💵 অফার মূল্য: <code>{symbol}{price:.2f}</code>\n\n📧 <b>আপনার Gmail / Email এড্রেসটি লিখে পাঠান:</b>\n<i>(এই ইমেইলে আপনার ৩ মাসের সাবস্ক্রিপশন এক্টিভ করা হবে)</i>",
        "chatgpt_promo_invalid_email": "❌ <b>ভুল ইমেইল এড্রেস!</b>\n\n⚠️ অনুগ্রহ করে একটি সঠিক Gmail / Email এড্রেস লিখুন (যেমন: <code>example@gmail.com</code>):",
        "chatgpt_promo_order_submitted": "✅ <b>ChatGPT প্রোমো অর্ডার সফলভাবে জমা হয়েছে!</b>\n\n📦 <b>অফার:</b> <code>ChatGPT 3-Month Promo</code>\n🔖 <b>অর্ডার কোড:</b> <code>{code}</code>\n📧 <b>ইমেইল এড্রেস:</b> <code>{email}</code>\n💰 <b>পরিশোধিত মূল্য:</b> <code>{symbol}{price:.2f}</code>\n\n⏳ <i>এডমিন টিম আপনার ইমেইলে সাবস্ক্রিপশন একটিভ করছে। এক্টিভ হলে নোটিফিকেশন পাবেন (বা কোনো কারণে বাতিল হলে স্বয়ংক্রিয় রিফান্ড পেয়ে যাবেন)।</i>",
        "chatgpt_promo_activated_user": "🎉 <b>ChatGPT ৩-মাসের সাবস্ক্রিপশন একটিভ হয়েছে!</b>\n\n🔖 <b>অর্ডার কোড:</b> <code>{code}</code>\n📧 <b>ইমেইল এড্রেস:</b> <code>{email}</code>\n\n🎁 <b>আপনার প্রোমো কোড / এক্টিভেশন লিংক:</b>\n<code>{link}</code>\n\n✨ <i>এডমিন আপনার একাউন্টে ChatGPT ৩ মাসের প্রোমো সফলভাবে ডেলিভারি করেছে!</i>",
        "chatgpt_promo_refunded_user": "❌ <b>ChatGPT প্রোমো অর্ডার বাতিল ও রিফান্ড করা হয়েছে</b>\n\n🔖 <b>অর্ডার কোড:</b> <code>{code}</code>\n💰 <b>রিফান্ডকৃত টাকা:</b> <code>{symbol}{price:.2f}</code>\n\n💡 <i>সম্পূর্ণ টাকা আপনার ওয়ালেট ব্যালেন্সে ফেরত দেওয়া হয়েছে।</i>",

        # Shop / Catalog
        "catalog_title": "স্টোর ক্যাটালগ - ক্যাটাগরি",
        "catalog_empty": "⚠️ এই মুহূর্তে কোনো ক্যাটাগরি উপলব্ধ নেই। অনুগ্রহ করে কিছুক্ষণ পর আবার চেক করুন!",
        "select_cat": "প্রোডাক্ট দেখতে ক্যাটাগরি সিলেক্ট করুন:",
        "category_empty": "⚠️ এই ক্যাটাগরিতে বর্তমানে কোনো প্রোডাক্ট নেই।",
        "select_product": "বিস্তারিত দেখতে ও কিনতে প্রোডাক্ট বেছে নিন:",
        "in_stock": "স্টকে আছে",
        "out_of_stock": "স্টক শেষ",
        "instant_service": "ইনস্ট্যান্ট সার্ভিস",
        "available_request": "অনুরোধে উপলব্ধ",
        "instant_delivery_info": "⚡ <b>ইনস্ট্যান্ট ডিজিটাল ডেলিভারি</b> <i>(কেনার সাথে সাথেই চ্যাটে অটোমেটিক কি/কোড পেয়ে যাবেন)</i>",
        "manual_delivery_info": "🛠 <b>ম্যানুয়াল সার্ভিস / অর্ডার</b> <i>(এডমিন অর্ডারটি চেক করে ডেলিভারি দেবেন)</i>",
        "price": "মূল্য",
        "product_label": "প্রোডাক্ট",
        "category_label": "ক্যাটাগরি",
        "description_label": "বিবরণ",
        "btn_buy_balance": "💳 ব্যালেন্স দিয়ে কিনুন ({symbol}{price:.2f})",
        "btn_buy_crypto": "🪙 ডিরেক্ট ক্রিপ্টো ইনভয়েস ({symbol}{price:.2f})",
        "btn_back_products": "🔙 প্রোডাক্ট তালিকায় ফিরুন",
        "btn_back_categories": "🔙 ক্যাটাগরিতে ফিরুন",
        
        # Purchase
        "insufficient_balance": "❌ <b>অপর্যাপ্ত ব্যালেন্স</b>\n\nপ্রয়োজনীয় মূল্য: <code>{symbol}{price:.2f}</code>\nআপনার ব্যালেন্স: <code>{symbol}{balance:.2f}</code>\nআপনার আরও <code>{symbol}{shortage:.2f}</code> প্রয়োজন।\n\n👇 বিকাশ, নগদ বা ক্রিপ্টোর মাধ্যমে ব্যালেন্স যোগ করতে নিচের বাটনে চাপুন!",
        "btn_deposit_now": "📥 এখনই ডিপোজিট করুন",
        "purchase_success": "🎉 <b>কেনাকাটা সফল হয়েছে!</b>\n\n📦 <b>প্রোডাক্ট:</b> <code>{name}</code>\n🔖 <b>অর্ডার কোড:</b> <code>{code}</code>\n💰 <b>পরিশোধিত মূল্য:</b> <code>{symbol}{price:.2f}</code>\n\n🔑 <b>ডেলিভারিকৃত কোড / অ্যাকাউন্ট তথ্য:</b>\n<pre>{item}</pre>\n\n💡 <i>আপনি যেকোনো সময় 'আমার অর্ডারসমূহ' থেকে এটি পুনরায় দেখতে পারবেন।</i>",
        "btn_continue_shopping": "🛍 আরও কেনাকাটা করুন",
        "manual_prompt": "📝 <b>ম্যানুয়াল অর্ডার: {name}</b>\n\nমূল্য: <code>{symbol}{price:.2f}</code>\n\nঅর্ডারটি সম্পন্ন করতে আপনার প্রয়োজনীয় বিবরণ (যেমন: ইমেইল, ইউজারনেম বা রিকোয়ারমেন্ট) লিখে মেসেজ পাঠান:",
        "manual_submitted": "✅ <b>অর্ডার সফলভাবে জমা দেওয়া হয়েছে!</b>\n\n📦 <b>প্রোডাক্ট:</b> <code>{name}</code>\n🔖 <b>অর্ডার কোড:</b> <code>{code}</code>\n💰 <b>পরিশোধিত মূল্য:</b> <code>{symbol}{price:.2f}</code>\n📝 <b>আপনার তথ্য:</b>\n<code>{details}</code>\n\n⏳ <i>আমাদের টিম আপনার অর্ডারটি প্রসেস করছে। সম্পন্ন হওয়া মাত্রই আপনাকে মেসেজ পাঠিয়ে জানানো হবে।</i>",

        # Wallet & Deposit Gateways
        "wallet_title": "💳 <b>আমার ওয়ালেট ও ব্যালেন্স</b>\n\n💰 <b>বর্তমান ব্যালেন্স:</b> <code>{symbol}{balance:.2f} {currency}</code>\n📥 <b>মোট ডিপোজিট:</b> <code>{symbol}{deposited:.2f}</code>\n🛒 <b>মোট কেনাকাটা:</b> <code>{symbol}{spent:.2f}</code>\n\n⚡ <i>সহজ ডিপোজিট অপশন: ক্রিপ্টো (অটো ভেরিফাই), বিকাশ, নগদ এবং অন্যান্য মাধ্যম।</i>",
        "btn_deposit": "📥 ব্যালেন্স ডিপোজিট করুন",
        "deposit_select_method": "📥 <b>পেমেন্ট / ডিপোজিট পদ্ধতি বেছে নিন</b>\n\nওয়ালেটে টাকা যোগ করতে আপনার পছন্দের মেথড সিলেক্ট করুন:",
        "btn_crypto_gateway": "🪙 USDT / ক্রিপ্টো (অটো ইনস্ট্যান্ট)",
        "deposit_menu": "📥 <b>ক্রিপ্টো ডিপোজিট (USDT Multi-Chain)</b>\n\n🪙 <b>সাপোর্টেড নেটওয়ার্ক:</b>\n• <b>USDT - BEP20</b> (BNB Smart Chain)\n• <b>USDT - TRC20</b> (TRON Network)\n• <b>USDT - ERC20</b> (Ethereum)\n\n📌 <i>সর্বনিম্ন ডিপোজিট:</i> <code>{symbol}{min_dep:.2f}</code>\n\nএকটি পরিমাণ সিলেক্ট করুন বা কাস্টম পরিমাণ লিখুন:",
        "btn_custom_amount": "✏️ কাস্টম পরিমাণ",
        "custom_amount_prompt": "✏️ <b>কাস্টম ডিপোজিট পরিমাণ লিখুন</b>\n\nঅনুগ্রহ করে USDT তে পরিমাণ লিখে পাঠান (সর্বনিম্ন <code>{symbol}{min_dep:.2f}</code>):\n<i>(যেমন: <code>15</code> বা <code>35.50</code>)</i>",
        "invalid_amount_min": "❌ <b>ভুল পরিমাণ দেওয়া হয়েছে!</b>\n\n⚠️ আপনি <code>{symbol}{amount:.2f}</code> লিখেছেন, কিন্তু সর্বনিম্ন ডিপোজিট হলো <code>{symbol}{min_dep:.2f}</code>।\n\n👉 অনুগ্রহ করে <code>{min_dep:.2f}</code> বা তার বেশি পরিমাণ লিখুন (যেমন: <code>10</code> বা <code>25.50</code>):",
        "invalid_amount_number": "❌ <b>ভুল ইনপুট!</b>\n\n⚠️ কোনো অক্ষর বা চিহ্ন দেওয়া যাবে না।\n👉 অনুগ্রহ করে শুধুমাত্র সঠিক সংখ্যার পরিমাণটি লিখুন (যেমন: <code>10</code>, <code>20</code> বা <code>50</code>):",
        
        # Crypto Invoice
        "invoice_title": "🪙 <b>পেমেন্ট ইনভয়েস তৈরি হয়েছে</b>\n\n🔖 <b>ইনভয়েস ID:</b> <code>{code}</code>\n💵 <b>পরিমাণ:</b> <code>{symbol}{amount:.2f} USDT</code>\n⏳ <b>স্ট্যাটাস:</b> <code>পেমেন্টের অপেক্ষায় (INITIAL)</code>\n\n━━━━━━━━━━━━━━━━━━━━\n🌐 <b>মাল্টি-চেইন USDT ট্রান্সফার এড্রেস:</b>\nনিচের যেকোনো একটি এড্রেসে ঠিক <code>{amount:.2f} USDT</code> সেন্ড করুন:\n\n🟡 <b>BEP20 (BNB Smart Chain):</b>\n<code>{bep20}</code>\n\n🔴 <b>TRC20 (TRON Network):</b>\n<code>{trc20}</code>\n\n🔵 <b>ERC20 (Ethereum):</b>\n<code>{erc20}</code>\n━━━━━━━━━━━━━━━━━━━━\n💡 <i>ট্রান্সফার করার পর '🔄 Check Payment Status' চাপুন অথবা আপনার TxHash সাবমিট করুন।</i>",
        "btn_check_status": "🔄 পেমেন্ট স্ট্যাটাস চেক করুন",
        "btn_submit_tx": "⚡ TxHash সাবমিট করুন",
        "deposit_confirmed": "🎉 <b>ডিপোজিট সফলভাবে জমা হয়েছে!</b>\n\n🔖 <b>ইনভয়েস ID:</b> <code>{code}</code>\n💰 <b>জমা হওয়া ব্যালেন্স:</b> <code>{symbol}{amount:.2f} USDT</code>\n🌐 <b>নেটওয়ার্ক:</b> <code>{network}</code>\n\n✨ <i>আপনার ওয়ালেটে ব্যালেন্স যুক্ত করা হয়েছে। কেনাকাটার জন্য প্রস্তুত!</i>",
        "deposit_already_credited": "✅ এই ডিপোজিটটি আগেই সফলভাবে ওয়ালেটে যুক্ত হয়েছে!",
        "deposit_pending": "⏳ পেমেন্ট এখনও ব্লকচেইনে কনফার্ম হয়নি। আপনি যদি মাত্র ট্রান্সফার করে থাকেন, তবে ১-২ মিনিট অপেক্ষা করে আবার চেক করুন।",
        
        # Manual Deposit Flow (bKash / Nagad / Local)
        "manual_dep_info": "📱 <b>{name} ডিপোজিট নির্দেশনা</b>\n\n📌 <b>অ্যাকাউন্ট বিবরণ:</b>\n<code>{details}</code> <i>(কপি করতে ট্যাপ করুন)</i>\n\n📝 <b>নির্দেশনা:</b> {instructions}\n💵 <b>এক্সচেঞ্জ রেট:</b> <code>$১.০০ = {rate:.2f} টাকা</code>\n📌 <b>সর্বনিম্ন ডিপোজিট:</b> <code>{symbol}{min_dep:.2f} ({min_bdt:.2f} টাকা)</code>\n\n👉 <i>টাকা পাঠানোর পর নিচের বাটনে চাপ দিয়ে আপনার পেমেন্ট তথ্য সাবমিট করুন:</i>",
        "btn_submit_manual_dep": "📝 পেমেন্ট তথ্য সাবমিট করুন",
        "manual_dep_ask_amount": "💵 <b>ডিপোজিট পরিমাণ লিখুন:</b>\n\nএক্সচেঞ্জ রেট: <code>$১.০০ = {rate:.2f} টাকা</code>\n\nঅনুগ্রহ করে কত <b>ডলার ($)</b> (যেমন: <code>10</code>) অথবা কত <b>টাকা</b> (যেমন: <code>1250</code>) পাঠিয়েছেন তা লিখুন:\n<i>(সর্বনিম্ন: {symbol}{min_dep:.2f})</i>",
        "manual_dep_ask_sender": "📱 <b>সেন্ডার ফোন নম্বর লিখুন:</b>\n\nযে বিকাশ/নগদ নম্বর থেকে টাকা পাঠিয়েছেন সেই নম্বরটি লিখুন (যেমন: <code>017XXXXXXXX</code>):",
        "manual_dep_ask_trxid": "🔖 <b>Transaction ID (TrxID) লিখুন:</b>\n\nপেমেন্ট এসএমএস থেকে প্রাপ্ত <b>TrxID / ট্রানজ্যাকশন আইডি</b> লিখে পাঠান (যেমন: <code>9J87HG65D4</code>):",
        "manual_dep_submitted": "✅ <b>ডিপোজিট রিকোয়েস্ট সফলভাবে জমা হয়েছে!</b>\n\n🔖 <b>ডিপোজিট ID:</b> <code>{code}</code>\n💳 <b>মেথড:</b> <code>{method}</code>\n💵 <b>পরিমাণ:</b> <code>{symbol}{amount:.2f} ({bdt:.2f} টাকা)</code>\n📱 <b>সেন্ডার নম্বর:</b> <code>{sender}</code>\n🔖 <b>TrxID:</b> <code>{trx_id}</code>\n\n⏳ <i>এডমিন টিম আপনার পেমেন্ট চেক করছে। ভেরিফাই হওয়া মাত্রই আপনার ওয়ালেটে ব্যালেন্স যোগ হয়ে যাবে।</i>",
        "deposit_approved_user": "🎉 <b>ডিপোজিট সফলভাবে অনুমোদিত হয়েছে!</b>\n\n🔖 <b>ডিপোজিট ID:</b> <code>{code}</code>\n💰 <b>যোগ হওয়া ব্যালেন্স:</b> <code>{symbol}{amount:.2f}</code>\n💳 <b>মেথড:</b> <code>{method}</code>\n\n✨ <i>আপনার ওয়ালেট ব্যালেন্স আপডেট করা হয়েছে!</i>",
        "deposit_rejected_user": "❌ <b>ডিপোজিট রিকোয়েস্ট বাতিল করা হয়েছে</b>\n\n🔖 <b>ডিপোজিট ID:</b> <code>{code}</code>\n💳 <b>মেথড:</b> <code>{method}</code>\n\n⚠️ <i>কারণ: আপনার প্রদত্ত TrxID বা সেন্ডার নম্বরে পেমেন্ট পাওয়া যায়নি। সহায়তার জন্য সাপোর্টে যোগাযোগ করুন।</i>",

        # TxHash Validation
        "submit_tx_select_net": "⚡ <b>অন-চেইন TxHash ভেরিফিকেশন</b>\n\n🔖 ইনভয়েস ID: <code>{code}</code>\n\n👇 আপনি কোন নেটওয়ার্কের মাধ্যমে ট্রান্সফার করেছেন তা সিলেক্ট করুন:",
        "submit_tx_prompt": "⚡ <b>TxHash সাবমিট করুন ({network})</b>\n\n🔖 ইনভয়েস: <code>{code}</code>\n🌐 নেটওয়ার্ক: <code>{network}</code>\n\n📌 <b>সঠিক TxHash পাওয়ার নিয়ম:</b>\n১. আপনার Binance App বা ক্রিপ্টো ওয়ালেটের <b>Withdrawal History</b>-তে যান।\n২. ট্রানজ্যাকশনটির উপর ক্লিক করে <b>TxID / TxHash</b> কপি করুন (৬৪ বা ৬৬ অক্ষরের কোড)।\n৩. কপি করা কোডটি এখানে মেসেজ করুন।\n\n💡 <i>(যেমন: <code>0x78ab9c456...</code>)</i>",
        "fake_tx_hash_warn": "❌ <b>ভুল বা নকল Transaction Hash (TxHash)!</b>\n\n⚠️ আপনি যে তথ্যটি দিয়েছেন: <code>{hash}</code> — এটি কোনো সঠিক ব্লকচেইন ট্রানজ্যাকশন হ্যাশ নয়।\n\n📌 <b>সঠিক হ্যাশ কোথায় পাবেন:</b>\n• আপনার Binance App বা ওয়ালেটের <b>Withdrawal History</b>-তে যান।\n• ডিপোজিট করা ট্রানজ্যাকশনটির আসল <b>TxID</b> কপি করে আনুন।\n\n👉 অনুগ্রহ করে সঠিক ৬৪/৬৬ অক্ষরের আসল TxHash টি পাঠান:",
        "tx_submitted_success": "✅ <b>TxHash সফলভাবে সাবমিট হয়েছে!</b>\n\n🔖 <b>ইনভয়েস:</b> <code>{code}</code>\n🌐 <b>নেটওয়ার্ক:</b> <code>{network}</code>\n🔗 <b>TxHash:</b> <code>{hash}</code>\n\n⏳ <i>সিস্টেম ব্লকচেইন কনফার্মেশন চেক করছে। ব্লক কনফার্ম হওয়া মাত্রই ব্যালেন্স অটোমেটিক যোগ হয়ে যাবে।</i>",
        "tx_verification_failed": "⚠️ <b>ট্রানজ্যাকশন ভেরিফিকেশন করা যায়নি!</b>\n\n❌ <b>কারণ:</b> <i>{reason}</i>\n\n💡 <b>পরামর্শ:</b>\n১. আপনি যদি মাত্র ১-২ সেকেন্ড আগে পাঠিয়ে থাকেন, তবে ব্লকচেইনে আসতে ১-২ মিনিট সময় লাগতে পারে।\n২. সঠিক নেটওয়ার্কে ও সঠিক ঠিকানায় ফান্ড পাঠিয়েছেন কিনা তা নিশ্চিত করুন।\n৩. কিছুক্ষণ পর 'পেমেন্ট স্ট্যাটাস চেক করুন' বাটনে চাপুন।",

        "orders_title": "📦 <b>আপনার সাম্প্রতিক অর্ডারসমূহ:</b>\n\n",
        "orders_empty": "📦 <b>আমার অর্ডারসমূহ</b>\n\n⚠️ আপনি এখনও কোনো কেনাকাটা করেননি।",
        "profile_title": "👤 <b>ইউজার প্রোফাইল</b>\n\n🆔 <b>টেলিগ্রাম আইডি:</b> <code>{id}</code>\n👤 <b>নাম:</b> {name}\n🏷 <b>ইউজারনেম:</b> @{username}\n💰 <b>ওয়ালেট ব্যালেন্স:</b> <code>{symbol}{balance:.2f}</code>\n📥 <b>মোট ডিপোজিট:</b> <code>{symbol}{deposited:.2f}</code>\n🛒 <b>মোট কেনাকাটা:</b> <code>{symbol}{spent:.2f}</code>\n🌐 <b>ভাষা:</b> {language}\n📅 <b>যোগদানের তারিখ:</b> <code>{date}</code>",
        "support_text": "💬 <b>সাপোর্ট ও সাহায্য</b>\n\nকোনো অর্ডার, ডিপোজিট বা সহায়তার প্রয়োজন হলে যোগাযোগ করুন:\n\n👨‍💻 <b>সরাসরি এডমিন সাপোর্ট:</b> {support}\n⚡ <b>সময়:</b> ২৪/৭ দ্রুত রেসপন্স",
        "language_menu": "🌐 <b>ভাষা নির্বাচন করুন (Select Language):</b>\n\nবর্তমান ভাষা: <b>{current}</b>",
        "language_changed": "✅ ভাষা সফলভাবে <b>{name}</b> এ পরিবর্তন করা হয়েছে!"
    },

    "ur": {
        # Urdu / Pakistan (اردو)
        "welcome_title": "Nexvora Shop میں خوش آمدید، {name}!",
        "welcome_sub": "ڈیجیٹل مصنوعات، سبسکرپشنز اور فوری خدمات کے لیے آپ کا خودکار بازار۔",
        "balance": "آپ کا بیلنس",
        "user_id": "آپ کا صارف ID",
        "choose_option": "شروع کرنے کے لیے نیچے دیے گئے اختیارات میں سے انتخاب کریں:",
        "btn_shop": "🛍 دکان / پروڈکٹس",
        "btn_wallet": "💳 میرا والٹ",
        "btn_orders": "📦 میرے آرڈرز",
        "btn_profile": "👤 میری پروفائل",
        "btn_support": "💬 مدد اور سپورٹ",
        "btn_language": "🌐 زبان (Language)",
        "btn_admin": "🛠 ایڈمن پینل",
        "btn_back_main": "🔙 مین مینو پر واپس جائیں",
        "btn_back": "🔙 واپس",
        
        # Promo Offer
        "btn_chatgpt_promo": "🔥 چیٹ جی پی ٹی 3 ماہ کی آفر ({symbol}{price:.2f})",
        "chatgpt_promo_title": "🤖 <b>ChatGPT 3-Month پرومو آفر</b>",
        "chatgpt_promo_desc": "اپنے ذاتی جی میل / ای میل ایڈریس پر براہ راست ChatGPT 3 ماہ کی سبسکرپشن فعال کروائیں۔",
        "chatgpt_promo_disabled": "⚠️ ChatGPT 3-Month پرومو آفر فی الحال ایڈمن کی طرف سے بند ہے۔",
        "chatgpt_promo_ask_email": "🤖 <b>ChatGPT 3-Month پرومو ایکٹیویشن</b>\n\n💵 قیمت: <code>{symbol}{price:.2f}</code>\n\n📧 <b>براہ کرم اپنا Gmail / Email ایڈریس بھیجیں:</b>\n<i>(ہم اس ای میل پر 3 ماہ کی سبسکرپشن فعال کریں گے)</i>",
        "chatgpt_promo_invalid_email": "❌ <b>غلط ای میل ایڈریس!</b>\n\n⚠️ براہ کرم درست ای میل درج کریں (مثال: <code>example@gmail.com</code>):",
        "chatgpt_promo_order_submitted": "✅ <b>ChatGPT پرومو آرڈر جمع ہو گیا!</b>\n\n📦 <b>آفر:</b> <code>ChatGPT 3-Month Promo</code>\n🔖 <b>آرڈر کوڈ:</b> <code>{code}</code>\n📧 <b>ای میل:</b> <code>{email}</code>\n💰 <b>ادا شدہ رقم:</b> <code>{symbol}{price:.2f}</code>\n\n⏳ <i>ایڈمن آپ کے ای میل پر کارروائی کر رہا ہے۔ ایکٹیویشن پر آپ کو مطلع کر دیا جائے گا (منسوخ ہونے پر فوری ریفنڈ)۔</i>",
        "chatgpt_promo_activated_user": "🎉 <b>ChatGPT 3-Month سبسکرپشن فعال ہو گئی!</b>\n\n🔖 <b>آرڈر:</b> <code>{code}</code>\n📧 <b>ای میل:</b> <code>{email}</code>\n\n🎁 <b>آپ کا پرومو کوڈ / لنک:</b>\n<code>{link}</code>\n\n✨ <i>ایڈمن نے آپ کے لیے ChatGPT 3 ماہ کا پرومو کامیابی سے فعال کر دیا ہے۔</i>",
        "chatgpt_promo_refunded_user": "❌ <b>ChatGPT آرڈر منسوخ اور رقم واپس!</b>\n\n🔖 <b>آرڈر:</b> <code>{code}</code>\n💰 <b>واپس کردہ رقم:</b> <code>{symbol}{price:.2f}</code>\n\n💡 <i>پوری رقم آپ کے والٹ بیلنس میں واپس جمع کر دی گئی ہے۔</i>",

        # Shop / Catalog
        "catalog_title": "اسٹور کیٹلاگ - کیٹیگریز",
        "catalog_empty": "⚠️ فی الحال کوئی کیٹیگری دستیاب نہیں ہے۔ براہ کرم جلد دوبارہ چیک کریں!",
        "select_cat": "پروڈکٹس دیکھنے کے لیے کیٹیگری منتخب کریں:",
        "category_empty": "⚠️ اس کیٹیگری میں فی الحال کوئی پروڈکٹ دستیاب نہیں ہے۔",
        "select_product": "تفصیلات اور خریداری کے لیے پروڈکٹ منتخب کریں:",
        "in_stock": "دستیاب",
        "out_of_stock": "اسٹاک ختم",
        "instant_service": "فوری سروس",
        "available_request": "درخواست پر دستیاب",
        "instant_delivery_info": "⚡ <b>فوری ڈیجیٹل ترسیل</b> <i>(خریداری کے فوراً بعد چیٹ میں کوڈ/اکاؤنٹ فراہم کیا جائے گا)</i>",
        "manual_delivery_info": "🛠 <b>دستی سروس / آرڈر</b> <i>(ایڈمن آرڈر پر کارروائی کرے گا)</i>",
        "price": "قیمت",
        "product_label": "پروڈکٹ",
        "category_label": "کیٹیگری",
        "description_label": "تفصیل",
        "btn_buy_balance": "💳 بیلنس سے خریدیں ({symbol}{price:.2f})",
        "btn_buy_crypto": "🪙 براہ راست کرپٹو انوائس ({symbol}{price:.2f})",
        "btn_back_products": "🔙 پروڈکٹس پر واپس",
        "btn_back_categories": "🔙 کیٹیگریز پر واپس",
        
        "insufficient_balance": "❌ <b>ناکافی بیلنس</b>\n\nمطلوبہ: <code>{symbol}{price:.2f}</code>\nآپ کا بیلنس: <code>{symbol}{balance:.2f}</code>\nآپ کو مزید <code>{symbol}{shortage:.2f}</code> کی ضرورت ہے۔\n\n👇 کرپٹو یا مقامی ادائیگی کے ذریعے رقم جمع کریں!",
        "btn_deposit_now": "📥 ابھی ڈپازٹ کریں",
        "purchase_success": "🎉 <b>خریداری کامیاب!</b>\n\n📦 <b>پروڈکٹ:</b> <code>{name}</code>\n🔖 <b>آرڈر کوڈ:</b> <code>{code}</code>\n💰 <b>ادا شدہ رقم:</b> <code>{symbol}{price:.2f}</code>\n\n🔑 <b>فراہم کردہ آئٹم / کوڈ / اکاؤنٹ:</b>\n<pre>{item}</pre>\n\n💡 <i>آپ اسے کسی بھی وقت 'میرے آرڈرز' میں دیکھ سکتے ہیں۔</i>",
        "btn_continue_shopping": "🛍 مزید خریداری کریں",
        "manual_prompt": "📝 <b>دستی سروس آرڈر: {name}</b>\n\nقیمت: <code>{symbol}{price:.2f}</code>\n\nخریداری مکمل کرنے کے لیے براہ کرم اپنے آرڈر کی ضروری تفصیلات (مثلاً ای میل، یوزر نیم) درج کریں:",
        "manual_submitted": "✅ <b>آرڈر کامیابی سے جمع ہو گیا!</b>\n\n📦 <b>پروڈکٹ:</b> <code>{name}</code>\n🔖 <b>آرڈر کوڈ:</b> <code>{code}</code>\n💰 <b>ادا شدہ رقم:</b> <code>{symbol}{price:.2f}</code>\n📝 <b>آپ کی تفصیلات:</b>\n<code>{details}</code>\n\n⏳ <i>ہماری ٹیم کو آپ کا آرڈر موصول ہو گیا ہے۔ تکمیل پر آپ کو یہاں مطلع کر دیا جائے گا۔</i>",

        "wallet_title": "💳 <b>میرا والٹ اور بیلنس</b>\n\n💰 <b>موجودہ بیلنس:</b> <code>{symbol}{balance:.2f} {currency}</code>\n📥 <b>کل ڈپازٹ:</b> <code>{symbol}{deposited:.2f}</code>\n🛒 <b>کل خرچ:</b> <code>{symbol}{spent:.2f}</code>\n\n⚡ <i>ڈپازٹ طریقے: کرپٹو (خودکار)، ایزی پیسہ، جاز کیش اور دیگر۔</i>",
        "btn_deposit": "📥 بیلنس ڈپازٹ کریں",
        "deposit_select_method": "📥 <b>ادائیگی کا طریقہ منتخب کریں</b>\n\nوالٹ میں بیلنس شامل کرنے کے لیے طریقہ منتخب کریں:",
        "btn_crypto_gateway": "🪙 USDT / کرپٹو (فوری خودکار)",
        "deposit_menu": "📥 <b>کرپٹو ڈپازٹ (USDT Multi-Chain)</b>\n\n🪙 <b>سپورٹ شدہ نیٹ ورک:</b>\n• <b>USDT - BEP20</b> (BNB اسمارٹ چین)\n• <b>USDT - TRC20</b> (TRON نیٹ ورک)\n• <b>USDT - ERC20</b> (ایتھیریم)\n\n📌 <i>کم از کم ڈپازٹ:</i> <code>{symbol}{min_dep:.2f}</code>\n\nکوئی رقم منتخب کریں یا کسٹم رقم درج کریں:",
        "btn_custom_amount": "✏️ کسٹم رقم",
        "custom_amount_prompt": "✏️ <b>کسٹم ڈپازٹ رقم درج کریں</b>\n\nبراہ کرم USDT میں رقم درج کریں (کم از کم <code>{symbol}{min_dep:.2f}</code>):\n<i>(مثال: <code>15</code> یا <code>35.50</code>)</i>",
        "invalid_amount_min": "❌ <b>غلط رقم!</b>\n\n⚠️ آپ نے <code>{symbol}{amount:.2f}</code> درج کیا ہے، لیکن کم از کم ڈپازٹ <code>{symbol}{min_dep:.2f}</code> ہے۔\n\n👉 براہ کرم <code>{min_dep:.2f}</code> یا اس سے زیادہ درج کریں (مثلاً: <code>10</code> یا <code>25.50</code>):",
        "invalid_amount_number": "❌ <b>غلط ان پٹ!</b>\n\n⚠️ حروف یا علامات کی اجازت نہیں ہے۔\n👉 براہ کرم صرف درست نمبر درج کریں (مثلاً: <code>10</code>, <code>20</code> یا <code>50</code>):",
        "invoice_title": "🪙 <b>پیمنٹ انوائس تیار ہے</b>\n\n🔖 <b>انوائس ID:</b> <code>{code}</code>\n💵 <b>رقم:</b> <code>{symbol}{amount:.2f} USDT</code>\n⏳ <b>حیثیت:</b> <code>ادائیگی کا انتظار (INITIAL)</code>\n\n━━━━━━━━━━━━━━━━━━━━\n🌐 <b>ملٹی چین کرپٹو ٹرانسفر ایڈریسز:</b>\nدرج ذیل کسی بھی ایڈریس پر ٹھیک <code>{amount:.2f} USDT</code> بھیجیں:\n\n🟡 <b>BEP20 (BNB Smart Chain):</b>\n<code>{bep20}</code>\n\n🔴 <b>TRC20 (TRON Network):</b>\n<code>{trc20}</code>\n\n🔵 <b>ERC20 (Ethereum):</b>\n<code>{erc20}</code>\n━━━━━━━━━━━━━━━━━━━━\n💡 <i>ٹرانسفر کے بعد 'چیک پیمنٹ اسٹیٹس' دبائیں یا اپنا TxHash جمع کروائیں۔</i>",
        "btn_check_status": "🔄 اسٹیٹس چیک کریں",
        "btn_submit_tx": "⚡ ٹرانزیکشن ہیش (TxHash) دیں",
        "deposit_confirmed": "🎉 <b>ڈپازٹ کامیابی سے موصول ہوا!</b>\n\n🔖 <b>انوائس ID:</b> <code>{code}</code>\n💰 <b>شامل شدہ رقم:</b> <code>{symbol}{amount:.2f} USDT</code>\n🌐 <b>نیٹ ورک:</b> <code>{network}</code>\n\n✨ <i>آپ کا والٹ بیلنس اپ ڈیٹ ہو گیا ہے۔ خریداری کے لیے تیار!</i>",
        "deposit_already_credited": "✅ یہ ڈپازٹ پہلے ہی آپ کے والٹ میں شامل کیا جا چکا ہے!",
        "deposit_pending": "⏳ ادائیگی ابھی بلاک چین پر کنفرم نہیں ہوئی۔ براہ کرم 1-2 منٹ بعد دوبارہ چیک کریں۔",
        
        "manual_dep_info": "📱 <b>{name} ڈپازٹ کی ہدایات</b>\n\n📌 <b>اکاؤنٹ کی تفصیلات:</b>\n<code>{details}</code>\n\n📝 <b>ہدایات:</b> {instructions}\n💵 <b>ایکسچینج ریٹ:</b> <code>$1.00 = {rate:.2f}</code>\n📌 <b>کم از کم ڈپازٹ:</b> <code>{symbol}{min_dep:.2f}</code>\n\n👉 <i>رقم بھیجنے کے بعد اپنی ادائیگی کی تفصیلات جمع کروائیں:</i>",
        "btn_submit_manual_dep": "📝 ادائیگی کی تفصیلات بھیجیں",
        "manual_dep_ask_amount": "💵 <b>ڈپازٹ کی رقم درج کریں:</b>\n\nریٹ: <code>$1.00 = {rate:.2f}</code>\n\nبراہ کرم ادا کردہ رقم درج کریں (USD یا مقامی کرنسی):",
        "manual_dep_ask_sender": "📱 <b>بھیجنے والے کا فون نمبر درج کریں:</b>\n\nجس نمبر سے رقم بھیجی ہے وہ نمبر درج کریں:",
        "manual_dep_ask_trxid": "🔖 <b>Transaction ID (TrxID) درج کریں:</b>\n\nایس ایم ایس سے ٹرانزیکشن آئی ڈی درج کریں:",
        "manual_dep_submitted": "✅ <b>ڈپازٹ کی درخواست جمع ہو گئی!</b>\n\n🔖 <b>ڈپازٹ ID:</b> <code>{code}</code>\n💳 <b>طریقہ:</b> <code>{method}</code>\n💵 <b>رقم:</b> <code>{symbol}{amount:.2f}</code>\n\n⏳ <i>ایڈمن تصدیق کے بعد رقم والٹ میں شامل کر دے گا۔</i>",
        "deposit_approved_user": "🎉 <b>ڈپازٹ منظور اور شامل کر دیا گیا!</b>\n\n🔖 <b>ڈپازٹ ID:</b> <code>{code}</code>\n💰 <b>شامل شدہ رقم:</b> <code>{symbol}{amount:.2f}</code>\n💳 <b>طریقہ:</b> <code>{method}</code>\n\n✨ <i>آپ کا بیلنس اپ ڈیٹ ہو گیا ہے!</i>",
        "deposit_rejected_user": "❌ <b>ڈپازٹ کی درخواست مسترد کر دی گئی</b>\n\n🔖 <b>ڈپازٹ ID:</b> <code>{code}</code>\n💳 <b>طریقہ:</b> <code>{method}</code>\n\n⚠️ <i>دی گئی تفصیلات سے ادائیگی کی تصدیق نہیں ہو سکی۔</i>",

        "submit_tx_select_net": "⚡ <b>آن چین TxHash تصدیق</b>\n\n🔖 انوائس ID: <code>{code}</code>\n\n👇 جس نیٹ ورک سے رقم بھیجی ہے وہ منتخب کریں:",
        "submit_tx_prompt": "⚡ <b>TxHash درج کریں ({network})</b>\n\n🔖 انوائس: <code>{code}</code>\n🌐 نیٹ ورک: <code>{network}</code>\n\n📌 <b>درست TxHash حاصل کرنے کا طریقہ:</b>\n1. بائننس ایپ یا والٹ کی <b>Withdrawal History</b> کھولیں۔\n2. ٹرانزیکشن پر کلک کر کے <b>TxID / TxHash</b> کاپی کریں۔\n3. کاپی شدہ کوڈ یہاں بھیجیں۔\n\n💡 <i>(مثال: <code>0x78ab9c456...</code>)</i>",
        "fake_tx_hash_warn": "❌ <b>غلط یا جعلی ٹرانزیکشن ہیش (TxHash)!</b>\n\n⚠️ آپ کا فراہم کردہ ٹیکسٹ: <code>{hash}</code> درست بلاک چین ہیش نہیں ہے۔\n\n📌 <b>درست ہیش کہاں ملے گی:</b>\n• اپنے بائننس یا والٹ کی <b>Withdrawal History</b> میں جائیں۔\n• ٹرانزیکشن کی اصل <b>TxID</b> کاپی کر کے لائیں۔\n\n👉 براہ کرم اصل 64/66 ہندسوں کا TxHash دوبارہ بھیجیں:",
        "tx_submitted_success": "✅ <b>TxHash کامیابی سے جمع ہو گیا!</b>\n\n🔖 <b>انوائس:</b> <code>{code}</code>\n🌐 <b>نیٹ ورک:</b> <code>{network}</code>\n🔗 <b>TxHash:</b> <code>{hash}</code>\n\n⏳ <i>سسٹم تصدیق کر رہا ہے۔ تصدیق ہوتے ہی بیلنس شامل کر دیا جائے گا۔</i>",
        "tx_verification_failed": "⚠️ <b>ٹرانزیکشن کی تصدیق نہیں ہو سکی!</b>\n\n❌ <b>وجہ:</b> <i>{reason}</i>\n\n💡 <b>رہنمائی:</b>\n1. اگر ابھی رقم بھیجی ہے تو بلاک چین کنفرمیشن کے لیے 1-2 منٹ انتظار کریں۔\n2. یقینی بنائیں کہ آپ نے درست نیٹ ورک پر رقم بھیجی ہے۔\n3. تھوڑی دیر بعد دوبارہ اسٹیٹس چیک کریں۔",

        "orders_title": "📦 <b>آپ کے حالیہ آرڈرز:</b>\n\n",
        "orders_empty": "📦 <b>میرے آرڈرز</b>\n\n⚠️ آپ نے ابھی تک کوئی خریداری نہیں کی ہے۔",
        "profile_title": "👤 <b>صارف پروفائل</b>\n\n🆔 <b>ٹیلیگرام ID:</b> <code>{id}</code>\n👤 <b>نام:</b> {name}\n🏷 <b>یوزر نیم:</b> @{username}\n💰 <b>والٹ بیلنس:</b> <code>{symbol}{balance:.2f}</code>\n📥 <b>کل ڈپازٹ:</b> <code>{symbol}{deposited:.2f}</code>\n🛒 <b>کل خرچ:</b> <code>{symbol}{spent:.2f}</code>\n🌐 <b>زبان:</b> {language}\n📅 <b>رکنیت کی تاریخ:</b> <code>{date}</code>",
        "support_text": "💬 <b>سپورٹ اور مدد</b>\n\nکسی بھی آرڈر یا ڈپازٹ کے بارے میں مدد کی ضرورت ہے؟\n\n👨‍💻 <b>ایڈمن سپورٹ:</b> {support}\n⚡ <b>دستیاب:</b> 24/7 فوری جواب",
        "language_menu": "🌐 <b>زبان منتخب کریں (Select Language):</b>\n\nموجودہ: <b>{current}</b>",
        "language_changed": "✅ زبان کامیابی سے <b>{name}</b> میں تبدیل کر دی گئی ہے!"
    },

    "fa": {
        # Persian / Iran (فارسی)
        "welcome_title": "به فروشگاه نکسوورا خوش آمدید، {name}!",
        "welcome_sub": "بازار خودکار شما برای محصولات دیجیتال، اشتراک‌ها و خدمات آنی.",
        "balance": "موجودی شما",
        "user_id": "شناسه کاربری شما",
        "choose_option": "برای شروع یکی از گزینه‌های زیر را انتخاب کنید:",
        "btn_shop": "🛍 فروشگاه / محصولات",
        "btn_wallet": "💳 کیف پول من",
        "btn_orders": "📦 سفارش‌های من",
        "btn_profile": "👤 پروفایل من",
        "btn_support": "💬 پشتیبانی و راهنما",
        "btn_language": "🌐 تغییر زبان (Language)",
        "btn_admin": "🛠 پنل مدیریت",
        "btn_back_main": "🔙 منوی اصلی",
        "btn_back": "🔙 بازگشت",
        
        # Promo Offer
        "btn_chatgpt_promo": "🔥 آفر ۳ ماهه چت‌جی‌پی‌تی ({symbol}{price:.2f})",
        "chatgpt_promo_title": "🤖 <b>آفر ویژه ۳ ماهه ChatGPT</b>",
        "chatgpt_promo_desc": "اشتراک ۳ ماهه چت‌جی‌پی‌تی را مستقیماً روی جیمیل / ایمیل شخصی خود فعال کنید.",
        "chatgpt_promo_disabled": "⚠️ آفر ۳ ماهه ChatGPT در حال حاضر غیرفعال می‌باشد.",
        "chatgpt_promo_ask_email": "🤖 <b>فعال‌سازی آفر ۳ ماهه ChatGPT</b>\n\n💵 قیمت: <code>{symbol}{price:.2f}</code>\n\n📧 <b>لطفاً آدرس Gmail / Email خود را ارسال فرمایید:</b>\n<i>(اشتراک ۳ ماهه روی این ایمیل فعال خواهد شد)</i>",
        "chatgpt_promo_invalid_email": "❌ <b>ایمیل نامعتبر است!</b>\n\n⚠️ لطفاً یک ایمیل صحیح وارد فرمایید (مثال: <code>example@gmail.com</code>):",
        "chatgpt_promo_order_submitted": "✅ <b>سفارش آفر ChatGPT ثبت شد!</b>\n\n📦 <b>آفر:</b> <code>ChatGPT 3-Month Promo</code>\n🔖 <b>کد سفارش:</b> <code>{code}</code>\n📧 <b>ایمیل ارسالی:</b> <code>{email}</code>\n💰 <b>مبلغ پرداختی:</b> <code>{symbol}{price:.2f}</code>\n\n⏳ <i>تیم مدیریت در حال فعال‌سازی اشتراک روی ایمیل شما است. پس از انجام یا لغو پیام دریافت خواهید کرد.</i>",
        "chatgpt_promo_activated_user": "🎉 <b>اشتراک ۳ ماهه ChatGPT فعال شد!</b>\n\n🔖 <b>کد سفارش:</b> <code>{code}</code>\n📧 <b>ایمیل:</b> <code>{email}</code>\n\n🎁 <b>کد تبلیغاتی / لینک فعال‌سازی:</b>\n<code>{link}</code>\n\n✨ <i>اشتراک ۳ ماهه چت‌جی‌پی‌تی با موفقیت فعال شد.</i>",
        "chatgpt_promo_refunded_user": "❌ <b>سفارش ChatGPT لغو و مبلغ بازگردانده شد</b>\n\n🔖 <b>کد سفارش:</b> <code>{code}</code>\n💰 <b>مبلغ عودت داده شده:</b> <code>{symbol}{price:.2f}</code>\n\n💡 <i>مبلغ به موجودی کیف پول شما بازگشت داده شد.</i>",

        # Shop / Catalog
        "catalog_title": "کاتالوگ فروشگاه - دسته‌بندی‌ها",
        "catalog_empty": "⚠️ در حال حاضر دسته‌بندی فعالی وجود ندارد. لطفاً بعداً بررسی فرمایید!",
        "select_cat": "برای مشاهده محصولات، دسته‌بندی را انتخاب کنید:",
        "category_empty": "⚠️ محصولی در این دسته‌بندی یافت نشد.",
        "select_product": "برای مشاهده جزئیات و خرید، محصول را انتخاب کنید:",
        "in_stock": "موجود",
        "out_of_stock": "ناموجود",
        "instant_service": "تحویل آنی",
        "available_request": "موجود در صورت درخواست",
        "instant_delivery_info": "⚡ <b>تحویل فوری دیجیتال</b> <i>(کد/اکانت بلافاصله پس از خرید در چت تحویل داده می‌شود)</i>",
        "manual_delivery_info": "🛠 <b>سفارش دستی / خدمات</b> <i>(مدیریت سفارش شما را بررسی و تحویل خواهد داد)</i>",
        "price": "قیمت",
        "product_label": "محصول",
        "category_label": "دسته‌بندی",
        "description_label": "توضیحات",
        "btn_buy_balance": "💳 خرید با موجودی ({symbol}{price:.2f})",
        "btn_buy_crypto": "🪙 فاکتور مستقیم کریپتو ({symbol}{price:.2f})",
        "btn_back_products": "🔙 بازگشت به محصولات",
        "btn_back_categories": "🔙 بازگشت به دسته‌ها",
        
        "insufficient_balance": "❌ <b>موجودی ناکافی است</b>\n\nمبلغ مورد نیاز: <code>{symbol}{price:.2f}</code>\nموجودی شما: <code>{symbol}{balance:.2f}</code>\nشما به <code>{symbol}{shortage:.2f}</code> دیگر نیاز دارید.\n\n👇 برای شارژ حساب دکمه زیر را بزنید!",
        "btn_deposit_now": "📥 افزایش موجودی",
        "purchase_success": "🎉 <b>خرید با موفقیت انجام شد!</b>\n\n📦 <b>محصول:</b> <code>{name}</code>\n🔖 <b>کد سفارش:</b> <code>{code}</code>\n💰 <b>مبلغ پرداختی:</b> <code>{symbol}{price:.2f}</code>\n\n🔑 <b>کد / اکانت تحویلی:</b>\n<pre>{item}</pre>\n\n💡 <i>می‌توانید این اطلاعات را همیشه در 'سفارش‌های من' مشاهده فرمایید.</i>",
        "btn_continue_shopping": "🛍 ادامه خرید",
        "manual_prompt": "📝 <b>سفارش خدمات دستی: {name}</b>\n\nقیمت: <code>{symbol}{price:.2f}</code>\n\nلطفاً جزئیات مورد نیاز سفارش خود (مانند ایمیل، نام کاربری یا مشخصات) را ارسال فرمایید:",
        "manual_submitted": "✅ <b>سفارش با موفقیت ثبت شد!</b>\n\n📦 <b>محصول:</b> <code>{name}</code>\n🔖 <b>کد سفارش:</b> <code>{code}</code>\n💰 <b>مبلغ پرداختی:</b> <code>{symbol}{price:.2f}</code>\n📝 <b>اطلاعات ارسالی شما:</b>\n<code>{details}</code>\n\n⏳ <i>تیم ما سفارش شما را دریافت کرده و در حال پردازش است. پس از تکمیل پیام دریافت خواهید کرد.</i>",

        "wallet_title": "💳 <b>کیف پول و موجودی</b>\n\n💰 <b>موجودی فعلی:</b> <code>{symbol}{balance:.2f} {currency}</code>\n📥 <b>مجموع واریزی:</b> <code>{symbol}{deposited:.2f}</code>\n🛒 <b>مجموع خرید:</b> <code>{symbol}{spent:.2f}</code>\n\n⚡ <i>روش‌های واریز: کریپتو (خودکار)، پرداخت دستی و کارت به کارت.</i>",
        "btn_deposit": "📥 افزایش موجودی (واریز)",
        "deposit_select_method": "📥 <b>انتخاب روش پرداخت / واریز</b>\n\nروش مورد نظر خود برای شارژ حساب را انتخاب فرمایید:",
        "btn_crypto_gateway": "🪙 تتر / کریپتو (تأیید آنی خودکار)",
        "deposit_menu": "📥 <b>شارژ حساب با تتر (USDT Multi-Chain)</b>\n\n🪙 <b>شبکه‌های پشتیبانی‌شده:</b>\n• <b>USDT - BEP20</b> (شبکه BSC)\n• <b>USDT - TRC20</b> (شبکه ترون)\n• <b>USDT - ERC20</b> (شبکه اتریوم)\n\n📌 <i>حداقل مبلغ واریز:</i> <code>{symbol}{min_dep:.2f}</code>\n\nیک مبلغ را انتخاب کنید یا مبلغ دلخواه وارد نمایید:",
        "btn_custom_amount": "✏️ مبلغ دلخواه",
        "custom_amount_prompt": "✏️ <b>ورود مبلغ دلخواه</b>\n\nلطفاً مبلغ مورد نظر به USDT را ارسال کنید (حداقل <code>{symbol}{min_dep:.2f}</code>):\n<i>(مثال: <code>15</code> یا <code>35.50</code>)</i>",
        "invalid_amount_min": "❌ <b>مبلغ نامعتبر است!</b>\n\n⚠️ شما مبلغ <code>{symbol}{amount:.2f}</code> را وارد کردید، اما حداقل واریزی <code>{symbol}{min_dep:.2f}</code> می‌باشد.\n\n👉 لطفاً <code>{min_dep:.2f}</code> یا بیشتر وارد نمایید (مثال: <code>10</code> یا <code>25.50</code>):",
        "invalid_amount_number": "❌ <b>ورودی نامعتبر!</b>\n\n⚠️ استفاده از حروف مجاز نیست.\n👉 لطفاً فقط عدد انگلیسی وارد نمایید (مثال: <code>10</code>, <code>20</code> یا <code>50</code>):",
        "invoice_title": "🪙 <b>فاکتور پرداخت صادر شد</b>\n\n🔖 <b>شناسه فاکتور:</b> <code>{code}</code>\n💵 <b>مبلغ:</b> <code>{symbol}{amount:.2f} USDT</code>\n⏳ <b>وضعیت:</b> <code>در انتظار پرداخت (INITIAL)</code>\n\n━━━━━━━━━━━━━━━━━━━━\n🌐 <b>آدرس‌های انتقال USDT:</b>\nدقیقاً مبلغ <code>{amount:.2f} USDT</code> را به یکی از آدرس‌های زیر انتقال دهید:\n\n🟡 <b>BEP20 (BNB Smart Chain):</b>\n<code>{bep20}</code>\n\n🔴 <b>TRC20 (TRON Network):</b>\n<code>{trc20}</code>\n\n🔵 <b>ERC20 (Ethereum):</b>\n<code>{erc20}</code>\n━━━━━━━━━━━━━━━━━━━━\n💡 <i>پس از انتقال، روی 'بررسی وضعیت پرداخت' کلیک کنید یا کد TxHash خود را ثبت نمایید.</i>",
        "btn_check_status": "🔄 بررسی وضعیت پرداخت",
        "btn_submit_tx": "⚡ ثبت هش تراکنش (TxHash)",
        "deposit_confirmed": "🎉 <b>واریزی تأیید و شارژ شد!</b>\n\n🔖 <b>شناسه فاکتور:</b> <code>{code}</code>\n💰 <b>مبلغ اضافه شده:</b> <code>{symbol}{amount:.2f} USDT</code>\n🌐 <b>شبکه:</b> <code>{network}</code>\n\n✨ <i>موجودی شما با موفقیت به‌روزرسانی شد. خرید خوبی داشته باشید!</i>",
        "deposit_already_credited": "✅ این واریزی قبلاً به کیف پول شما واریز شده است!",
        "deposit_pending": "⏳ تراکنش هنوز روی بلاک‌چین تأیید نشده است. لطفاً ۱ الی ۲ دقیقه دیگر مجدداً بررسی فرمایید.",
        
        "manual_dep_info": "📱 <b>راهنمای پرداخت دستی ({name})</b>\n\n📌 <b>مشخصات حساب:</b>\n<code>{details}</code>\n\n📝 <b>توضیحات:</b> {instructions}\n💵 <b>نرخ ارز:</b> <code>$1.00 = {rate:.2f}</code>\n📌 <b>حداقل واریز:</b> <code>{symbol}{min_dep:.2f}</code>\n\n👉 <i>پس از انتقال، دکمه زیر را برای ارسال مشخصات واریز فشار دهید:</i>",
        "btn_submit_manual_dep": "📝 ثبت مشخصات پرداخت",
        "manual_dep_ask_amount": "💵 <b>مبلغ واریزی را وارد فرمایید:</b>\n\nلطفاً مبلغ پرداختی را ارسال نمایید:",
        "manual_dep_ask_sender": "📱 <b>شماره فرستنده را وارد فرمایید:</b>\n\nشماره حسابی که با آن پرداخت کردید را ارسال فرمایید:",
        "manual_dep_ask_trxid": "🔖 <b>کد رهگیری / شناسه پرداخت را وارد فرمایید:</b>\n\nکد پیگیری تراکنش را ارسال کنید:",
        "manual_dep_submitted": "✅ <b>درخواست افزایش موجودی با موفقیت ثبت شد!</b>\n\n🔖 <b>شناسه:</b> <code>{code}</code>\n💳 <b>روش:</b> <code>{method}</code>\n💵 <b>مبلغ:</b> <code>{symbol}{amount:.2f}</code>\n\n⏳ <i>تیم مدیریت در حال بررسی تراکنش شما است. پس از تأیید حساب شما شارژ خواهد شد.</i>",
        "deposit_approved_user": "🎉 <b>واریزی تأیید و موجودی شارژ شد!</b>\n\n🔖 <b>شناسه:</b> <code>{code}</code>\n💰 <b>مبلغ:</b> <code>{symbol}{amount:.2f}</code>\n💳 <b>روش:</b> <code>{method}</code>\n\n✨ <i>موجودی شما با موفقیت افزایش یافت!</i>",
        "deposit_rejected_user": "❌ <b>درخواست واریز رد شد</b>\n\n🔖 <b>شناسه:</b> <code>{code}</code>\n💳 <b>روش:</b> <code>{method}</code>\n\n⚠️ <i>تراکنش با مشخصات وارد شده تأیید نگردید.</i>",

        "submit_tx_select_net": "⚡ <b>ثبت TxHash برای تأیید تراکنش</b>\n\n🔖 شناسه فاکتور: <code>{code}</code>\n\n👇 لطفاً شبکه‌ای که با آن پرداخت کردید را انتخاب کنید:",
        "submit_tx_prompt": "⚡ <b>ارسال TxHash ({network})</b>\n\n🔖 فاکتور: <code>{code}</code>\n🌐 شبکه: <code>{network}</code>\n\n📌 <b>نحوه دریافت کد TxHash:</b>\n۱. برنامه بایننس یا کیف پول خود را باز کرده و به بخش <b>Withdrawal History</b> بروید.\n۲. روی تراکنش کلیک کرده و <b>TxID / TxHash</b> (کد ۶۴ یا ۶۶ کاراکتری) را کپی کنید.\n۳. کد کپی شده را اینجا ارسال فرمایید.\n\n💡 <i>(مثال: <code>0x78ab9c456...</code>)</i>",
        "fake_tx_hash_warn": "❌ <b>هش تراکنش نامعتبر یا جعلی (TxHash)!</b>\n\n⚠️ متنی که ارسال فرمودید: <code>{hash}</code> یک هش معتبر بلاک‌چین نمی‌باشد.\n\n📌 <b>یافتن کد صحیح:</b>\n• به بخش تاریخچه برداشت کیف پول خود بروید.\n• کد <b>TxID</b> تراکنش را کپی کرده و ارسال نمایید.\n\n👉 لطفاً کد صحیح ۶۴ یا ۶۶ رقمی را ارسال فرمایید:",
        "tx_submitted_success": "✅ <b>هش تراکنش با موفقیت ثبت شد!</b>\n\n🔖 <b>فاکتور:</b> <code>{code}</code>\n🌐 <b>شبکه:</b> <code>{network}</code>\n🔗 <b>TxHash:</b> <code>{hash}</code>\n\n⏳ <i>سیستم در حال بررسی تراکنش است. به محض تأیید شبکه، حساب شما شارژ خواهد شد.</i>",
        "tx_verification_failed": "⚠️ <b>تأیید تراکنش ناموفق بود!</b>\n\n❌ <b>دلیل:</b> <i>{reason}</i>\n\n💡 <b>راهنمایی:</b>\n۱. اگر به تازگی انتقال داده‌اید، تأیید بلاک‌چین ممکن است ۱ تا ۲ دقیقه طول بکشد.\n۲. از ارسال به آدرس و شبکه صحیح اطمینان حاصل نمایید.\n۳. کمی بعد دکمه 'بررسی وضعیت پرداخت' را بزنید.",

        "orders_title": "📦 <b>سفارش‌های اخیر شما:</b>\n\n",
        "orders_empty": "📦 <b>سفارش‌های من</b>\n\n⚠️ هنوز خریدی انجام نداده‌اید.",
        "profile_title": "👤 <b>پروفایل کاربری</b>\n\n🆔 <b>شناسه کاربری:</b> <code>{id}</code>\n👤 <b>نام:</b> {name}\n🏷 <b>نام کاربری:</b> @{username}\n💰 <b>موجودی کیف پول:</b> <code>{symbol}{balance:.2f}</code>\n📥 <b>مجموع واریزها:</b> <code>{symbol}{deposited:.2f}</code>\n🛒 <b>مجموع خریدها:</b> <code>{symbol}{spent:.2f}</code>\n🌐 <b>زبان:</b> {language}\n📅 <b>عضویت از تاریخ:</b> <code>{date}</code>",
        "support_text": "💬 <b>پشتیبانی و راهنمایی</b>\n\nبه راهنمایی درباره سفارش یا واریزی نیاز دارید؟\n\n👨‍💻 <b>پشتیبانی مستقیم:</b> {support}\n⚡ <b>پاسخگویی:</b> ۲۴ ساعته و سریع",
        "language_menu": "🌐 <b>انتخاب زبان (Select Language):</b>\n\nزبان فعلی: <b>{current}</b>",
        "language_changed": "✅ زبان با موفقیت به <b>{name}</b> تغییر یافت!"
    },

    "ar": {
        # Arabic / Palestine (العربية / فلسطين)
        "welcome_title": "أهلاً بك في متجر نكسفورا، {name}! 🇵🇸",
        "welcome_sub": "سوقك المؤتمت الرائد للمنتجات الرقمية، الاشتراكات والخدمات الفورية.",
        "balance": "رصيدك الحالي",
        "user_id": "معرف المستخدم الخاص بك",
        "choose_option": "اختر من الخيارات أدناه للبدء:",
        "btn_shop": "🛍 المتجر / المنتجات",
        "btn_wallet": "💳 محفظتي",
        "btn_orders": "📦 طلباتي",
        "btn_profile": "👤 حسابي",
        "btn_support": "💬 الدعم والمساعدة",
        "btn_language": "🌐 تغيير اللغة",
        "btn_admin": "🛠 لوحة التحكم",
        "btn_back_main": "🔙 القائمة الرئيسية",
        "btn_back": "🔙 رجوع",
        
        # Promo Offer
        "btn_chatgpt_promo": "🔥 عرض ChatGPT لـ 3 أشهر ({symbol}{price:.2f})",
        "chatgpt_promo_title": "🤖 <b>عرض اشتراك ChatGPT لمدة 3 أشهر</b>",
        "chatgpt_promo_desc": "احصل على اشتراك ChatGPT لمدة 3 أشهر يتم تفعيله مباشرة على بريدك الإلكتروني الشخصي (Gmail).",
        "chatgpt_promo_disabled": "⚠️ عرض ChatGPT لمدة 3 أشهر غير متوفر حالياً. يرجى التحقق لاحقاً!",
        "chatgpt_promo_ask_email": "🤖 <b>تفعيل عرض ChatGPT لمدة 3 أشهر</b>\n\n💵 السعر: <code>{symbol}{price:.2f}</code>\n\n📧 <b>يرجى إرسال بريدك الإلكتروني (Gmail / Email):</b>\n<i>(سيتم تفعيل الاشتراك لمدة 3 أشهر على هذا البريد)</i>",
        "chatgpt_promo_invalid_email": "❌ <b>بريد إلكتروني غير صالح!</b>\n\n⚠️ يرجى إدخال بريد إلكتروني صحيح (مثال: <code>example@gmail.com</code>):",
        "chatgpt_promo_order_submitted": "✅ <b>تم إرسال طلب عرض ChatGPT بنجاح!</b>\n\n📦 <b>العرض:</b> <code>ChatGPT 3-Month Promo</code>\n🔖 <b>رقم الطلب:</b> <code>{code}</code>\n📧 <b>البريد:</b> <code>{email}</code>\n💰 <b>المبلغ المدفوع:</b> <code>{symbol}{price:.2f}</code>\n\n⏳ <i>فريق الإدارة يقوم بتفعيل الاشتراك على بريدك الإلكتروني. ستصلك رسالة فور التفعيل (أو استرجاع المبلغ تلقائياً في حال الإلغاء).</i>",
        "chatgpt_promo_activated_user": "🎉 <b>تم تفعيل اشتراك ChatGPT لمدة 3 أشهر!</b>\n\n🔖 <b>رقم الطلب:</b> <code>{code}</code>\n📧 <b>البريد:</b> <code>{email}</code>\n\n🎁 <b>كود الخصم / رابط التفعيل:</b>\n<code>{link}</code>\n\n✨ <i>تم تفعيل اشتراكك بنجاح من قبل المسؤول. استمتع بالخدمة!</i>",
        "chatgpt_promo_refunded_user": "❌ <b>تم إلغاء طلب ChatGPT واسترجاع المبلغ</b>\n\n🔖 <b>رقم الطلب:</b> <code>{code}</code>\n💰 <b>المبلغ المسترجع:</b> <code>{symbol}{price:.2f}</code>\n\n💡 <i>تمت إعادة كامل المبلغ إلى رصيد محفظتك.</i>",

        # Shop / Catalog
        "catalog_title": "كتالوج المتجر - الأقسام",
        "catalog_empty": "⚠️ لا توجد أقسام متاحة حالياً. يرجى التحقق لاحقاً!",
        "select_cat": "اختر قسماً لتصفح المنتجات:",
        "category_empty": "⚠️ لا توجد منتجات متوفرة في هذا القسم حالياً.",
        "select_product": "اختر منتجاً لعرض التفاصيل والشراء:",
        "in_stock": "متوفر",
        "out_of_stock": "نفد من المخزون",
        "instant_service": "خدمة فورية",
        "available_request": "متوفر عند الطلب",
        "instant_delivery_info": "⚡ <b>تسليم رقمي فوري</b> <i>(سيتم تسليم الكود/الحساب في الدردشة مباشرة بعد الشراء)</i>",
        "manual_delivery_info": "🛠 <b>خدمة / طلب يدوي</b> <i>(سيقوم المسؤول بمعالجة الطلب وتسليمه)</i>",
        "price": "السعر",
        "product_label": "المنتج",
        "category_label": "القسم",
        "description_label": "الوصف",
        "btn_buy_balance": "💳 شراء من الرصيد ({symbol}{price:.2f})",
        "btn_buy_crypto": "🪙 فاتورة كريبتو مباشرة ({symbol}{price:.2f})",
        "btn_back_products": "🔙 العودة للمنتجات",
        "btn_back_categories": "🔙 العودة للأقسام",
        
        "insufficient_balance": "❌ <b>رصيدك غير كافٍ</b>\n\nالمطلوب: <code>{symbol}{price:.2f}</code>\nرصيدك: <code>{symbol}{balance:.2f}</code>\nأنت بحاجة إلى <code>{symbol}{shortage:.2f}</code> إضافية.\n\n👇 اضغط أدناه لشحن رصيدك عبر العملات الرقمية أو الطرق المحلية!",
        "btn_deposit_now": "📥 شحن الرصيد الآن",
        "purchase_success": "🎉 <b>تم الشراء بنجاح!</b>\n\n📦 <b>المنتج:</b> <code>{name}</code>\n🔖 <b>رقم الطلب:</b> <code>{code}</code>\n💰 <b>المبلغ المدفوع:</b> <code>{symbol}{price:.2f}</code>\n\n🔑 <b>البيانات / الكود المستلم:</b>\n<pre>{item}</pre>\n\n💡 <i>يمكنك مراجعة تفاصيل هذا الطلب دائماً في 'طلباتي'.</i>",
        "btn_continue_shopping": "🛍 متابعة التسوق",
        "manual_prompt": "📝 <b>طلب خدمة يدوية: {name}</b>\n\nالسعر: <code>{symbol}{price:.2f}</code>\n\nيرجى إرسال التفاصيل المطلوبة لتنفيذ طلبك (مثل البريد الإلكتروني أو اسم المستخدم):",
        "manual_submitted": "✅ <b>تم إرسال الطلب بنجاح!</b>\n\n📦 <b>المنتج:</b> <code>{name}</code>\n🔖 <b>رقم الطلب:</b> <code>{code}</code>\n💰 <b>المبلغ المدفوع:</b> <code>{symbol}{price:.2f}</code>\n📝 <b>بياناتك المرسلة:</b>\n<code>{details}</code>\n\n⏳ <i>فريقنا استلم طلبك وجاري معالجته. سيتم إشعارك هنا فور الانتهاء.</i>",

        # Wallet & Deposit Gateways
        "wallet_title": "💳 <b>محفظتي والرصيد</b>\n\n💰 <b>الرصيد الحالي:</b> <code>{symbol}{balance:.2f} {currency}</code>\n📥 <b>إجمالي الإيداعات:</b> <code>{symbol}{deposited:.2f}</code>\n🛒 <b>إجمالي المشتريات:</b> <code>{symbol}{spent:.2f}</code>\n\n⚡ <i>طرق الإيداع: كريبتو (تلقائي)، بوابات الدفع اليدوية.</i>",
        "btn_deposit": "📥 شحن الرصيد",
        "deposit_select_method": "📥 <b>اختر طريقة الدفع / الإيداع</b>\n\nاختر وسيلة الدفع المناسبة لشحن رصيدك:",
        "btn_crypto_gateway": "🪙 تيذر / كريبتو (تأكيد فوري تلقائي)",
        "deposit_menu": "📥 <b>إيداع الكريبتو (USDT Multi-Chain)</b>\n\n🪙 <b>الشبكات المدعومة:</b>\n• <b>USDT - BEP20</b> (شبكة BSC)\n• <b>USDT - TRC20</b> (شبكة TRON)\n• <b>USDT - ERC20</b> (شبكة Ethereum)\n\n📌 <i>الحد الأدنى للإيداع:</i> <code>{symbol}{min_dep:.2f}</code>\n\nاختر مبلغاً محدداً أو أدخل مبلغاً مخصصاً:",
        "btn_custom_amount": "✏️ مبلغ مخصص",
        "custom_amount_prompt": "✏️ <b>أدخل مبلغ الإيداع</b>\n\nيرجى إرسال المبلغ بـ USDT (الحد الأدنى <code>{symbol}{min_dep:.2f}</code>):\n<i>(مثال: <code>15</code> أو <code>35.50</code>)</i>",
        "invalid_amount_min": "❌ <b>المبلغ غير صالح!</b>\n\n⚠️ لقد أدخلت <code>{symbol}{amount:.2f}</code>، ولكن الحد الأدنى للإيداع هو <code>{symbol}{min_dep:.2f}</code>.\n\n👉 يرجى إدخال <code>{min_dep:.2f}</code> أو أكثر (مثال: <code>10</code> أو <code>25.50</code>):",
        "invalid_amount_number": "❌ <b>إدخال غير صحيح!</b>\n\n⚠️ لا يسمح باستخدام الحروف أو الرموز.\n👉 يرجى كتابة أرقام إنجليزية فقط (مثال: <code>10</code> أو <code>20</code> أو <code>50</code>):",
        
        # Crypto Invoice
        "invoice_title": "🪙 <b>تم إنشاء فاتورة الدفع</b>\n\n🔖 <b>رقم الفاتورة:</b> <code>{code}</code>\n💵 <b>المبلغ:</b> <code>{symbol}{amount:.2f} USDT</code>\n⏳ <b>الحالة:</b> <code>بانتظار الدفع (INITIAL)</code>\n\n━━━━━━━━━━━━━━━━━━━━\n🌐 <b>عناوين تحويل USDT عبر الشبكات:</b>\nأرسل بالضبط <code>{amount:.2f} USDT</code> إلى أحد العناوين التالية:\n\n🟡 <b>BEP20 (BNB Smart Chain):</b>\n<code>{bep20}</code>\n\n🔴 <b>TRC20 (TRON Network):</b>\n<code>{trc20}</code>\n\n🔵 <b>ERC20 (Ethereum):</b>\n<code>{erc20}</code>\n━━━━━━━━━━━━━━━━━━━━\n💡 <i>بعد التحويل، اضغط على 'التحقق من حالة الدفع' أو أرسل كود TxHash.</i>",
        "btn_check_status": "🔄 التحقق من حالة الدفع",
        "btn_submit_tx": "⚡ إرسال هاش المعاملة (TxHash)",
        "deposit_confirmed": "🎉 <b>تم تأكيد الإيداع وإضافة الرصيد!</b>\n\n🔖 <b>رقم الفاتورة:</b> <code>{code}</code>\n💰 <b>المبلغ المضاف:</b> <code>{symbol}{amount:.2f} USDT</code>\n🌐 <b>الشبكة:</b> <code>{network}</code>\n\n✨ <i>تم تحديث رصيدك بنجاح. تسوق ممتع!</i>",
        "deposit_already_credited": "✅ تم التحقق من هذا الإيداع وإضافته إلى محفظتك مسبقاً!",
        "deposit_pending": "⏳ لم يتم رصد المعاملة بعد على البلوك تشين. يرجى الانتظار 1-2 دقيقة ثم إعادة التحقق.",
        
        # Manual Deposit Flow
        "manual_dep_info": "📱 <b>تعليمات الإيداع اليدوي ({name})</b>\n\n📌 <b>بيانات الحساب:</b>\n<code>{details}</code>\n\n📝 <b>التعليمات:</b> {instructions}\n💵 <b>سعر الصرف:</b> <code>$1.00 = {rate:.2f}</code>\n📌 <b>الحد الأدنى:</b> <code>{symbol}{min_dep:.2f}</code>\n\n👉 <i>بعد التحويل، اضغط على الزر أدناه لإرسال تفاصيل الدفع للتأكيد:</i>",
        "btn_submit_manual_dep": "📝 إرسال تفاصيل الدفع",
        "manual_dep_ask_amount": "💵 <b>أدخل المبلغ المدفوع:</b>\n\nيرجى إرسال المبلغ:",
        "manual_dep_ask_sender": "📱 <b>أدخل رقم الهاتف المحول منه:</b>\n\nيرجى كتابة رقم الحساب / الهاتف الذي تم التحويل منه:",
        "manual_dep_ask_trxid": "🔖 <b>أدخل رقم المعاملة (TrxID):</b>\n\nيرجى كتابة رقم الحوالة / TrxID:",
        "manual_dep_submitted": "✅ <b>تم استلام طلب الإيداع بنجاح!</b>\n\n🔖 <b>رقم الإيداع:</b> <code>{code}</code>\n💳 <b>الطريقة:</b> <code>{method}</code>\n💵 <b>المبلغ:</b> <code>{symbol}{amount:.2f}</code>\n\n⏳ <i>جاري التحقق من عملية الدفع من قبل الإدارة وسيتم إضافة الرصيد فوراً.</i>",
        "deposit_approved_user": "🎉 <b>تم تأكيد الإيداع وإضافة الرصيد إلى محفظتك!</b>\n\n🔖 <b>رقم الإيداع:</b> <code>{code}</code>\n💰 <b>المبلغ المضاف:</b> <code>{symbol}{amount:.2f}</code>\n💳 <b>الطريقة:</b> <code>{method}</code>\n\n✨ <i>تم تحديث رصيدك بنجاح!</i>",
        "deposit_rejected_user": "❌ <b>تم رفض طلب الإيداع</b>\n\n🔖 <b>رقم الإيداع:</b> <code>{code}</code>\n💳 <b>الطريقة:</b> <code>{method}</code>\n\n⚠️ <i>لم يتم العثور على حوالة مطابقة للبيانات المدخلة.</i>",

        "submit_tx_select_net": "⚡ <b>التحقق من هاش المعاملة (TxHash)</b>\n\n🔖 رقم الفاتورة: <code>{code}</code>\n\n👇 اختر شبكة البلوك تشين التي قمت بالتحويل من خلالها:",
        "submit_tx_prompt": "⚡ <b>أرسل كود TxHash ({network})</b>\n\n🔖 الفاتورة: <code>{code}</code>\n🌐 الشبكة: <code>{network}</code>\n\n📌 <b>كيفية الحصول على كود TxHash الصحيح:</b>\n1. افتح تطبيق بايننس أو محفظتك وانتقل إلى <b>سجل السحب (Withdrawal History)</b>.\n2. اضغط على المعاملة وانسخ <b>TxID / TxHash</b> (رمز بطول 64 أو 66 حرفاً).\n3. أرسل الرمز المنسوخ هنا.\n\n💡 <i>(مثال: <code>0x78ab9c456...</code>)</i>",
        "fake_tx_hash_warn": "❌ <b>هاش معاملة غير صحيح أو مزيف (TxHash)!</b>\n\n⚠️ النص الذي أرسلته: <code>{hash}</code> ليس كود معاملة بلوك تشين صالح.\n\n📌 <b>كيف تجد الهاش الصحيح:</b>\n• انتقل إلى سجل التحويلات في محفظتك أو بايننس.\n• انسخ كود <b>TxID</b> الحقيقي الخاص بعملية التحويل.\n\n👉 يرجى إعادة إرسال كود TxHash الصحيح المكون من 64/66 حرفاً:",
        "tx_submitted_success": "✅ <b>تم إرسال كود TxHash بنجاح!</b>\n\n🔖 <b>الفاتورة:</b> <code>{code}</code>\n🌐 <b>الشبكة:</b> <code>{network}</code>\n🔗 <b>TxHash:</b> <code>{hash}</code>\n\n⏳ <i>النظام يتحقق من تأكيدات البلوك تشين. ستتم إضافة الرصيد تلقائياً بمجرد التأكيد.</i>",
        "tx_verification_failed": "⚠️ <b>فشل التحقق من المعاملة!</b>\n\n❌ <b>السبب:</b> <i>{reason}</i>\n\n💡 <b>نصائح:</b>\n1. إذا قمت بالتحويل للتو، قد يستغرق تأكيد الشبكة 1-2 دقيقة.\n2. تأكد من أنك أرسلت المبلغ المطلوب على الشبكة المحددة.\n3. اضغط على 'التحقق من حالة الدفع' بعد قليل.",

        "orders_title": "📦 <b>طلباتك الأخيرة:</b>\n\n",
        "orders_empty": "📦 <b>طلباتي</b>\n\n⚠️ لم تقم بأي عملية شراء حتى الآن.",
        "profile_title": "👤 <b>الملف الشخصي</b>\n\n🆔 <b>معرف تيليجرام:</b> <code>{id}</code>\n👤 <b>الاسم:</b> {name}\n🏷 <b>اسم المستخدم:</b> @{username}\n💰 <b>رصيد المحفظة:</b> <code>{symbol}{balance:.2f}</code>\n📥 <b>إجمالي الإيداعات:</b> <code>{symbol}{deposited:.2f}</code>\n🛒 <b>إجمالي المشتريات:</b> <code>{symbol}{spent:.2f}</code>\n🌐 <b>اللغة:</b> {language}\n📅 <b>عضو منذ:</b> <code>{date}</code>",
        "support_text": "💬 <b>الدعم والمساعدة</b>\n\nهل تحتاج إلى مساعدة بخصوص طلب أو إيداع؟\n\n👨‍💻 <b>الدعم المباشر:</b> {support}\n⚡ <b>متاح:</b> 24/7 رد سريع",
        "language_menu": "🌐 <b>اختر لغتك (Select Language):</b>\n\nالحالية: <b>{current}</b>",
        "language_changed": "✅ تم تغيير اللغة إلى <b>{name}</b> بنجاح!"
    }
}

def t(key: str, lang: str = "en", **kwargs) -> str:
    """
    Returns the localized string for the given key and language.
    Falls back to English if key or language is not found.
    """
    lang_dict = STRINGS.get(lang, STRINGS["en"])
    template = lang_dict.get(key, STRINGS["en"].get(key, key))
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template
