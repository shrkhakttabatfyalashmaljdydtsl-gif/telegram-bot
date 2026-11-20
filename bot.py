import time
import bot as bot_mod

bot = bot_mod.bot
ADMIN_ID = bot_mod.ADMIN_ID
register_user = bot_mod.register_user
get_all_users = bot_mod.get_all_users
save_balance = bot_mod.save_balance
save_ad_photo = bot_mod.save_ad_photo
get_folders_selection_menu = bot_mod.get_folders_selection_menu
get_back_to_main_menu_only = bot_mod.get_back_to_main_menu_only
get_admin_support_action_menu = bot_mod.get_admin_support_action_menu
get_admin_action_menu = bot_mod.get_admin_action_menu


@bot.message_handler(content_types=["text", "photo"])
def handle_all_messages(message):
  chat_id = message.chat.id
  user_id = message.from_user.id
  register_user(user_id, chat_id)
  user_name = (
      message.from_user.first_name if message.from_user.first_name else "مستخدم"
  )

  if user_id == ADMIN_ID:
    if message.text and message.text.strip() == "/cancel":
      if ADMIN_ID in bot_mod.admin_waiting_for_broadcast:
        bot_mod.admin_waiting_for_broadcast.remove(ADMIN_ID)
        bot.reply_to(message, "❌ تم إلغاء عملية الإرسال الجماعي.")
      return

    if ADMIN_ID in bot_mod.admin_waiting_for_broadcast:
      bot_mod.admin_waiting_for_broadcast.remove(ADMIN_ID)
      recipients = get_all_users()
      sent_count = 0
      failed_count = 0

      status_msg = bot.reply_to(
          message,
          f"⏳ **جاري إرسال الرسالة إلى `{len(recipients)}` مستخدم...**",
          parse_mode="Markdown",
      )

      for target_chat_id in recipients:
        try:
          if message.content_type == "photo":
            bot.send_photo(
                target_chat_id,
                message.photo[-1].file_id,
                caption=message.caption if message.caption else None,
            )
          else:
            bot.send_message(target_chat_id, message.text)
          sent_count += 1
          time.sleep(0.05)
        except Exception:
          failed_count += 1

      try:
        bot.edit_message_text(
            f"✅ **اكتمل الإرسال الجماعي!**\n\n"
            f"📬 تم الإرسال بنجاح إلى: `{sent_count}` مستخدم\n"
            f"⚠️ تعذر الإرسال إلى: `{failed_count}` مستخدم",
            chat_id,
            status_msg.message_id,
            parse_mode="Markdown",
        )
      except Exception:
        bot.send_message(
            chat_id,
            f"✅ **اكتمل الإرسال الجماعي!**\n\n"
            f"📬 تم الإرسال بنجاح إلى: `{sent_count}` مستخدم\n"
            f"⚠️ تعذر الإرسال إلى: `{failed_count}` مستخدم",
            parse_mode="Markdown",
        )
      return

    if message.text and message.text == "/endchat":
      if ADMIN_ID in bot_mod.admin_active_chat:
        target_user_id = bot_mod.admin_active_chat[ADMIN_ID]
        bot_mod.user_active_admin.pop(target_user_id, None)
        bot_mod.admin_active_chat.pop(ADMIN_ID, None)
        bot.reply_to(
            message,
            "🔒 تم إنهاء جلسة الدردشة المباشرة مع هذا المستخدم بنجاح.",
        )
        bot.send_message(
            target_user_id,
            "🔒 تم إغلاق جلسة الدعم الفني الحالية. شكراً لتواصلك معنا!",
        )
      else:
        bot.reply_to(message, "⚠️ لا توجد محادثة نشطة حالياً لإنهاؤها.")
      return

    if ADMIN_ID in bot_mod.admin_active_chat:
      target_user_id = bot_mod.admin_active_chat[ADMIN_ID]
      try:
        if message.content_type == "text":
          bot.send_message(
              target_user_id,
              f"💬 **رد الإدارة:**\n{message.text}",
              parse_mode="Markdown",
          )
        elif message.content_type == "photo":
          bot.send_photo(
              target_user_id,
              message.photo[-1].file_id,
              caption=(
                  f"💬 **رد الإدارة:**\n{message.caption}"
                  if message.caption
                  else "💬 رد من الإدارة"
              ),
          )
        bot.reply_to(message, "✅ تم إرسال الرد للمستخدم بنجاح.")
      except Exception as e:
        bot.reply_to(
            message, f"❌ فشل إرسال الرد للمستخدم (ربما قام بحظر البوت): {e}"
        )
      return

    if (
        message.content_type == "photo"
        and not bot_mod.user_waiting_for_receipt.get(chat_id, False)
        and not bot_mod.user_waiting_for_ad_details.get(chat_id, False)
    ):
      photo_id = message.photo[-1].file_id
      bot_mod.current_ad_photo = photo_id
      save_ad_photo(photo_id)
      bot.reply_to(
          message,
          "✅ **تم تحديث وحفظ صورة الإعلان بنجاح!**",
          parse_mode="Markdown",
      )
      return

    if user_id in bot_mod.admin_waiting_for_amount:
      target_user_id = bot_mod.admin_waiting_for_amount[user_id]
      amount_text = (message.text or "").strip()
      if amount_text.isdigit():
        amount = float(amount_text)
        new_bal = bot_mod.user_balances.get(target_user_id, 0.0) + amount
        bot_mod.user_balances[target_user_id] = new_bal
        save_balance(target_user_id, new_bal)
        bot.reply_to(
            message,
            f"✅ **تم بنجاح إضافة مبلغ `{amount}` إلى حساب المستخدم (ID:"
            f" `{target_user_id}`)!**\nرصيده الجديد أصبح:"
            f" `{bot_mod.user_balances[target_user_id]}`",
            parse_mode="Markdown",
        )
        try:
          bot.send_message(
              target_user_id,
              f"🎉 **مبروك! تم تأكيد الشحن بنجاح من قبل الإدارة.**\n💰 تمت إضافة"
              f" رصيد وقدره: `{amount}` دولار إلى حسابك في البوت.",
              parse_mode="Markdown",
          )
        except Exception as e:
          print(f"لم يتم إرسال الرسالة للمستخدم: {e}")
        del bot_mod.admin_waiting_for_amount[user_id]
        return
      else:
        bot.reply_to(
            message,
            "⚠️ يرجى إرسال رقم صحيح فقط للمبلغ (مثال: 50 أو 100). حاول مرة أخرى.",
        )
        return
    return

  if bot_mod.user_active_admin.get(user_id, False):
    support_text = (
        message.text
        if message.text
        else (message.caption if message.caption else "محتوى مرفق")
    )
    forward_caption = (
        f"💬 **رد جديد من المستخدم:** {user_name}\n"
        f"🆔 المعرف: `{user_id}`\n\n"
        f"محتوى الرسالة:\n{support_text}"
    )
    try:
      if message.content_type == "photo":
        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=forward_caption,
            parse_mode="Markdown",
        )
      else:
        bot.send_message(
            ADMIN_ID,
            forward_caption,
            parse_mode="Markdown",
        )
      bot.reply_to(message, "✅ تم إرسال رسالتك للأدمن.")
    except Exception as e:
      print(f"خطأ في توجيه رسالة المحادثة للأدمن: {e}")
    return

  if bot_mod.user_waiting_for_ad_details.get(chat_id, False):
    bot_mod.user_waiting_for_ad_details[chat_id] = False
    if chat_id not in bot_mod.user_temp_ad_data:
      bot_mod.user_temp_ad_data[chat_id] = {}
    if message.content_type == "photo":
      bot_mod.user_temp_ad_data[chat_id]["photo_id"] = message.photo[-1].file_id
      bot_mod.user_temp_ad_data[chat_id][
          "caption"
      ] = message.caption if message.caption else "بدون نص"
    else:
      bot_mod.user_temp_ad_data[chat_id]["photo_id"] = None
      bot_mod.user_temp_ad_data[chat_id]["caption"] = message.text

    bot.reply_to(
        message,
        "📥 **تم استلام تفاصيل إعلانك بنجاح!**\n\n"
        "الرجاء اختيار المجلد الذي تود إعلان قناتك في جميع قنواته:\n"
        "اختر من هنا المجلد المناسب لك 👇🏻",
        parse_mode="Markdown",
        reply_markup=get_folders_selection_menu(),
    )
    return

  if bot_mod.user_waiting_for_support_message.get(chat_id, False):
    bot_mod.user_waiting_for_support_message[chat_id] = False
    support_text = (
        message.text
        if message.text
        else (message.caption if message.caption else "محتوى غير نصي")
    )

    bot.reply_to(
        message,
        "✅ **تم ارسال رسالتك إلى فريق الدعم الفني والإدارة بنجاح!**\n"
        "شكراً لتواصلك معنا، سيتم الاطلاع على رسالتك والرد عليك قريباً جداً عند"
        " تواجد الإدارة. طاب يومك! 🙏",
        parse_mode="Markdown",
        reply_markup=get_back_to_main_menu_only(),
    )

    admin_support_notification = (
        f"📩 **رسالة جديدة من قسم الدعم والتواصل:**\n\n"
        f"👤 اسم المستخدم: {user_name}\n"
        f"🆔 معرف المستخدم (ID): `{chat_id}`\n\n"
        f"💬 **محتوى الرسالة:**\n{support_text}"
    )

    try:
      if message.content_type == "photo":
        bot.send_photo(
            ADMIN_ID,
            message.photo[-1].file_id,
            caption=admin_support_notification,
            parse_mode="Markdown",
            reply_markup=get_admin_support_action_menu(chat_id),
        )
      else:
        bot.send_message(
            ADMIN_ID,
            admin_support_notification,
            parse_mode="Markdown",
            reply_markup=get_admin_support_action_menu(chat_id),
        )
    except Exception as e:
      print(f"خطأ في إرسال رسالة الدعم للأدمن: {e}")
    return

  if message.content_type == "photo":
    if bot_mod.user_waiting_for_receipt.get(chat_id, False):
      bot.reply_to(
          message,
          "✅ **تم استلام لقطة الشاشة (Screenshot) بنجاح!**\nتم إرسالها إلى"
          " الإدارة للمراجعة وتأكيد الشحن في حسابك قريباً.",
          parse_mode="Markdown",
      )
      bot_mod.user_waiting_for_receipt[chat_id] = False

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
