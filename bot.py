import os
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice

# ==================== الكود رقم (26) - النسخة العالمية المحدثة ====================
# قراءة توكن البوت من متغيرات البيئة في Railway مع وجود التوكن الاحتياطي
TOKEN = os.getenv("BOT_TOKEN", "9015540423:AAF1I4ZPdzybeoE4LjCyobw-kg86mgjRmDo")
bot = telebot.TeleBot(TOKEN)

# الآيدي الخاص بك كإدارة
ADMIN_ID = 7004113433

# المتغيرات الأساسية
current_ad_photo = None
user_waiting_for_receipt = {}
admin_waiting_for_amount = {}
user_balances = {}  # يحفظ أرصدة المستخدمين
user_waiting_for_ad_details = {}
user_temp_ad_data = {}

# نظام التقييمات التفاعلي (يبدأ بالأساسيات: 53 إيجابي، 11 سلبي، والمجموع 64)[span_0](start_span)[span_0](end_span)
ratings_data = {"positive": 53, "negative": 11, "voted_users": set()}

# قائمة المجلدات الديناميكية مع روابطها
dynamic_folders = {
    "folder_1": {
        "name": "📁 المجلد الأول",
        "link": "https://t.me/addlist/iGXVLJMZZx0yNWZk",
    },
    "folder_2": {
        "name": "📁 المجلد الثاني",
        "link": "https://t.me/addlist/default2",
    },
    "folder_3": {
        "name": "📁 المجلد الثالث",
        "link": "https://t.me/addlist/default3",
    },
}


# ==================== الأزرار الرئيسية ====================
def get_main_menu():
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton("شحن البوت 💎", callback_data="recharge_bot"),
      InlineKeyboardButton("رصيد البوت 💰", callback_data="bot_balance"),
  )
  keyboard.row(
      InlineKeyboardButton("اعلان قناتك الآن 📢", callback_data="advertise_channel"),
      InlineKeyboardButton(
          "شاهد كيفية إعلانك 📢", callback_data="how_to_advertise"
      ),
  )

  folder_buttons = [
      InlineKeyboardButton(data["name"], callback_data=key)
      for key, data in dynamic_folders.items()
  ]
  for i in range(0, len(folder_buttons), 2):
    keyboard.row(*folder_buttons[i : i + 2])

  keyboard.row(
      InlineKeyboardButton("تقييم المستخدمين ⭐", callback_data="user_ratings"),
      InlineKeyboardButton(
          "شاهد إعلانات تم إنجازها 💻", callback_data="completed_ads"
      ),
  )
  keyboard.row(
      InlineKeyboardButton("زر إضافي / تواصل 🔄", callback_data="extra_contact")
  )
  return keyboard


def get_sub_menu_with_payment():
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton("دفع عبر عملات رقمية 🪙", callback_data="pay_crypto"),
      InlineKeyboardButton("دفع عبر نجوم ⭐", callback_data="pay_stars"),
  )
  keyboard.row(
      InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main")
  )
  return keyboard


def get_ratings_menu(has_voted=False):
  keyboard = InlineKeyboardMarkup()
  if not has_voted:
    keyboard.row(
        InlineKeyboardButton("👍 تقييم إيجابي", callback_data="rate_positive"),
        InlineKeyboardButton("👎 تقييم سلبي", callback_data="rate_negative"),
    )
  keyboard.row(
      InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main")
  )
  return keyboard


def get_stars_packages_menu():
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton(
          "🌟 500 نجمة = 9.99 دولار", callback_data="star_pkg_500"
      )
  )
  keyboard.row(
      InlineKeyboardButton(
          "🔥 1,500 نجمة = 29.99 دولاراً", callback_data="star_pkg_1500"
      )
  )
  keyboard.row(
      InlineKeyboardButton(
          "🚀 2,500 نجمة = 50.90 دولاراً", callback_data="star_pkg_2500"
      )
  )
  keyboard.row(
      InlineKeyboardButton(
          "👑 5,000 نجمة = 101.80 دولاراً", callback_data="star_pkg_5000"
      )
  )
  keyboard.row(
      InlineKeyboardButton(
          "💎 10,000 نجمة = 203.60 دولاراً", callback_data="star_pkg_10000"
      )
  )
  keyboard.row(
      InlineKeyboardButton(
          "🔙 رجوع إلى طرق الدفع", callback_data="recharge_bot"
      )
  )
  return keyboard


def get_crypto_action_menu():
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton("أرسل الوصل 📤", callback_data="send_receipt"),
      InlineKeyboardButton("تأكيد ✅", callback_data="confirm_payment"),
  )
  keyboard.row(
      InlineKeyboardButton(
          "🔙 رجوع إلى طرق الدفع", callback_data="recharge_bot"
      )
  )
  return keyboard


def get_star_payment_menu(stars_amount):
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton(
          f"⭐ ادفع {stars_amount} نجمة الآن",
          callback_data=f"pay_stars_now_{stars_amount}",
      )
  )
  keyboard.row(
      InlineKeyboardButton(
          "🔙 رجوع إلى باقات النجوم", callback_data="pay_stars"
      )
  )
  return keyboard


def get_back_to_main_menu_only():
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main")
  )
  return keyboard


def get_folders_selection_menu():
  keyboard = InlineKeyboardMarkup()
  folder_buttons = [
      InlineKeyboardButton(data["name"], callback_data=f"select_{key}")
      for key, data in dynamic_folders.items()
  ]
  for i in range(0, len(folder_buttons), 2):
    keyboard.row(*folder_buttons[i : i + 2])

  keyboard.row(
      InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main")
  )
  return keyboard


def get_ad_duration_menu():
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton(
          "⏳ إعلان لمدة 10 ساعات — 5$", callback_data="duration_10h"
      )
  )
  keyboard.row(
      InlineKeyboardButton(
          "⌛ إعلان لمدة 24 ساعة — 12$", callback_data="duration_24h"
      )
  )
  keyboard.row(
      InlineKeyboardButton(
          "🚀 إعلان لمدة 48 ساعة — 24$", callback_data="duration_48h"
      )
  )
  keyboard.row(
      InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main")
  )
  return keyboard


def get_confirm_deduct_menu(duration_type):
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton(
          "تأكيد ✅", callback_data=f"confirm_deduct_{duration_type}"
      ),
      InlineKeyboardButton("إلغاء ❌", callback_data="back_to_main"),
  )
  return keyboard


def get_recharge_direct_menu():
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton(
          "💎 شحن رصيد البوت الآن", callback_data="recharge_bot"
      )
  )
  keyboard.row(
      InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main")
  )
  return keyboard


def get_admin_ad_review_menu(user_id):
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton(
          "تأكيد الطلب وقبوله ✅", callback_data=f"accept_ad_{user_id}"
      ),
      InlineKeyboardButton(
          "إلغاء ورفض الطلب ❌", callback_data=f"reject_ad_{user_id}"
      ),
  )
  return keyboard


def get_admin_action_menu(user_id):
  keyboard = InlineKeyboardMarkup()
  keyboard.row(
      InlineKeyboardButton(
          "إلغاء ❌", callback_data=f"admin_cancel_{user_id}"
      ),
      InlineKeyboardButton(
          "تأكيد الشحن ✅", callback_data=f"admin_approve_{user_id}"
      ),
  )
  return keyboard


# ==================== أوامر البوت ====================
@bot.message_handler(commands=["start"])
def send_welcome(message):
  chat_id = message.chat.id
  user_waiting_for_receipt[chat_id] = False
  user_waiting_for_ad_details[chat_id] = False
  text = (
      "مرحباً بك يا أخي فهد سامي القحطاني مدير جميع المؤسسات الاستثمار في بوت"
      " التمويل الاحترافي 🚀\n\nيرجى استخدام الأزرار في الأسفل للتنقل بين الأقسام"
      " المختلفة:"
  )
  bot.send_message(chat_id, text, reply_markup=get_main_menu())


@bot.message_handler(commands=["addfolder"])
def add_folder_command(message):
  if message.from_user.id != ADMIN_ID:
    return

  args = message.text.split(maxsplit=1)
  if len(args) < 2:
    bot.reply_to(
        message,
        "⚠️ يرجى كتابة اسم المجلد مع الأمر. مثال:\n`/addfolder المجلد الرابع`",
        parse_mode="Markdown",
    )
    return

  folder_title = args[1].strip()
  new_key = f"folder_{len(dynamic_folders) + 1}"
  dynamic_folders[new_key] = {
      "name": f"📁 {folder_title}",
      "link": "https://t.me/",
  }

  bot.reply_to(
      message,
      f"✅ **تم بنجاح إضافة المجلد الجديد:** `{folder_title}`\n"
      f"لتحديد رابطه، استخدم الأمر:\n`/setfolderlink {new_key}"
      " رابط_المجلد`",
      parse_mode="Markdown",
  )


@bot.message_handler(commands=["setfolderlink"])
def set_folder_link_command(message):
  if message.from_user.id != ADMIN_ID:
    return

  args = message.text.split(maxsplit=2)
  if len(args) < 3:
    bot.reply_to(
        message,
        "⚠️ صيغة الأمر غير صحيحة. مثال:\n`/setfolderlink folder_1"
        " https://t.me/addlist/xxxxx`",
        parse_mode="Markdown",
    )
    return

  folder_key = args[1].strip()
  folder_link = args[2].strip()

  if folder_key in dynamic_folders:
    dynamic_folders[folder_key]["link"] = folder_link
    folder_name = dynamic_folders[folder_key]["name"]
    bot.reply_to(
        message,
        f"✅ **تم تحديث رابط {folder_name} بنجاح!**\nالرابط الجديد:\n`{folder_link}`",
        parse_mode="Markdown",
    )
  else:
    bot.reply_to(
        message, "❌ عذراً، معرف المجلد غير موجود. تأكد من الكود (مثل folder_1)."
    )


# ==================== معالجة الأزرار التفاعلية ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
  chat_id = call.message.chat.id
  message_id = call.message.message_id
  user_id = call.from_user.id

  if call.data == "recharge_bot":
    user_waiting_for_receipt[chat_id] = False
    user_waiting_for_ad_details[chat_id] = False
    bot.edit_message_text(
        "💎 **قسم شحن البوت:**\nاختر طريقة الدفع المناسبة للشحن:",
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=get_sub_menu_with_payment(),
    )
  elif call.data == "bot_balance":
    current_balance = user_balances.get(chat_id, 0.0)
    bot.edit_message_text(
        f"💰 **رصيدك الحالي:**\n`{current_balance}` دولار / نقطة.",
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=get_sub_menu_with_payment(),
    )

  elif call.data == "advertise_channel":
    user_waiting_for_receipt[chat_id] = False
    user_waiting_for_ad_details[chat_id] = True

    ad_instructions = (
        "📢 **إعلان قناتك الآن:**\n\n"
        "الرجاء إرسال منشور إعلانك متضمناً:\n"
        "1️⃣ **اسم القناة**\n"
        "2️⃣ **رابط القناة العام**\n"
        "3️⃣ **صورة الإعلان**\n\n"
        "*(أرسلهم في رسالة واحدة (صورة مع تعليق/caption) وسيقوم البوت"
        " باستلامها فوراً)*"
    )
    bot.edit_message_text(
        ad_instructions,
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=get_back_to_main_menu_only(),
    )

  elif call.data == "how_to_advertise":
    global current_ad_photo
    user_waiting_for_receipt[chat_id] = False
    user_waiting_for_ad_details[chat_id] = False

    how_text = (
        "📢 **كيف يكون إعلانك؟ / How does your ad look?**\n\n"
        "🇪🇬 **العربية:**\n"
        "إخواني، الكل يتساءل كيف يكون إعلاني؟\n"
        "الجواب: إعلانك مجرد يتم ترتيب إعلانك ثم الموافقة على تأكيد تفعيل"
        " الإعلان، يظهر إعلانك في جميع قنوات المجلد كما تشاهدون أمامكم في الصورة"
        " 📸✨\n\n"
        "🇬🇧 **English:**\n"
        "Everyone is wondering how the ad will be displayed?\n"
        "Answer: Once your ad is arranged and approved, it will appear across"
        " all folder channels as shown in the pictures 📸✨"
    )

    try:
      bot.delete_message(chat_id, message_id)
    except Exception:
      pass

    if current_ad_photo:
      bot.send_photo(
          chat_id,
          photo=current_ad_photo,
          caption=how_text,
          parse_mode="Markdown",
          reply_markup=get_back_to_main_menu_only(),
      )
    else:
      bot.send_message(
          chat_id,
          how_text
          + "\n\n*(ملاحظة للأدمن: لم تقم برفع صورة الإعلان بعد. أرسل الصورة"
          " في الشات ليتم حفظها تلقائياً)*",
          parse_mode="Markdown",
          reply_markup=get_back_to_main_menu_only(),
      )

  elif call.data == "user_ratings":
    pos = ratings_data["positive"]
    neg = ratings_data["negative"]
    total = pos + neg

    pos_pct = (pos / total * 100) if total > 0 else 0.0
    neg_pct = (neg / total * 100) if total > 0 else 0.0

    has_voted = user_id in ratings_data["voted_users"]

    ratings_text = (
        "تقرير التقييم الشامل للبوت:\n\n"
        f"📌 نسبة التقييمات الإيجابية: {pos_pct:.2f}%\n"
        f"📌 نسبة التقييمات السلبية: {neg_pct:.2f}%\n\n"
        f"🔢 العدد الإجمالي للمستخدمين الذين قاموا بتقييم البوت: {total}\n\n"
        f"🟢 عدد التقييمات الإيجابية: {pos}\n"
        f"🔴 عدد التقييمات السلبية: {neg}"
    )

    bot.edit_message_text(
        ratings_text,
        chat_id,
        message_id,
        reply_markup=get_ratings_menu(has_voted),
    )

  elif call.data == "rate_positive":
    if user_id not in ratings_data["voted_users"]:
      ratings_data["positive"] += 1
      ratings_data["voted_users"].add(user_id)
      bot.answer_callback_query(call.id, "✅ شكراً لك! تم تسجيل تقييمك الإيجابي.")
    else:
      bot.answer_callback_query(
          call.id, "⚠️ لقد قمت بالتقييم مسبقاً!", show_alert=True
      )

    pos = ratings_data["positive"]
    neg = ratings_data["negative"]
    total = pos + neg
    pos_pct = (pos / total * 100) if total > 0 else 0.0
    neg_pct = (neg / total * 100) if total > 0 else 0.0

    updated_text = (
        "تقرير التقييم الشامل للبوت:\n\n"
        f"📌 نسبة التقييمات الإيجابية: {pos_pct:.2f}%\n"
        f"📌 نسبة التقييمات السلبية: {neg_pct:.2f}%\n\n"
        f"🔢 العدد الإجمالي للمستخدمين الذين قاموا بتقييم البوت: {total}\n\n"
        f"🟢 عدد التقييمات الإيجابية: {pos}\n"
        f"🔴 عدد التقييمات السلبية: {neg}"
    )
    try:
      bot.edit_message_text(
          updated_text,
          chat_id,
          message_id,
          reply_markup=get_ratings_menu(has_voted=True),
      )
    except Exception:
      pass

  elif call.data == "rate_negative":
    if user_id not in ratings_data["voted_users"]:
      ratings_data["negative"] += 1
      ratings_data["voted_users"].add(user_id)
      bot.answer_callback_query(
          call.id, "📌 شكراً لك! تم تسجيل تقييمك وسنعمل على تحسين البوت."
      )
    else:
      bot.answer_callback_query(
          call.id, "⚠️ لقد قمت بالتقييم مسبقاً!", show_alert=True
      )

    pos = ratings_data["positive"]
    neg = ratings_data["negative"]
    total = pos + neg
    pos_pct = (pos / total * 100) if total > 0 else 0.0
    neg_pct = (neg / total * 100) if total > 0 else 0.0

    updated_text = (
        "تقرير التقييم الشامل للبوت:\n\n"
        f"📌 نسبة التقييمات الإيجابية: {pos_pct:.2f}%\n"
        f"📌 نسبة التقييمات السلبية: {neg_pct:.2f}%\n\n"
        f"🔢 العدد الإجمالي للمستخدمين الذين قاموا بتقييم البوت: {total}\n\n"
        f"🟢 عدد التقييمات الإيجابية: {pos}\n"
        f"🔴 عدد التقييمات السلبية: {neg}"
    )
    try:
      bot.edit_message_text(
          updated_text,
          chat_id,
          message_id,
          reply_markup=get_ratings_menu(has_voted=True),
      )
    except Exception:
      pass

  elif call.data == "completed_ads":
    completed_ads_report = (
        "💻 **سجل الإعلانات المنجزة والانتشار العالمي الاحترافي:**\n\n"
        "بفضل الله ثم بثقة عملائنا، تم تنفيذ ونشر الإعلانات الناجحة عبر شبكة مجلداتنا في مختلف الدول العربية والعالمية:\n\n"
        "🇸🇦 **المملكة العربية السعودية:** `350 إعلان`\n"
        "🇦🇪 **الإمارات العربية المتحدة:** `280 إعلان`\n"
        "🇪🇬 **جمهورية مصر العربية:** `420 إعلان`\n"
        "🇰🇼 **دولة الكويت:** `190 إعلان`\n"
        "🇶🇦 **دولة قطر:** `150 إعلان`\n"
        "🇴🇲 **سلطنة عمان:** `130 إعلان`\n"
        "🇺🇸 **الولايات المتحدة الأمريكية (USA):** `45 إعلان`\n"
        "🇮🇳 **الهند (India):** `30 إعلان`\n"
        "🇬🇧 **المملكة المتحدة (UK):** `25 إعلان`\n"
        "🇩🇪 **ألمانيا (Germany):** `20 إعلان`\n"
        "🇹🇷 **تركيا (Turkey):** `60 إعلان`\n\n"
        "📊 **إجمالي الإعلانات المنجزة بنجاح عالمياً:** `1,900 إعلان` 🚀\n"
        "✨ نعمل على مدار الساعة لضمان أعلى نسبة انتشار ونمو لقنواتكم!"
    )
    bot.edit_message_text(
        completed_ads_report,
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=get_back_to_main_menu_only(),
    )

  elif call.data == "extra_contact":
    bot.edit_message_text(
        "🔄 **التواصل والدعم:**\nلأي استفسار أو مساعدة تواصل معنا عبر الأزرار.",
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=get_sub_menu_with_payment(),
    )
  elif call.data == "pay_crypto":
    user_waiting_for_receipt[chat_id] = False
    crypto_text = (
        "🪙 **العملات الرقمية:**\n"
        "📉 أقل مبلغ شحن: 10 دولار\n"
        "📈 أكثر مبلغ شحن: 200 دولار\n\n"
        "تدفع هنا 👇🏻\n"
        "بيانات الإيداع والتحويل الرسمي:\n"
        "🔹 العملة: USDT\n"
        "🔹 الشبكة: BNB Smart Chain (BEP20)\n"
        "🔹 العنوان:\n"
        "`0x4aaf2231199d24842e606f99b4f69bb5cddb171e`\n\n"
        "⚠️ يرجى التأكد من اختيار شبكة (BEP20) لضمان وصول التحويل.\n"
        "📸 عند اكتمال الدفع، يرجى إرسال لقطة شاشة (Screenshot) هنا لتوثيق"
        " وتأكيد العملية للإدارة."
    )
    bot.edit_message_text(
        crypto_text,
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=get_crypto_action_menu(),
    )
  elif call.data == "pay_stars":
    user_waiting_for_receipt[chat_id] = False
    stars_text = (
        "⭐ **شحن الرصيد عبر نجوم تيليجرام:**\n\n"
        "👇 اختر الباقة المناسبة لك:\n"
        "💳 الدفع يتم بسهولة عبر Google Play أو iTunes\n"
        "🎁 النجوم تحتسب مباشرة ضمن البونص اليومي"
    )
    bot.edit_message_text(
        stars_text,
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=get_stars_packages_menu(),
    )
  elif call.data.startswith("star_pkg_"):
    pkg_type = call.data.split("_")[2]
    packages_info = {
        "500": ("🌟 **باقة 500 نجمة**\n💰 السعر: 9.99 دولار", "500"),
        "1500": ("🔥 **باقة 1,500 نجمة**\n💰 السعر: 29.99 دولاراً", "1500"),
        "2500": ("🚀 **باقة 2,500 نجمة**\n💰 السعر: 50.90 دولاراً", "2500"),
        "5000": ("👑 **باقة 5,000 نجمة**\n💰 السعر: 101.80 دولاراً", "5000"),
        "10000": ("💎 **باقة 10,000 نجمة**\n💰 السعر: 203.60 دولاراً", "10000"),
    }
    if pkg_type in packages_info:
      desc, stars_count = packages_info[pkg_type]
      bot.edit_message_text(
          desc + "\n\nاضغط على زر الدفع أدناه لإتمام الشراء بالنجوم:",
          chat_id,
          message_id,
          parse_mode="Markdown",
          reply_markup=get_star_payment_menu(stars_count),
      )
  elif call.data.startswith("pay_stars_now_"):
    stars_count = int(call.data.split("_")[3])
    prices = [LabeledPrice(label="شحن رصيد بالنجوم", amount=stars_count)]
    title = f"شحن باقة {stars_count} نجمة"
    description = (
        f"شحن رصيد في البوت مقابل {stars_count} نجمة من نجوم تيليجرام."
    )
    payload = f"stars_topup_{stars_count}"
    currency = "XTR"
    try:
      bot.send_invoice(
          chat_id,
          title=title,
          description=description,
          invoice_payload=payload,
          provider_token="",
          currency=currency,
          prices=prices,
      )
    except Exception as e:
      bot.answer_callback_query(
          call.id, f"عذراً، حدث خطأ في إنشاء الفاتورة: {e}", show_alert=True
      )
  elif call.data == "send_receipt":
    user_waiting_for_receipt[chat_id] = True
    bot.answer_callback_query(call.id)
    bot.send_message(
        chat_id,
        "📩 **الرجاء إرسال صورة إيصال التحويل (Screenshot) مباشرة في هذه"
        " الدردشة ليقوم البوت بتحويلها إلى الإدارة فوراً ومراجعتها.**",
        parse_mode="Markdown",
    )
  elif call.data == "confirm_payment":
    bot.answer_callback_query(
        call.id,
        "تم استلام طلب التأكيد. يرجى إرسال صورة الوصل أولاً.",
        show_alert=True,
    )
  elif call.data.startswith("admin_cancel_"):
    target_user_id = int(call.data.split("_")[2])
    bot.edit_message_caption(
        f"❌ **تم رفض العملية وإلغاء الطلب للمستخدم (ID: {target_user_id})**",
        chat_id,
        message_id,
        parse_mode="Markdown",
    )
    bot.send_message(
        target_user_id,
        "❌ عذراً، تم رفض إيصال الدفع من قبل الإدارة. يرجى التأكد والمحاولة"
        " مرة أخرى.",
    )
  elif call.data.startswith("admin_approve_"):
    target_user_id = int(call.data.split("_")[2])
    admin_waiting_for_amount[user_id] = target_user_id
    bot.answer_callback_query(call.id)
    bot.send_message(
        user_id,
        "✍️ **أرسل الآن المبلغ المراد إضافته لرصيد المستخدم (اكتب الرقم فقط مثلاً:"
        " 50 أو 100):**",
        parse_mode="Markdown",
    )

  elif call.data in dynamic_folders:
    folder_info = dynamic_folders[call.data]
    f_name = folder_info["name"]
    f_link = folder_info["link"]

    folder_markup = InlineKeyboardMarkup()
    folder_markup.row(
        InlineKeyboardButton(
            "🔗 انقر هنا لعرض المجلد والانضمام إليه", url=f_link
        )
    )
    folder_markup.row(
        InlineKeyboardButton(
            "🔙 رجوع للقائمة الرئيسية", callback_data="back_to_main"
        )
    )

    bot.edit_message_text(
        f"📂 أنت الآن تصفح **{f_name}**.\n\n"
        "يمكنك الضغط على الزر أدناه للانتقال المباشر إلى المجلد ورؤية قنواته:",
        chat_id,
        message_id,
        reply_markup=folder_markup,
    )

  elif call.data.startswith("select_"):
    folder_key = call.data.replace("select_", "")
    selected_f_name = dynamic_folders.get(folder_key, {}).get("name", "المجلد")

    if chat_id not in user_temp_ad_data:
      user_temp_ad_data[chat_id] = {}
    user_temp_ad_data[chat_id]["folder"] = selected_f_name

    duration_text = (
        f"✅ **تم اختيار `{selected_f_name}` بنجاح!**\n\n"
        "اختار المدة ازمنيه علانك اختار من احد الازرار امامك 👇🏻\n\n"
        "• علان لمدة 10 ساعات 5$\n"
        "• علان لمدة 24 ساعة 12 $\n"
        "• علان لمدة 48 ساعة 24 $"
    )

    bot.edit_message_text(
        duration_text,
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=get_ad_duration_menu(),
    )

  elif call.data.startswith("duration_"):
    duration_type = call.data.replace("duration_", "")
    prices_map = {"10h": 5.0, "24h": 12.0, "48h": 24.0}
    duration_names_map = {
        "10h": "علان لمدة 10 ساعات (5$)",
        "24h": "علان لمدة 24 ساعة (12$)",
        "48h": "علان لمدة 48 ساعة (24$)",
    }

    price = prices_map.get(duration_type, 0.0)

    if chat_id not in user_temp_ad_data:
      user_temp_ad_data[chat_id] = {}
    user_temp_ad_data[chat_id]["duration"] = duration_names_map.get(
        duration_type, ""
    )
    user_temp_ad_data[chat_id]["price"] = price
    user_temp_ad_data[chat_id]["duration_type"] = duration_type

    confirm_text = (
        f"⚠️ **تأكيد عملية الحجز والخصم:**\n\n"
        f"سيتم خصم ({int(price)}$) من رصيدك في البوت، هل أنت جاهز الآن؟\n\n"
        "إذا كنت جاهزاً، اضغط على زر (تأكيد) أدناه 👇🏻"
    )

    bot.edit_message_text(
        confirm_text,
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=get_confirm_deduct_menu(duration_type),
    )

  elif call.data.startswith("confirm_deduct_"):
    ad_info = user_temp_ad_data.get(chat_id, {})
    price = ad_info.get("price", 0.0)
    current_bal = user_balances.get(chat_id, 0.0)

    if current_bal < price:
      insufficient_text = (
          "❌ **عذراً، رصيدك غير كافي لإتمام هذا الإعلان!** 💳📉\n\n"
          f"💰 رصيدك الحالي: `{int(current_bal)}$`\n"
          f"🏷️ المبلغ المطلوب: `{int(price)}$`\n\n"
          "✨ يا هلا بك يا غالي، منصتنا تمنحك أفضل قوة انتشار لقناتك وتستحق"
          " الأفضل دائماً!\n"
          "الرجاء شحن رصيد البوت لتتمكن من تفعيل إعلانك الاحترافي وتحقيق نتائج"
          " مذهلة. نحن بانتظارك! 🚀💎"
      )
      bot.edit_message_text(
          insufficient_text,
          chat_id,
          message_id,
          parse_mode="Markdown",
          reply_markup=get_recharge_direct_menu(),
      )
      return

    user_balances[chat_id] = current_bal - price

    review_text = (
        "⏳ **تم استلام طلبك بنجاح!**\n\n"
        "الإدارة تقوم بمراجعة طلبك الآن.\n"
        "*(ملاحظة: الوقت الذي يتم استنفاذه أثناء الانتظار لم يُحسب، وسيبدأ عداد"
        " الإعلان فور الموافقة ونشره)*"
    )

    bot.edit_message_text(
        review_text,
        chat_id,
        message_id,
        parse_mode="Markdown",
        reply_markup=get_back_to_main_menu_only(),
    )

    folder = ad_info.get("folder", "غير محدد")
    duration = ad_info.get("duration", "غير محدد")
    photo_id = ad_info.get("photo_id", None)
    caption_text = ad_info.get("caption", "بدون نص")

    admin_msg_text = (
        f"📢 **طلب إعلان جديد بانتظار الموافقة!**\n\n"
        f"👤 معرف المستخدم (ID): `{chat_id}`\n"
        f"📁 المجلد المختار: `{folder}`\n"
        f"⏱️ المدة المختارة: `{duration}`\n"
        f"💰 المبلغ المخصوم: `{int(price)}$`\n\n"
        f"📝 **تفاصيل الإعلان المرسل:**\n{caption_text}"
    )

    try:
      if photo_id:
        bot.send_photo(
            ADMIN_ID,
            photo_id,
            caption=admin_msg_text,
            parse_mode="Markdown",
            reply_markup=get_admin_ad_review_menu(chat_id),
        )
      else:
        bot.send_message(
            ADMIN_ID,
            admin_msg_text,
            parse_mode="Markdown",
            reply_markup=get_admin_ad_review_menu(chat_id),
        )
    except Exception as e:
      print(f"خطأ في إرسال تفاصيل الإعلان للأدمن: {e}")

  elif call.data.startswith("accept_ad_"):
    target_user_id = int(call.data.replace("accept_ad_", ""))

    accepted_msg = (
        "🎉 **تهانينا! تم قبول إعلانك بنجاح ونشره في القنوات** 🚀✨\n\n"
        "أهلاً بك دائماً معنا في منصة التمويل والاستثمار الاحترافي. تم تفعيل"
        " إعلانك بالمدة المطلوبة وبدأ عداد الظهور الآن بنجاح.\n"
        "نتمنى لك دوام التوفيق والنجاح وزيادة كبيرة في تفاعل ومتابعي قناتك! 🌟"
    )

    try:
      bot.send_message(target_user_id, accepted_msg, parse_mode="Markdown")
      bot.edit_message_caption(
          f"✅ **تم قبول هذا الإعلان ونشره بنجاح للمستخدم (ID: `{target_user_id}`)**",
          chat_id,
          message_id,
          parse_mode="Markdown",
      )
    except Exception as e:
      bot.answer_callback_query(
          call.id, f"حدث خطأ أثناء إرسال رسالة القبول: {e}", show_alert=True
      )

  elif call.data.startswith("reject_ad_"):
    target_user_id = int(call.data.replace("reject_ad_", ""))

    ad_info = user_temp_ad_data.get(target_user_id, {})
    price = ad_info.get("price", 0.0)

    current_bal = user_balances.get(target_user_id, 0.0)
    user_balances[target_user_id] = current_bal + price

    rejected_msg = (
        f"❌ **عذراً، لقد تم رفض طلب إعلانك الحالي من قبل الإدارة** 🛑\n"
        f" وتم رجوع المبلغ (`{int(price)}$`) المخصوم من حسابك 💰\n\n"
        "نعتذر منك لعدم مطابقة محتوى أو شروط الإعلان للمعايير العامة الخاصة"
        " بالمجلدات حالياً.\n"
        "يرجى مراجعة تفاصيل وشروط الإعلانات أو التواصل مع الدعم الفني، ويمكنك"
        " إعادة المحاولة في أي وقت تريده. شكراً لتفهمك! 🙏"
    )

    try:
      bot.send_message(target_user_id, rejected_msg, parse_mode="Markdown")
      bot.edit_message_caption(
          f"❌ **تم رفض هذا الإعلان وإلغاء الطلب وتم إرجاع مبلغ `{int(price)}$`"
          f" للمستخدم (ID: `{target_user_id}`)**",
          chat_id,
          message_id,
          parse_mode="Markdown",
      )
    except Exception as e:
      bot.answer_callback_query(
          call.id, f"حدث خطأ أثناء إرسال رسالة الرفض: {e}", show_alert=True
      )

  elif call.data == "back_to_main":
    user_waiting_for_receipt[chat_id] = False
    user_waiting_for_ad_details[chat_id] = False
    text = (
        "مرحباً بك يا أخي فهد سامي القحطاني مدير جميع المؤسسات الاستثمار في بوت"
        " التمويل الاحترافي 🚀\n\nيرجى استخدام الأزرار في الأسفل للتنقل بين الأقسام"
        " المختلفة:"
    )
    try:
      bot.delete_message(chat_id, message_id)
      bot.send_message(chat_id, text, reply_markup=get_main_menu())
    except Exception:
      bot.edit_message_text(
          text, chat_id, message_id, reply_markup=get_main_menu()
      )


# ==================== معالجة الدفع بالنجوم ====================
@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
  bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@bot.message_handler(content_types=["successful_payment"])
def got_payment(message):
  payment_info = message.successful_payment
  total_amount = payment_info.total_amount
  chat_id = message.chat.id

  current_bal = user_balances.get(chat_id, 0.0)
  user_balances[chat_id] = current_bal + total_amount

  bot.send_message(
      chat_id,
      f"🎉 **تم الدفع بنجاح عبر نجوم تيليجرام!**\n⭐ تمت إضافة قيمة النجوم إلى"
      f" رصيدك في البوت. رصيدك الحالي: `{user_balances[chat_id]}`",
      parse_mode="Markdown",
  )

  try:
    bot.send_message(
        ADMIN_ID,
        f"⭐ **عملية دفع ناجحة عبر النجوم!**\n👤 المستخدم: `{chat_id}`\n💰 عدد"
        f" النجوم المدفوعة: `{total_amount}`",
        parse_mode="Markdown",
    )
  except Exception as e:
    print(f"خطأ إرسال إشعار النجوم للآدمن: {e}")


# ==================== معالجة الرسائل والصور ====================
@bot.message_handler(content_types=["text", "photo"])
def handle_all_messages(message):
  global current_ad_photo
  chat_id = message.chat.id
  user_id = message.from_user.id

  if (
      user_id == ADMIN_ID
      and message.content_type == "photo"
      and not user_waiting_for_receipt.get(chat_id, False)
      and not user_waiting_for_ad_details.get(chat_id, False)
  ):
    current_ad_photo = message.photo[-1].file_id
    bot.reply_to(
        message,
        "✅ **تم تحديث وحفظ صورة الإعلان بنجاح!**",
        parse_mode="Markdown",
    )
    return

  if user_waiting_for_ad_details.get(chat_id, False):
    user_waiting_for_ad_details[chat_id] = False

    if chat_id not in user_temp_ad_data:
      user_temp_ad_data[chat_id] = {}

    if message.content_type == "photo":
      user_temp_ad_data[chat_id]["photo_id"] = message.photo[-1].file_id
      user_temp_ad_data[chat_id][
          "caption"
      ] = message.caption if message.caption else "بدون نص"
    else:
      user_temp_ad_data[chat_id]["photo_id"] = None
      user_temp_ad_data[chat_id]["caption"] = message.text

    bot.reply_to(
        message,
        "📥 **تم استلام تفاصيل إعلانك بنجاح!**\n\n"
        "الرجاء اختيار المجلد الذي تود إعلان قناتك في جميع قنواته:\n"
        "اختر من هنا المجلد المناسب لك 👇🏻",
        parse_mode="Markdown",
        reply_markup=get_folders_selection_menu(),
    )
    return

  if user_id == ADMIN_ID and user_id in admin_waiting_for_amount:
    target_user_id = admin_waiting_for_amount[user_id]
    amount_text = message.text.strip()

    if amount_text.isdigit():
      amount = float(amount_text)
      current_bal = user_balances.get(target_user_id, 0.0)
      user_balances[target_user_id] = current_bal + amount

      bot.reply_to(
          message,
          f"✅ **تم بنجاح إضافة مبلغ `{amount}` إلى حساب المستخدم (ID:"
          f" `{target_user_id}`)!**\nرصيده الجديد أصبح: `{user_balances[target_user_id]}`",
          parse_mode="Markdown",
      )

      try:
        bot.send_message(
            target_user_id,
            f"🎉 **مبروك! تم تأكيد الشحن بنجاح من قبل الإدارة.**\n💰 تمت إضافة"
            f" رصيد وقدره: `{amount}` إلى حسابك في البوت.",
            parse_mode="Markdown",
        )
      except Exception as e:
        print(f"لم يتم إرسال الرسالة للمستخدم: {e}")

      del admin_waiting_for_amount[user_id]
      return
    else:
      bot.reply_to(
          message,
          "⚠️ يرجى إرسال رقم صحيح فقط للمبلغ (مثال: 50 أو 100). حاول مرة أخرى.",
      )
      return

  if message.content_type == "photo":
    user_name = (
        message.from_user.first_name
        if message.from_user.first_name
        else "مستخدم"
    )

    if user_waiting_for_receipt.get(chat_id, False):
      bot.reply_to(
          message,
          "✅ **تم استلام لقطة الشاشة (Screenshot) بنجاح!**\nتم إرسالها إلى"
          " الإدارة للمراجعة وتأكيد الشحن في حسابك قريباً.",
          parse_mode="Markdown",
      )
      user_waiting_for_receipt[chat_id] = False

      file_id = message.photo[-1].file_id
      caption = (
          f"📥 **طلب شحن جديد من المستخدم:** {user_name}\n🆔 المعرف: `{user_id}`"
          f"\n\nيرجى مراجعة إيصال الدفع بالأعلى، ثم الضغط على (تأكيد الشحن) وكتابة"
          " المبلغ:"
      )

      try:
        bot.send_photo(
            ADMIN_ID,
            file_id,
            caption=caption,
            parse_mode="Markdown",
            reply_markup=get_admin_action_menu(user_id),
        )
      except Exception as e:
        print(f"خطأ في إرسال الصورة للآدمن: {e}")
    else:
      bot.reply_to(
          message,
          "📸 شكراً لإرسال الصورة. للشحن، يرجى الدخول إلى (شحن البوت) ثم اختيار"
          " طريقة الدفع المناسبة.",
      )


# ==================== تشغيل البوت ====================
if __name__ == "__main__":
  print(
      "تم تشغيل البوت بنجاح (كود رقم 26 - النسخة العالمية للإعلانات المنجزة)..."
  )
  bot.infinity_polling(timeout=60, long_polling_timeout=60)
