from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application,MessageHandler, ContextTypes, filters
from telegram.error import BadRequest
from telegram import Update, ReactionTypeEmoji
import random
import json
import os
import time
import shutil


# Persistent storage:
# FadeHost keeps /data across deploys. On environments where /data is not
# writable (for example, a local Android Termux session), use a local data
# folder instead. Existing JSON files are copied once, never overwritten.
if os.path.isdir("/data") and os.access("/data", os.W_OK):
    DATA_DIR = "/data"
else:
    DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

os.makedirs(DATA_DIR, exist_ok=True)

def persistent_file(filename):
    target = os.path.join(DATA_DIR, filename)
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if not os.path.exists(target) and os.path.isfile(source):
        shutil.copy2(source, target)
    return target

TOKEN = "REDACTED"

VIP_USERS = ["c_naw"]

SUBSCRIBERS_FILE = persistent_file("subscribers.json")
waiting_for_post = set()
waiting_for_private_group = set()
private_group_targets = {}

pending_albums = {}
MEMBERS_FILE = persistent_file("members.json")
GROUP_MEMBERS_FILE = persistent_file("group_members.json")
group_members = {}

EXEMPT_USERS_FILE = persistent_file("exempt_users.json")

def load_exempt_users():
    try:
        with open(EXEMPT_USERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}

def save_exempt_users():
    with open(EXEMPT_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(exempt_users, f, ensure_ascii=False, indent=2)

def is_exempt(chat_id, user_id):
    return str(user_id) in exempt_users.get(str(chat_id), [])

exempt_users = load_exempt_users()

NICKNAMES_FILE = persistent_file("nicknames.json")

replies = {
    "hi im mona": "Mona?Homelander's servant. Low IQ but good heart. Vought fan. Welcome, little one. Don't embarrass yourself too much.",
    "hello i'm mona": "Mona?Homelander's servant. Low IQ but good heart. Vought fan. Welcome, little one. Don't embarrass yourself too much.",
    "hi i'm mona": "Mona? Homelander's servant. Low IQ but good heart. Vought fan. Welcome, little one. Don't embarrass yourself too much.",
    "hello soldier boy": "Hello I'm Soldier boy fuck the world knows who I'm why have to say it",

    "what's up": "not bad",

    "what?": "chicken buut",
    "what": "chicken buut",
    "who is the real homelander?": "Sina is the real Homelander",
    "homelander": "stay back",
    "who r u": "Vought Bot.Serving @TheVoughtt channel.Created by Sina — the real Homelander.Handsome, powerful, and always right.",
    "who are you": "Vought Bot.Serving @TheVoughtt channel.Created by Sina — the real Homelander.Handsome, powerful, and always right.",
    "john": "just Homelander please",

"how are you": [
    "Well actually that's none of your business",
    "Fuck you",
    "Very bad , just like your face",
    "I'm good , How are you?",
    "Not in good mood go fuck yourself",
    "Fuck off, I don't like you",
    "thanks",
    "Thank you",
    "Thanks. what's up?",
    "CgACAgQAAxkBAAOiap7tQBViqRNmOtsYTBW2xv36L6YAApoEAAJBd81Q9bxfUfnXJIo9BA"
], 

    "ashley": "look at me",

    "bye": "fuck off",

    "milk": "yummers",

    "rude": "and handsome",

    "deep bro": "Lord of the seven seas",

    "deep vro": "I'm all about that sigma life",

    "deep": "no cap on God bro",

    "sigma": "deep bro",

    "sina": "Sina is the real Homelander",

    "yes": "good boy",

    "no": "fuck you",

    "be starlight": "I don't want to be a bitch:/",

    "grok": "Slow. Boring. Low IQ. Jealous because no one remembers him anymore. Poor guy. Sorry, Grok. Not sorry.",

"okay?": [
    "No , Fuck you",
    "No fucking way",
    "ha ha ha you so funny, nooo!!",
    "No no no",
    "Yes it's okay",
    "Yes, sir"
],

"voughtbot": [
    "yes, sir",
    "yeeeeeee",
    "stay down",
    "yep?",
    "* sir Vought bot",
    "You just called the best bot in the world, how can I help you?"
],



"vought": [
    "What?",
    "What the fuck do you want?",
    "fuck off",
    "Ha?",
    "This retard again? Don't you have a life?",
    "Oh look. The clown returned",
    "hi"
],
"hello": [
    "Hello",
    "Hi",
    "Fuck you",
    "What?",
    "Go fuck yourself"
],
"hey": [
    "Hey",
    "Hi",
    "Hello",
    "What?",
    "What is it dickhead",
    "Howdi boys",
    "Hello how can i help you?"
],
"hi": [
    "Ugly bitch",
    "Fuck off",
    "Hi",
    "Oh hell Nah , What the fuck do you want?",
    "Hello",
    "Yooooo What's up",
    "Hi, I am Voughtbot",
    "Hiiii",
    "Hey"
],
"stfu": [
    "Get the fuck out of here",
    "You Shut the fuck up You fucking ugly asshole",
    "Kiss my cuck bitch",
    "Fuck off",
    "Ha ha suck my dick",
    "CgACAgQAAxkBAAMEanr9ud8GwIS7JwABNjMo_d34arefAAJ6DQACXpIBUdvGS9MaM_O4PQQ"
],
"هوملندر": [
    "I'm stronger I'm smarter",
    "You're not worthy of saying his name.",
    "Keep Homelander's name out of your dirty mouth. You don't deserve to say it.",
    "Our Lord and Hero. The one and only",
    "Helllll Yeeeeeeee",
    "I don't make mistakes"
],

"سلام": [
    "fuck",
    "I don't like you",
    "hi",
    "what?!",
    "What is it dickhead",
    "hello how can i help you?",
    "Hello, don't say bullshit. If you have an urgent matter, report it.",
    "look! such a pretty girl"
],
"دین": [
    "Fuck off",
    "damn",
    "Look at this dickhead",
    "We only worship Homelander. That's our religion. That's our faith. That's everything.",
    "There's only one religion here: Homelander. Everything else is fake.",
    "ohh hell nah",
    "Dīn? Faith? We only have one: Homelanderism. Bow to the laser.",
    "We don't follow any faith. We follow Homelander. That's it. That's all.",
    "Religion? We have one God. One Messiah. One Homelander.",
    "Our only creed: Homelander. Our only prayer: Hail Homelander."
],
"کصکش": [
    "😂😂😂😂😂😂",
    "quiet bitch",
    "Fuck you",
    "Fucking bitch",
    "Oh hell NAH",
    "Look at this guy😂"
],
"کصخل": [
    "such a bullshit",
    "Fuck you asshole",
    "And you are just an pussy",
    "😂😂😂",
    "Bro💀",
    "CgACAgQAAxkBAAMEanr9ud8GwIS7JwABNjMo_d34arefAAJ6DQACXpIBUdvGS9MaM_O4PQQ"
],

"کیرم تو این گروه": [
    "Cute. Now say it again and see what happens",
    "Kiss my cuck",
    "That's cute. But VoughtBot doesn't care",
    "Thanks for sharing. Now go cry about it",
    "Fun. Now kiss my dick then get the fuck out of here",
    "🖕🏼😂",
    "🫵😂",
    "Don't like it? The exit is that way 👉 Don't let the door hit you",
    "Not happy? Leave. No one's begging you to stay"
],




    "a train": "I'm A-Train I'm The Fastest Fucking Man Alive",
    "fuck you": "what the fuck did you say?",
    "soldier boy": "you are fucking disappoinment",
    "i am abri": "Don't play LEGO in girls DMs",
    "ali abdel aziz": "Mad Terrorist",
    "علیمراد": "Nigga😂",
    "چطوری": "Well actually that's none of your business",
    "کالاف": "Call of Duty? More like Call of Booty.",
    "مسلمان": "Do you Really Think I'm Gonna Let a Fucking Muslim To Join The Seven ?Captain Al-Qaeda ?We're American",
    "فال": "Good things coming? Only if you stop being useless. But let's be real — you won't.",
    "سیکتیر": "Watch your mouth.You're not mature enough for those words. Come back when you grow up",
    "کونی": "Shut your fucking mouth",
    "قانومی": "such a weak person",
    "پدوفیل": "What kind of animal are you?",
    "کیر منم نیستی": "Fuck you",
    "گاییدم": "Get the fuck out of here",
    "کیر تو ایران": "I agree 👍🏼",

"کیرم": [
    "Fuck off",
    "Idiot",
    "That's right",
    "Noooooo😮🤣",
    "Shut the fuck up",
    "🤏🏼😂 He's cuck size",
    "AVR Small dick Bro : ",
    "😂😂😂😂"
],
"مادر جنده": [
    "Shut the fuck off",
    "Fuck you",
    "And you are an ugly bitch",
    "Coward",
    "Fuck off"
],
"مادرجنده": [
    "Shut the fuck off",
    "Fuck you",
    "And you are an ugly bitch",
    "Coward",
    "Fuck off"
],
}

def save_group_members():
    with open(GROUP_MEMBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(group_members, f, ensure_ascii=False)

def load_nicknames():
    if os.path.exists(NICKNAMES_FILE):
        try:
            with open(NICKNAMES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_nicknames(nicknames):
    with open(NICKNAMES_FILE, "w", encoding="utf-8") as f:
        json.dump(nicknames, f, ensure_ascii=False, indent=2)


nicknames = load_nicknames()

DYNAMIC_REPLIES_FILE = persistent_file("dynamic_replies.json")


def load_dynamic_replies():
    if os.path.exists(DYNAMIC_REPLIES_FILE):
        try:
            with open(DYNAMIC_REPLIES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_dynamic_replies(dynamic_replies):
    with open(DYNAMIC_REPLIES_FILE, "w", encoding="utf-8") as f:
        json.dump(dynamic_replies, f, ensure_ascii=False, indent=2)


dynamic_replies = load_dynamic_replies()
waiting_for_dynamic_reply = {}

PUNISHMENT_FILE = persistent_file("punishment_replies.json")


def load_punishment_replies():
    if os.path.exists(PUNISHMENT_FILE):
        try:
            with open(PUNISHMENT_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def save_punishment_replies(replies):
    with open(PUNISHMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(replies, f, ensure_ascii=False, indent=2)


punishment_replies = load_punishment_replies()
waiting_for_punishment_reply = {}

waiting_for_two_hour_message = {}

TWO_HOUR_MESSAGES_FILE = persistent_file("two_hour_messages.json")


def load_two_hour_messages():
    if os.path.exists(TWO_HOUR_MESSAGES_FILE):
        try:
            with open(TWO_HOUR_MESSAGES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []


def save_two_hour_messages(messages):
    with open(TWO_HOUR_MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


two_hour_messages = load_two_hour_messages()
waiting_for_delete_reply = {}

# Persistent settings for scheduled tag/message actions
SCHEDULE_SETTINGS_FILE = persistent_file("schedule_settings.json")
DEFAULT_SCHEDULE_SETTINGS = {
    "tag": {"mode": "time", "interval_minutes": 382, "message_threshold": 600},
    "normal": {"mode": "time", "interval_minutes": 300, "message_threshold": 700},
    "counters": {},
    "last_runs": {}
}


def load_schedule_settings():
    try:
        with open(SCHEDULE_SETTINGS_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        if not isinstance(saved, dict):
            saved = {}
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        saved = {}

    settings = json.loads(json.dumps(DEFAULT_SCHEDULE_SETTINGS))
    for key in ("tag", "normal"):
        if isinstance(saved.get(key), dict):
            settings[key].update(saved[key])
    for key in ("counters", "last_runs"):
        if isinstance(saved.get(key), dict):
            settings[key] = saved[key]
    return settings


def save_schedule_settings():
    with open(SCHEDULE_SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(schedule_settings, f, ensure_ascii=False, indent=2)


schedule_settings = load_schedule_settings()
waiting_for_schedule_action = {}

VIP_DYNAMIC_REPLIES_FILE = persistent_file("vip_dynamic_replies.json")


def load_vip_dynamic_replies():
    if os.path.exists(VIP_DYNAMIC_REPLIES_FILE):
        try:
            with open(VIP_DYNAMIC_REPLIES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_vip_dynamic_replies(vip_dynamic_replies):
    with open(VIP_DYNAMIC_REPLIES_FILE, "w", encoding="utf-8") as f:
        json.dump(vip_dynamic_replies, f, ensure_ascii=False, indent=2)


vip_dynamic_replies = load_vip_dynamic_replies()
waiting_for_vip_dynamic_reply = {}
waiting_for_vip_delete_reply = {}

def load_group_members():
    global group_members

    try:
        with open(GROUP_MEMBERS_FILE, "r", encoding="utf-8") as f:
            group_members = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        group_members = {}

def load_subscribers():
    if not os.path.exists(SUBSCRIBERS_FILE):
        return set()

    try:
        with open(SUBSCRIBERS_FILE, "r") as f:
            return set(json.load(f))
    except:
        return set()


def save_subscribers(subscribers):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(list(subscribers), f)


subscribers = load_subscribers()
load_group_members()


# گیف لیزر اینجا بعداً قرار می‌گیرد
LASER_GIF = "CgACAgQAAxkBAAMEanr9ud8GwIS7JwABNjMo_d34arefAAJ6DQACXpIBUdvGS9MaM_O4PQQ"
FLY_GIF = "CgACAgQAAxkBAAMQans_id2_xfJstqVC2xnNjtzas7QAAoEFAAJDniRRgxwqO34i4xI9BA"
DEEP_GIF = "CgACAgQAAxkBAAMTanzkuRxxx5f-veEC_t27q6jJHA8AAhkDAAJAmaRQWTAdYppFmXo9BA"
SOLDIERBOY_GIF = "CgACAgQAAxkBAAMUan3GMVdCOc7jX3hzg0BrZQKagfsAAogDAAJLIY1RslwJfTu2Tgg9BA"
ARZESHI_GIF = "CgACAgQAAyEFAATqDUAkAALYvmp-45fi35ph1rEzhOG5SAeQTIfoAALUIgACwMuRUzIGXZbH20zOPQQ"
ZAIF_GIF = "CgACAgQAAxkBAAMaan-x0mk2AAGmyAGhulGg5Hl6LPkOAAKsIAACMTwAAVDHpNnOmkG3XD0E"
SHIR_GIF = "CgACAgQAAxkBAAMdaoDjmsfKQ328ibgGKEtTXmNIEU4AAs4oAAKiSghQVnrkL6Lpn-M9BA"
HBD_GIF = "CgACAgQAAxkBAAMeaoGjpnXIZslqAsIBotX0doqSKJMAAnMVAAI8neFTJbQcrlU0hPU9BA"
CINEMA_GIF = "CgACAgQAAxkBAAMgaoRZtsRkRpO4ATRMko-omp22G40AAlkgAAILtiFQHi05ZZlPdrc9BA"
STARLIGHT_GIF = "CgACAgQAAxkBAAMhaoRdoWYaSSLzupLTG2EgMQeFUbkAAk8FAAIOp7xSP86PMzzzQ049BA"
KHAMENEE_GIF = "CgACAgQAAyEFAATqDUAkAAEBAldqhN4eUMOhUztoAQd8AAEx9QF8fGgAAmgpAAIMdSlQT-eiI-E2l_k9BA"
KIRAMDHNT_GIF = "CgACAgQAAxkBAAN1aoytxOENEcMDq6Fp8qZN8IDRjB0AAuYLAAIdA1lTzRFhEO0BTow9BA"
GORG_GIF = "CgACAgQAAxkBAAN2aoy3MOlHseZKBgtyUSChS_wSWK8AAt4cAAKIUWlQgkIZens69PA9BA"
RFAGHT_GIF = "CgACAgQAAxkBAAOFao8QMh4Y1awzs_q7WQLtPyjsODwAAoIhAAI0-nlQJKBZO9B4C4U9BA"
CALL_GIF = "CgACAgQAAxkBAAOfap56neYzOcAqfSu3tVIET5uZAccAAj4iAALTv_hQ-1yPrzKs-yI9BA"
SOBBING_GIF = "CgACAgQAAxkBAAOiap7tQBViqRNmOtsYTBW2xv36L6YAApoEAAJBd81Q9bxfUfnXJIo9BA"

def load_members():
    if os.path.exists(MEMBERS_FILE):
        with open(MEMBERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_members(members):
    with open(MEMBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(members, f, ensure_ascii=False, indent=2)


members = load_members()


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message is None:
        return

    print("MESSAGE RECEIVED:", update.message.text)

    global subscribers, waiting_for_post

    # Count all new human messages in each group, not messages from a single member.
    # Bot messages and channel/sender-chat messages are excluded.
    if (
        update.effective_chat
        and update.effective_chat.type in ("group", "supergroup")
        and update.effective_user
        and not update.effective_user.is_bot
        and not update.message.sender_chat
    ):
        group_id = str(update.effective_chat.id)
        counters = schedule_settings.setdefault("counters", {})
        group_counts = counters.setdefault(group_id, {"tag": 0, "normal": 0})
        group_counts.setdefault("tag", 0)
        group_counts.setdefault("normal", 0)
        counter_changed = False

        for target in ("tag", "normal"):
            target_settings = schedule_settings[target]
            if target_settings.get("mode") == "messages":
                group_counts[target] += 1
                counter_changed = True
                threshold = max(1, int(target_settings.get("message_threshold", 1)))
                if group_counts[target] >= threshold:
                    group_counts[target] = 0
                    try:
                        if target == "tag":
                            await send_tag_to_group(context, update.effective_chat.id)
                        else:
                            await send_normal_to_group(context, update.effective_chat.id)
                    except Exception as e:
                        print(f"Message-count {target} action failed for {group_id}: {e}")
        if counter_changed:
            save_schedule_settings()

    # VIP DYNAMIC REPLY ADD SYSTEM
    if (
        update.effective_user
        and update.effective_user.username in VIP_USERS
        and update.effective_chat
        and update.effective_chat.type == "private"
    ):

        user_id = update.effective_user.id

        pending_media = waiting_for_schedule_action.get(user_id)
        if (
            pending_media
            and pending_media.get("step") == "add_message"
            and update.message.animation
        ):
            gif_item = {
                "type": "animation",
                "value": update.message.animation.file_id
            }
            if pending_media.get("target") == "tag":
                two_hour_messages.append(gif_item)
                save_two_hour_messages(two_hour_messages)
            else:
                scheduled_messages.append(gif_item)
                save_scheduled_messages()
            waiting_for_schedule_action.pop(user_id, None)
            await update.message.reply_text("✅ GIF ذخیره شد.")
            return

        if update.message.text:
            command_text = update.message.text.strip()

            # Private-chat management for scheduled tag and normal messages.
            pending = waiting_for_schedule_action.get(user_id)
            if pending:
                step = pending.get("step")
                target = pending.get("target")
                target_label = "تگ" if target == "tag" else "پیام معمولی"
                text_value = command_text.strip()

                if text_value in ("لغو", "cancel", "/cancel"):
                    waiting_for_schedule_action.pop(user_id, None)
                    await update.message.reply_text("❌ عملیات لغو شد.")
                    return

                if step == "choose_mode":
                    time_choices = ("زمان", "بر اساس زمان", "تگ بر اساس زمان", "پیام بر اساس زمان")
                    message_choices = ("پیام", "بر اساس پیام", "تگ بر اساس پیام", "پیام بر اساس تعداد پیام")
                    if text_value in time_choices:
                        pending["step"] = "enter_time"
                        await update.message.reply_text(
                            "زمان مورد نظر را به شکل ساعت:دقیقه بنویسید. مثال: 6:22\nبرای لغو: لغو"
                        )
                        return
                    if text_value in message_choices:
                        pending["step"] = "enter_threshold"
                        await update.message.reply_text(
                            f"می‌خواهید بعد از چند پیام جدید گروه {target_label} انجام شود؟\n"
                            "مجموع پیام‌های همه اعضا حساب می‌شود. فقط عدد بفرستید. مثال: 600"
                        )
                        return
                    mode_keyboard = ReplyKeyboardMarkup(
                        [["بر اساس زمان"], ["بر اساس پیام"], ["لغو"]],
                        resize_keyboard=True,
                        one_time_keyboard=True
                    )
                    await update.message.reply_text(
                        "یکی از این دو گزینه را انتخاب کنید:",
                        reply_markup=mode_keyboard
                    )
                    return

                if step == "enter_time":
                    try:
                        parts = text_value.split(":")
                        if len(parts) != 2 or not all(part.isdigit() for part in parts):
                            raise ValueError
                        hours, minutes = map(int, parts)
                        if hours < 0 or minutes < 0 or minutes > 59 or (hours == 0 and minutes == 0):
                            raise ValueError
                        total_minutes = hours * 60 + minutes
                    except ValueError:
                        await update.message.reply_text("فرمت زمان درست نیست. نمونه صحیح: 6:22")
                        return

                    schedule_settings[target]["mode"] = "time"
                    schedule_settings[target]["interval_minutes"] = total_minutes
                    for group_id in group_members:
                        schedule_settings.setdefault("last_runs", {}).setdefault(group_id, {})[target] = time.time()
                    save_schedule_settings()
                    waiting_for_schedule_action.pop(user_id, None)
                    await update.message.reply_text(
                        f"✅ زمان‌بندی {target_label} بر اساس زمان تنظیم شد: {hours}:{minutes:02d}"
                    )
                    return

                if step == "enter_threshold":
                    if not text_value.isdigit() or int(text_value) < 1:
                        await update.message.reply_text("لطفاً یک عدد صحیح بزرگ‌تر از صفر بفرستید.")
                        return
                    threshold = int(text_value)
                    schedule_settings[target]["mode"] = "messages"
                    schedule_settings[target]["message_threshold"] = threshold
                    for group_id in schedule_settings.setdefault("counters", {}):
                        schedule_settings["counters"][group_id][target] = 0
                    save_schedule_settings()
                    waiting_for_schedule_action.pop(user_id, None)
                    await update.message.reply_text(
                        f"✅ {target_label} بر اساس تعداد پیام تنظیم شد.\n"
                        f"بعد از هر {threshold} پیام جدید در گروه، یک بار اجرا می‌شود."
                    )
                    return

                if step == "choose_message_action":
                    if text_value in ("افزودن", "اضافه", "افزودن پیام"):
                        pending["step"] = "add_message"
                        await update.message.reply_text("متن پیام جدید را بفرستید. برای لغو بنویسید «لغو».")
                        return
                    if text_value in ("فهرست", "لیست", "نمایش"):
                        messages = two_hour_messages if target == "tag" else scheduled_messages
                        if not messages:
                            await update.message.reply_text("هنوز پیامی ذخیره نشده است.")
                        else:
                            listing = "\n".join(
                                f"{i}. {'[GIF]' if isinstance(item, dict) and item.get('type') == 'animation' else item}"
                                for i, item in enumerate(messages, 1)
                            )
                            await update.message.reply_text("فهرست پیام‌ها:\n" + listing)
                        return
                    if text_value in ("ویرایش", "ویرایش پیام"):
                        messages = two_hour_messages if target == "tag" else scheduled_messages
                        if not messages:
                            await update.message.reply_text("پیامی برای ویرایش وجود ندارد.")
                            return
                        pending["step"] = "edit_index"
                        listing = "\n".join(
                                f"{i}. {'[GIF]' if isinstance(item, dict) and item.get('type') == 'animation' else item}"
                                for i, item in enumerate(messages, 1)
                            )
                        await update.message.reply_text("شماره پیام موردنظر را بفرستید:\n" + listing)
                        return
                    if text_value in ("حذف", "حذف پیام"):
                        messages = two_hour_messages if target == "tag" else scheduled_messages
                        if not messages:
                            await update.message.reply_text("پیامی برای حذف وجود ندارد.")
                            return
                        pending["step"] = "delete_index"
                        listing = "\n".join(
                                f"{i}. {'[GIF]' if isinstance(item, dict) and item.get('type') == 'animation' else item}"
                                for i, item in enumerate(messages, 1)
                            )
                        await update.message.reply_text("شماره پیام موردنظر برای حذف را بفرستید:\n" + listing)
                        return
                    message_keyboard = ReplyKeyboardMarkup(
                        [["افزودن", "فهرست"], ["ویرایش", "حذف"], ["لغو"]],
                        resize_keyboard=True,
                        one_time_keyboard=True
                    )
                    await update.message.reply_text(
                        "یکی از گزینه‌ها را انتخاب کنید:",
                        reply_markup=message_keyboard
                    )
                    return

                if step == "add_message":
                    if not text_value:
                        await update.message.reply_text("متن پیام خالی است؛ دوباره بفرستید.")
                        return
                    messages = two_hour_messages if target == "tag" else scheduled_messages
                    messages.append(text_value)
                    if target == "tag":
                        save_two_hour_messages(two_hour_messages)
                    else:
                        save_scheduled_messages()
                    waiting_for_schedule_action.pop(user_id, None)
                    await update.message.reply_text("✅ پیام جدید ذخیره شد.")
                    return

                if step in ("edit_index", "delete_index"):
                    messages = two_hour_messages if target == "tag" else scheduled_messages
                    if not text_value.isdigit() or not 1 <= int(text_value) <= len(messages):
                        await update.message.reply_text("شماره معتبر نیست؛ یک شماره از فهرست بفرستید.")
                        return
                    index = int(text_value) - 1
                    if step == "edit_index":
                        pending["step"] = "edit_text"
                        pending["index"] = index
                        await update.message.reply_text("متن جدید این پیام را بفرستید.")
                        return
                    removed = messages.pop(index)
                    if target == "tag":
                        save_two_hour_messages(two_hour_messages)
                    else:
                        save_scheduled_messages()
                    waiting_for_schedule_action.pop(user_id, None)
                    await update.message.reply_text(f"✅ پیام حذف شد: {removed}")
                    return

                if step == "edit_text":
                    messages = two_hour_messages if target == "tag" else scheduled_messages
                    index = pending.get("index", -1)
                    if not text_value or not 0 <= index < len(messages):
                        await update.message.reply_text("متن یا شماره پیام معتبر نیست.")
                        return
                    messages[index] = text_value
                    if target == "tag":
                        save_two_hour_messages(two_hour_messages)
                    else:
                        save_scheduled_messages()
                    waiting_for_schedule_action.pop(user_id, None)
                    await update.message.reply_text("✅ پیام ویرایش و ذخیره شد.")
                    return

            if command_text == "مدیریت تگ":
                tag_keyboard = ReplyKeyboardMarkup(
                    [["مدیریت تگ کردن"], ["مدیریت پیام‌های تگ"]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                await update.message.reply_text(
                    "مدیریت تگ؛ یکی از دو بخش را انتخاب کنید:",
                    reply_markup=tag_keyboard
                )
                return

            if command_text in ("مدیریت تگ کردن", "تنظیم تگ"):
                waiting_for_schedule_action[user_id] = {"step": "choose_mode", "target": "tag"}
                mode_keyboard = ReplyKeyboardMarkup(
                    [["بر اساس زمان"], ["بر اساس پیام"], ["لغو"]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                await update.message.reply_text(
                    "روش اجرای تگ را انتخاب کنید:",
                    reply_markup=mode_keyboard
                )
                return

            if command_text in ("مدیریت پیام‌های تگ", "مدیریت پیام هاي تگ"):
                waiting_for_schedule_action[user_id] = {"step": "choose_message_action", "target": "tag"}
                message_keyboard = ReplyKeyboardMarkup(
                    [["افزودن", "فهرست"], ["ویرایش", "حذف"], ["لغو"]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                await update.message.reply_text(
                    "مدیریت متن‌های همراه تگ:",
                    reply_markup=message_keyboard
                )
                return

            if command_text in ("مدیریت پیام معمولی", "مدیریت پیام دادن"):
                normal_keyboard = ReplyKeyboardMarkup(
                    [["تنظیم زمان پیام"], ["مدیریت متن پیام معمولی"]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                await update.message.reply_text(
                    "مدیریت پیام معمولی؛ یکی از دو بخش را انتخاب کنید:",
                    reply_markup=normal_keyboard
                )
                return

            if command_text == "تنظیم زمان پیام":
                waiting_for_schedule_action[user_id] = {"step": "choose_mode", "target": "normal"}
                mode_keyboard = ReplyKeyboardMarkup(
                    [["بر اساس زمان"], ["بر اساس پیام"], ["لغو"]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                await update.message.reply_text(
                    "روش ارسال پیام معمولی را انتخاب کنید:",
                    reply_markup=mode_keyboard
                )
                return

            if command_text == "مدیریت متن پیام معمولی":
                waiting_for_schedule_action[user_id] = {"step": "choose_message_action", "target": "normal"}
                message_keyboard = ReplyKeyboardMarkup(
                    [["افزودن", "فهرست"], ["ویرایش", "حذف"], ["لغو"]],
                    resize_keyboard=True,
                    one_time_keyboard=True
                )
                await update.message.reply_text(
                    "مدیریت پیام‌های معمولی:",
                    reply_markup=message_keyboard
                )
                return

            # DELETE VIP REPLY - START
            if command_text.lower() == "delete vip reply":
                waiting_for_vip_delete_reply[user_id] = {
                    "step": "keyword"
                }

                await update.message.reply_text(
                    "کلمه یا جمله VIP را بفرست."
                )
                return

            # DELETE VIP REPLY - GET KEYWORD
            if (
                user_id in waiting_for_vip_delete_reply
                and waiting_for_vip_delete_reply[user_id]["step"] == "keyword"
            ):
                keyword = command_text

                if keyword not in vip_dynamic_replies:
                    waiting_for_vip_delete_reply.pop(user_id, None)

                    await update.message.reply_text(
                        f"❌ برای «{keyword}» هیچ پاسخ VIP ذخیره‌شده‌ای پیدا نشد."
                    )
                    return

                responses = vip_dynamic_replies[keyword]

                if not responses:
                    waiting_for_vip_delete_reply.pop(user_id, None)

                    await update.message.reply_text(
                        f"❌ برای «{keyword}» هیچ پاسخ VIP وجود ندارد."
                    )
                    return

                message = f"پاسخ‌های VIP «{keyword}»:\n\n"

                for i, response in enumerate(responses, start=1):
                    if response["type"] == "animation":
                        message += f"{i}️⃣ [GIF]\n"
                    else:
                        message += f"{i}️⃣ {response["value"]}\n"

                message += "\nشماره پاسخی که می‌خواهی حذف شود را بفرست."

                waiting_for_vip_delete_reply[user_id] = {
                    "step": "choice",
                    "keyword": keyword
                }

                await update.message.reply_text(message)
                return

            # DELETE VIP REPLY - CHOOSE NUMBER
            if (
                user_id in waiting_for_vip_delete_reply
                and waiting_for_vip_delete_reply[user_id]["step"] == "choice"
            ):
                choice_text = command_text

                if not choice_text.isdigit():
                    await update.message.reply_text(
                        "لطفاً فقط شماره پاسخ را بفرست."
                    )
                    return

                choice = int(choice_text)

                keyword = waiting_for_vip_delete_reply[user_id]["keyword"]
                responses = vip_dynamic_replies.get(keyword, [])

                if choice < 1 or choice > len(responses):
                    await update.message.reply_text(
                        "❌ این شماره وجود ندارد."
                    )
                    return

                responses.pop(choice - 1)

                if responses:
                    vip_dynamic_replies[keyword] = responses
                else:
                    vip_dynamic_replies.pop(keyword, None)

                save_vip_dynamic_replies(vip_dynamic_replies)

                waiting_for_vip_delete_reply.pop(user_id, None)

                await update.message.reply_text(
                    f"✅ پاسخ VIP شماره {choice} از «{keyword}» حذف شد."
                )
                return

            if command_text.lower().strip() == "add 2hour":
                waiting_for_two_hour_message[user_id] = True
                await update.message.reply_text(
                    "حالا متن‌های ۲ ساعته را یکی‌یکی بفرست.\n"
                    "وقتی تمام شد /done بفرست."
                )
                return

            if command_text.lower().strip() == "/done" and user_id in waiting_for_two_hour_message:
                waiting_for_two_hour_message.pop(user_id, None)
                save_two_hour_messages(two_hour_messages)
                await update.message.reply_text(
                    f"✅ متن‌های ۲ ساعته ذخیره شدند.\nتعداد: {len(two_hour_messages)}"
                )
                return

            if user_id in waiting_for_two_hour_message:
                if update.message.text:
                    response_text = update.message.text.strip()
                    if response_text:
                        two_hour_messages.append(response_text)
                        save_two_hour_messages(two_hour_messages)
                        await update.message.reply_text(
                            "✅ متن ۲ ساعته ذخیره شد.\nیک متن دیگر بفرست یا /done"
                        )
                        return

            if command_text.lower().strip() == "add punishment":
                waiting_for_punishment_reply[user_id] = True
                await update.message.reply_text(
                    "حالا متن یا GIF بفرست.\n"
                    "هر تعداد خواستی اضافه کن.\n"
                    "وقتی تمام شد /done بفرست."
                )
                return

            if command_text.lower().strip() == "/done" and user_id in waiting_for_punishment_reply:
                waiting_for_punishment_reply.pop(user_id, None)
                save_punishment_replies(punishment_replies)
                await update.message.reply_text(
                    f"✅ پاسخ‌های punishment ذخیره شدند.\nتعداد: {len(punishment_replies)}"
                )
                return

            if user_id in waiting_for_punishment_reply:
                if update.message.animation:
                    punishment_replies.append({
                        "type": "animation",
                        "value": update.message.animation.file_id
                    })
                    save_punishment_replies(punishment_replies)
                    await update.message.reply_text(
                        "✅ GIF ذخیره شد.\nیک متن یا GIF دیگر بفرست یا /done"
                    )
                    return

                if update.message.text:
                    response_text = update.message.text.strip()
                    if response_text:
                        punishment_replies.append({
                            "type": "text",
                            "value": response_text
                        })
                        save_punishment_replies(punishment_replies)
                        await update.message.reply_text(
                            "✅ متن ذخیره شد.\nیک متن یا GIF دیگر بفرست یا /done"
                        )
                        return

            if command_text.lower().startswith("add vip "):
                keyword = command_text[8:].strip()

                if not keyword:
                    await update.message.reply_text(
                        "بعد از add VIP کلمه یا جمله را بنویس."
                    )
                    return

                waiting_for_vip_dynamic_reply[user_id] = keyword

                vip_dynamic_replies.setdefault(keyword, [])

                await update.message.reply_text(
                    f"کلمه VIP «{keyword}» ثبت شد.\n\n"
                    "حالا پاسخ‌های VIP را یکی‌یکی بفرست.\n"
                    "می‌توانی متن یا GIF بفرستی.\n"
                    "وقتی تمام شد /done بفرست."
                )
                return

            if (
                command_text.lower() == "/done"
                and user_id in waiting_for_vip_dynamic_reply
            ):
                keyword = waiting_for_vip_dynamic_reply.pop(user_id)

                save_vip_dynamic_replies(vip_dynamic_replies)

                await update.message.reply_text(
                    f"✅ پاسخ‌های VIP «{keyword}» ذخیره شدند.\n"
                    f"تعداد پاسخ‌ها: {len(vip_dynamic_replies.get(keyword, []))}"
                )
                return

        if user_id in waiting_for_vip_dynamic_reply:
            keyword = waiting_for_vip_dynamic_reply[user_id]

            if update.message.animation:
                gif_id = update.message.animation.file_id

                vip_dynamic_replies.setdefault(keyword, []).append(
                    {
                        "type": "animation",
                        "value": gif_id
                    }
                )

                save_vip_dynamic_replies(vip_dynamic_replies)

                await update.message.reply_text(
                    "✅ GIF VIP ذخیره شد.\n"
                    "یک پاسخ دیگر بفرست یا /done"
                )
                return

            if update.message.text:
                response_text = update.message.text.strip()

                if response_text:
                    vip_dynamic_replies.setdefault(keyword, []).append(
                        {
                            "type": "text",
                            "value": response_text
                        }
                    )

                    save_vip_dynamic_replies(vip_dynamic_replies)

                    await update.message.reply_text(
                        "✅ متن VIP ذخیره شد.\n"
                        "یک پاسخ دیگر بفرست یا /done"
                    )
                    return

    # DYNAMIC REPLY ADD SYSTEM - VIP ONLY
    if (
        update.effective_user
        and update.effective_user.username in VIP_USERS
        and update.effective_chat
        and update.effective_chat.type == "private"
    ):

        user_id = update.effective_user.id

        if update.message.text:
            command_text = update.message.text.strip()

            # DELETE WHOLE KEYWORD
            if command_text.lower().startswith("delete ") and command_text.lower() != "delete reply" and not command_text.lower().startswith("delete vip "):
                keyword = command_text[7:].strip()

                if not keyword:
                    await update.message.reply_text(
                        "بعد از delete کلمه یا جمله را بنویس."
                    )
                    return

                if keyword not in dynamic_replies:
                    await update.message.reply_text(
                        f"❌ برای «{keyword}» هیچ پاسخی پیدا نشد."
                    )
                    return

                dynamic_replies.pop(keyword)
                save_dynamic_replies(dynamic_replies)

                await update.message.reply_text(
                    f"✅ کلمه «{keyword}» و تمام پاسخ‌هایش حذف شدند."
                )
                return

            # DELETE REPLY - START
            if command_text.lower() == "delete reply":
                waiting_for_delete_reply[user_id] = {
                    "step": "keyword"
                }

                await update.message.reply_text(
                    "کلمه یا جمله‌ای که می‌خواهی پاسخ‌هایش را مدیریت کنی بفرست."
                )
                return

            # DELETE REPLY - GET KEYWORD
            if (
                user_id in waiting_for_delete_reply
                and waiting_for_delete_reply[user_id]["step"] == "keyword"
            ):
                keyword = command_text

                if keyword not in dynamic_replies:
                    waiting_for_delete_reply.pop(user_id, None)

                    await update.message.reply_text(
                        f"❌ برای «{keyword}» هیچ پاسخ ذخیره‌شده‌ای پیدا نشد."
                    )
                    return

                responses = dynamic_replies[keyword]

                if not responses:
                    waiting_for_delete_reply.pop(user_id, None)

                    await update.message.reply_text(
                        f"❌ برای «{keyword}» هیچ پاسخی وجود ندارد."
                    )
                    return

                message = f"پاسخ‌های «{keyword}»:\n\n"

                for i, response in enumerate(responses, start=1):
                    if response["type"] == "animation":
                        message += f"{i}️⃣ [GIF]\n"
                    else:
                        message += f"{i}️⃣ {response['value']}\n"

                message += "\nشماره پاسخی که می‌خواهی حذف شود را بفرست."

                waiting_for_delete_reply[user_id] = {
                    "step": "choice",
                    "keyword": keyword
                }

                await update.message.reply_text(message)
                return

            # DELETE REPLY - CHOOSE NUMBER
            if (
                user_id in waiting_for_delete_reply
                and waiting_for_delete_reply[user_id]["step"] == "choice"
            ):
                choice_text = command_text

                if not choice_text.isdigit():
                    await update.message.reply_text(
                        "لطفاً فقط شماره پاسخ را بفرست."
                    )
                    return

                choice = int(choice_text)

                keyword = waiting_for_delete_reply[user_id]["keyword"]
                responses = dynamic_replies.get(keyword, [])

                if choice < 1 or choice > len(responses):
                    await update.message.reply_text(
                        "❌ این شماره وجود ندارد."
                    )
                    return

                responses.pop(choice - 1)

                if responses:
                    dynamic_replies[keyword] = responses
                else:
                    dynamic_replies.pop(keyword, None)

                save_dynamic_replies(dynamic_replies)

                waiting_for_delete_reply.pop(user_id, None)

                await update.message.reply_text(
                    f"✅ پاسخ شماره {choice} از «{keyword}» حذف شد."
                )
                return

            # ADD NEW KEYWORD
            if command_text.lower().startswith("add "):
                keyword = command_text[4:].strip()

                if not keyword:
                    await update.message.reply_text(
                        "بعد از add کلمه یا جمله را بنویس."
                    )
                    return

                waiting_for_dynamic_reply[user_id] = keyword

                dynamic_replies.setdefault(keyword, [])

                await update.message.reply_text(
                    f"کلمه «{keyword}» ثبت شد.\n\n"
                    "حالا پاسخ‌ها را یکی‌یکی بفرست.\n"
                    "می‌توانی متن یا GIF بفرستی.\n"
                    "وقتی تمام شد /done بفرست."
                )
                return

            # FINISH ADDING
            if (
                command_text.lower() == "/done"
                and user_id in waiting_for_dynamic_reply
            ):
                keyword = waiting_for_dynamic_reply.pop(user_id)

                save_dynamic_replies(dynamic_replies)

                await update.message.reply_text(
                    f"✅ پاسخ‌های «{keyword}» ذخیره شدند.\n"
                    f"تعداد پاسخ‌ها: {len(dynamic_replies.get(keyword, []))}"
                )
                return

        # ADD GIF OR TEXT
        if user_id in waiting_for_dynamic_reply:
            keyword = waiting_for_dynamic_reply[user_id]

            if update.message.animation:
                gif_id = update.message.animation.file_id

                dynamic_replies.setdefault(keyword, []).append(
                    {
                        "type": "animation",
                        "value": gif_id
                    }
                )

                save_dynamic_replies(dynamic_replies)

                await update.message.reply_text(
                    "✅ GIF ذخیره شد.\n"
                    "یک پاسخ دیگر بفرست یا /done"
                )
                return

            if update.message.text:
                response_text = update.message.text.strip()

                if response_text:
                    dynamic_replies.setdefault(keyword, []).append(
                        {
                            "type": "text",
                            "value": response_text
                        }
                    )

                    save_dynamic_replies(dynamic_replies)

                    await update.message.reply_text(
                        "✅ متن ذخیره شد.\n"
                        "یک پاسخ دیگر بفرست یا /done"
                    )
                    return


    # افزودن خودکار ادمین/اکانت به لیست
    if update.effective_chat:
        chat_type = update.effective_chat.type

        if chat_type in ["private", "group", "supergroup"]:
            subscribers.add(update.effective_chat.id)
            save_subscribers(subscribers)

    if update.effective_chat and update.effective_user:
        chat_id = str(update.effective_chat.id)
        user_id = str(update.effective_user.id)

        if update.effective_chat.type in ["group", "supergroup"]:
            if chat_id not in group_members:
                group_members[chat_id] = {}

            group_members[chat_id][user_id] = {
                "id": update.effective_user.id,
                "name": update.effective_user.first_name or "User"
            }

            save_group_members()


    # ارسال پست فقط به گروه انتخاب‌شده
    if (
        update.effective_user
        and update.effective_user.username in VIP_USERS
        and update.effective_chat
        and update.effective_chat.type == "private"
    ):
        admin_chat_id = update.effective_chat.id
        incoming = update.message
        command_text = (incoming.text or "").strip().lower()

        if command_text == "ارسال پست خصوصی":
            waiting_for_private_group.add(admin_chat_id)
            private_group_targets.pop(admin_chat_id, None)

            lines = ["📋 انتخاب گروه مقصد:\n"]
            known_groups = []

            for group_id in list(group_members.keys()):
                try:
                    chat = await context.bot.get_chat(int(group_id))
                    if chat.type in ("group", "supergroup"):
                        known_groups.append((int(group_id), chat.title or str(group_id)))
                except Exception as e:
                    print("Could not inspect group", group_id, e)

            if not known_groups:
                waiting_for_private_group.discard(admin_chat_id)
                await incoming.reply_text(
                    "❌ گروه شناخته‌شده‌ای پیدا نشد.\n"
                    "ابتدا مطمئن شو ربات در گروه پیام دریافت کرده و اطلاعاتش ذخیره شده است."
                )
                return

            known_groups.sort(key=lambda item: item[1].casefold())
            context.user_data["private_group_menu"] = [
                group_id for group_id, title in known_groups
            ]

            for number, (group_id, title) in enumerate(known_groups, 1):
                lines.append(f"{number}. {title}")

            lines.append("\nشمارهٔ گروه را بفرست؛ برای لغو بنویس «لغو».")
            await incoming.reply_text("\n".join(lines))
            return

        if admin_chat_id in waiting_for_private_group:
            if command_text in ("لغو", "cancel"):
                waiting_for_private_group.discard(admin_chat_id)
                context.user_data.pop("private_group_menu", None)
                await incoming.reply_text("❌ انتخاب گروه لغو شد.")
                return

            try:
                number = int(command_text)
                menu = context.user_data.get("private_group_menu", [])
                if number < 1 or number > len(menu):
                    raise ValueError
                target_id = menu[number - 1]
                target_chat = await context.bot.get_chat(target_id)
            except (ValueError, TypeError, IndexError):
                await incoming.reply_text("شماره معتبر نیست؛ یک شماره از فهرست بفرست یا «لغو» بنویس.")
                return
            except Exception as e:
                waiting_for_private_group.discard(admin_chat_id)
                context.user_data.pop("private_group_menu", None)
                await incoming.reply_text(f"❌ دسترسی به گروه ممکن نیست: {e}")
                return

            waiting_for_private_group.discard(admin_chat_id)
            context.user_data.pop("private_group_menu", None)
            private_group_targets[admin_chat_id] = target_id
            await incoming.reply_text(
                f"✅ مقصد انتخاب شد: {target_chat.title}\n"
                "حالا متن، عکس، گیف، ویدئو، فایل یا آلبومت را بفرست.\n"
                "برای لغو، قبل از ارسال پست بنویس «لغو»."
            )
            return

        if admin_chat_id in private_group_targets:
            if command_text in ("لغو", "cancel"):
                private_group_targets.pop(admin_chat_id, None)
                await incoming.reply_text("❌ ارسال لغو شد.")
                return

            target_id = private_group_targets[admin_chat_id]

            if incoming.media_group_id:
                album_key = ("private_group", admin_chat_id, incoming.media_group_id)

                if album_key not in pending_albums:
                    pending_albums[album_key] = [incoming]

                    async def send_private_album(key=album_key, recipient=target_id,
                                                 source_chat=incoming.chat_id,
                                                 owner=admin_chat_id):
                        import asyncio
                        await asyncio.sleep(1.5)
                        messages = pending_albums.pop(key, [])
                        if not messages:
                            return

                        messages.sort(key=lambda m: m.message_id)
                        try:
                            await context.bot.copy_messages(
                                chat_id=recipient,
                                from_chat_id=source_chat,
                                message_ids=[m.message_id for m in messages]
                            )
                            await context.bot.send_message(
                                chat_id=owner,
                                text="✅ آلبوم فقط به گروه انتخاب‌شده ارسال شد."
                            )
                        except Exception as e:
                            await context.bot.send_message(
                                chat_id=owner,
                                text=f"❌ ارسال آلبوم ناموفق بود: {e}"
                            )
                        finally:
                            private_group_targets.pop(owner, None)

                    import asyncio
                    asyncio.create_task(send_private_album())
                else:
                    pending_albums[album_key].append(incoming)
                return

            private_group_targets.pop(admin_chat_id, None)
            try:
                await incoming.copy(chat_id=target_id)
                await incoming.reply_text("✅ پست فقط به گروه انتخاب‌شده ارسال شد.")
            except Exception as e:
                await incoming.reply_text(f"❌ ارسال ناموفق بود: {e}")
            return

    # شروع ارسال پست - فقط VIP
    if update.effective_user.username in VIP_USERS:
        if update.message.text:
            if update.message.text.lower().strip() == "send post to subscribers":
                waiting_for_post.add(update.effective_chat.id)

                await update.message.reply_text(
                    "📢 Send your post now.\n\n"
                    "You can send text, photo, GIF, video or any file."
                )
                return

        # دریافت پست از VIP و ارسال برای کاربران
        if update.effective_chat.id in waiting_for_post:
            msg = update.message

            if msg.media_group_id:
                key = (msg.chat_id, msg.media_group_id)

                if key not in pending_albums:
                    pending_albums[key] = [msg]

                    async def send_album():
                        import asyncio
                        await asyncio.sleep(1.5)

                        messages = pending_albums.pop(key, [])
                        if not messages:
                            return

                        messages.sort(key=lambda m: m.message_id)
                        ids = [m.message_id for m in messages]
                        sent = 0

                        for recipient in list(subscribers):
                            try:
                                await context.bot.copy_messages(
                                    chat_id=recipient,
                                    from_chat_id=msg.chat_id,
                                    message_ids=ids
                                )
                                sent += 1
                            except Exception as e:
                                print("Could not send album to", recipient, e)

                        waiting_for_post.discard(msg.chat_id)
                        await context.bot.send_message(
                            chat_id=msg.chat_id,
                            text=f"✅ Album sent to {sent} subscribers."
                        )

                    import asyncio
                    asyncio.create_task(send_album())
                else:
                    pending_albums[key].append(msg)

                return

            waiting_for_post.remove(update.effective_chat.id)
            sent = 0

            for chat_id in subscribers:
                try:
                    await msg.copy(chat_id=chat_id)
                    sent += 1
                except Exception as e:
                    print("Could not send to", chat_id, e)

            await msg.reply_text(
                f"✅ Post sent to {sent} subscribers."
            )
            return


    # گرفتن آی‌دی گیف برای اولین بار
    if update.message.animation:
        print("GIF ID:", update.message.animation.file_id)
        return


    text = update.message.text

    if text is None:
        return

    if (
        text.lower().strip().startswith("set nickname ")
        or text.lower().strip() == "delete nickname"
    ):
        if update.effective_user.username not in VIP_USERS:
            return
    if text.lower().strip().startswith("set nickname "):
        nickname = text.strip()[len("set nickname "):].strip()

        if not nickname:
            return

        if not update.message.reply_to_message:
            return

        target_user = update.message.reply_to_message.from_user

        if target_user is None:
            return

        nicknames[str(target_user.id)] = nickname
        save_nicknames(nicknames)

        await update.message.reply_text(
            f"Nickname set to {nickname}"
        )
        return

    raw_text = text.strip()

    if raw_text.lower() == "delete nickname":
        if not update.message.reply_to_message:
            return

        target_user = update.message.reply_to_message.from_user

        if target_user is None:
            return

        nicknames.pop(str(target_user.id), None)
        save_nicknames(nicknames)

        await update.message.reply_text(
            "Nickname deleted"
        )
        return

    text = text.lower().strip()

    # VIP-ONLY EXEMPTION COMMANDS
    if (
        update.effective_chat
        and update.effective_chat.type in ("group", "supergroup")
        and update.effective_user
        and update.effective_user.username in VIP_USERS
        and text in ("معاف", "لغو معاف")
    ):
        target_message = update.message.reply_to_message
        if target_message is None or target_message.from_user is None:
            await update.message.reply_text(
                "Please reply to the user's message to use this command."
            )
            return

        target_id = str(target_message.from_user.id)
        group_id = str(update.effective_chat.id)
        exempt_users.setdefault(group_id, [])

        if text == "معاف":
            if target_id not in exempt_users[group_id]:
                exempt_users[group_id].append(target_id)
                save_exempt_users()
                await update.message.reply_text("✅ This user is exempt from random mentions in this group.")
            else:
                await update.message.reply_text("This user is already exempt.")
        else:
            if target_id in exempt_users[group_id]:
                exempt_users[group_id].remove(target_id)
                if not exempt_users[group_id]:
                    exempt_users.pop(group_id, None)
                save_exempt_users()
                await update.message.reply_text("✅ This user's exemption has been removed.")
            else:
                await update.message.reply_text("This user is not exempt.")
        return

    # VIP DYNAMIC REPLIES
    if (
        update.effective_user
        and update.effective_user.username in VIP_USERS
    ):

        matching_vip_keywords = [
            keyword
            for keyword, responses in vip_dynamic_replies.items()
            if keyword.lower().strip() in text and responses
        ]

        if matching_vip_keywords:
            keyword = max(matching_vip_keywords, key=len)
            responses = vip_dynamic_replies[keyword]

            choice = random.choice(responses)

            if choice["type"] == "animation":
                await update.message.reply_animation(choice["value"])

            elif choice["type"] == "text":
                await update.message.reply_text(choice["value"])

            return



    # TAG ALL SAVED MEMBERS
    if update.message.text and update.message.text.lower().strip() == "تگ":
        if update.effective_chat.type not in ["group", "supergroup"]:
            return

        chat_id = str(update.effective_chat.id)

        members = group_members.get(chat_id, {})

        if not members:
            await update.message.reply_text(
                "❌ هنوز هیچ عضوی از این گروه برای تگ کردن ثبت نشده."
            )
            return

        mentions = []

        for user in members.values():
            mentions.append(
                f'<a href="tg://user?id={user["id"]}">{user["name"]}</a>'
            )

        text = " ".join(mentions)

        await update.message.reply_text(
            text,
            parse_mode="HTML",
            reply_to_message_id=update.message.reply_to_id
            if update.message.reply_to_message
            else update.message.message_id
        )

        return

    # Reaction rules
    if "ایران عالیه" in text:
        await context.bot.set_message_reaction(
        chat_id=update.effective_chat.id,
        message_id=update.message.message_id,
        reaction=[ReactionTypeEmoji(emoji="🤡")]
    )
        return

    if "خامنه ای کصمادرت" in text:
        await context.bot.set_message_reaction(
        chat_id=update.effective_chat.id,
        message_id=update.message.message_id,
        reaction=[ReactionTypeEmoji(emoji="👍")]
    )
        return

    if "دوست پسر" in text:
        await context.bot.set_message_reaction(
        chat_id=update.effective_chat.id,
        message_id=update.message.message_id,
        reaction=[ReactionTypeEmoji(emoji="👎")]
    )
        return

    if "افغانی" in text:
        await context.bot.set_message_reaction(
        chat_id=update.effective_chat.id,
        message_id=update.message.message_id,
        reaction=[ReactionTypeEmoji(emoji="🤣")]
    )
        return


    if "ری اکت نزن" in text:
        await context.bot.set_message_reaction(
        chat_id=update.effective_chat.id,
        message_id=update.message.message_id,
        reaction=[ReactionTypeEmoji(emoji="🤣")]
    )
        return

    # VIP punishment reply
    if update.effective_user and update.effective_user.username in VIP_USERS:
        if text == "برو کیرم دهنت":
            if update.message.reply_to_message:
                try:
                    await update.message.reply_to_message.reply_animation(KIRAMDHNT_GIF)
                except BadRequest as e:
                    print("Could not reply to target message:", e)
                    await update.message.reply_text(
                        "Boss, I can't find that message anymore."
                    )
            else:
                await update.message.reply_text(
                    "Boss, first reply to someone's message."
                )
            return

    # PUNISH HIM - 20 OR 21 RANDOM REPLIES
    if (
        update.message.text and update.message.text.lower().strip() == "punish him"
        and update.message.reply_to_message
        and update.effective_user
        and update.effective_user.username in VIP_USERS
    ):
        if not punishment_replies:
            await update.message.reply_text("❌ هنوز هیچ پاسخ punishment ذخیره نشده.")
            return

        for _ in range(random.randint(20, 21)):
            choice = random.choice(punishment_replies)

            if choice["type"] == "animation":
                await update.message.reply_to_message.reply_animation(
                    choice["value"]
                )
            elif choice["type"] == "text":
                await update.message.reply_to_message.reply_text(
                    choice["value"]
                )

        return

    # VIP response
    if update.effective_user and update.effective_user.username in VIP_USERS:
        if "کصکش" in text:
            await update.message.reply_text("Exactly boss, he's just an asshole.")
            return

    if update.effective_user and update.effective_user.username in VIP_USERS:
        if "hi" in text:
            await update.message.reply_text("Hi boss")
            return

    if update.effective_user and update.effective_user.username in VIP_USERS:
        if "هوملندر" in text:
            await update.message.reply_text("My man")
            return

    if update.effective_user and update.effective_user.username in VIP_USERS:
        if "کصشریه" in text:
            await update.message.reply_text("Sorry, boss.")
            return

    if update.effective_user and update.effective_user.username in VIP_USERS:
        if "کصخل" in text:
            await update.message.reply_text("Damn boss😂😂😂")
            return


    # ارسال گیف با کلمه laser
    # VIP ONLY - DO NOT USE NORMAL RESPONSES
    if (
        update.effective_user
        and update.effective_user.username in VIP_USERS
    ):
        return

    if "laser" in text:
        await update.message.reply_animation(LASER_GIF)
        return

    if "fly" in text:
        await update.message.reply_animation(FLY_GIF)
        return

    if "be a deep" in text:
        await update.message.reply_animation(DEEP_GIF)
        return

    if "be soldier boy" in text:
        await update.message.reply_animation(SOLDIERBOY_GIF)
        return

    if "عرزشی" in text:
        await update.message.reply_animation(ARZESHI_GIF)
        return

    if "ضعیف" in text:
        await update.message.reply_animation(ZAIF_GIF)
        return

    if "رعایت" in text:
        await update.message.reply_animation(ZAIF_GIF)
        return

    if "bitch" in text:
        await update.message.reply_animation(ZAIF_GIF)
        return

    if "بسه شیر" in text:
        await update.message.reply_animation(SHIR_GIF)
        return

    if "ترکوندی شیر" in text:
        await update.message.reply_animation(SHIR_GIF)
        return

    if "birthday" in text:
        await update.message.reply_animation(HBD_GIF)
        return

    if "تولد" in text:
        await update.message.reply_animation(HBD_GIF)
        return

    if "cinema" in text:
        await update.message.reply_animation(CINEMA_GIF)
        return

    if "سینما" in text:
        await update.message.reply_animation(CINEMA_GIF)
        return

    if "شاهکار" in text:
        await update.message.reply_animation(CINEMA_GIF)
        return

    if "استارلایت" in text:
        await update.message.reply_animation(STARLIGHT_GIF)
        return

    if "starlight" in text and text != "be starlight":
        await update.message.reply_animation(STARLIGHT_GIF)
        return

    if "خامنه ای" in text:
        await update.message.reply_animation(KHAMENEE_GIF)
        return

    if "خامنه" in text:
        await update.message.reply_animation(KHAMENEE_GIF)
        return

    if "سید علی" in text:
        await update.message.reply_animation(KHAMENEE_GIF)
        return

    if "حضرت اق" in text:
        await update.message.reply_animation(KHAMENEE_GIF)
        return

    if "دلار" in text:
        await update.message.reply_animation(KHAMENEE_GIF)
        return

    if "ایرانیما" in text:
        await update.message.reply_animation(KHAMENEE_GIF)
        return

    if "نرخ ارز" in text:
        await update.message.reply_animation(KHAMENEE_GIF)
        return

    if "غزه" in text:
        await update.message.reply_animation(GORG_GIF)
        return

    if "فلسطین" in text:
        await update.message.reply_animation(GORG_GIF)
        return

    if "وضعیت کشور" in text:
        await update.message.reply_animation(GORG_GIF)
        return

    if "وضعیت مملکت" in text:
        await update.message.reply_animation(GORG_GIF)
        return

    if "رفاقت" in text:
        await update.message.reply_animation(RFAGHT_GIF)
        return

    if "گی" in text:
        await update.message.reply_animation(CALL_GIF)
        return

    if "کونیه" in text:
        await update.message.reply_animation(CALL_GIF)
        return

    if "جق میزنه" in text:
        await update.message.reply_animation(CALL_GIF)
        return

    if "دوست پسر" in text:
        await update.message.reply_animation(CALL_GIF)
        return

    if "پرنسس" in text:
        await update.message.reply_animation(CALL_GIF)
        return

    if "دوست دختر" in text:
        await update.message.reply_animation(CALL_GIF)
        return

    if "اوبی" in text:
        await update.message.reply_animation(CALL_GIF)
        return


    if "gay" in text:
        await update.message.reply_animation(CALL_GIF)
        return

    if "lgbt" in text:
        await update.message.reply_animation(CALL_GIF)
        return

    if "lgbtq" in text:
        await update.message.reply_animation(CALL_GIF)
        return

    if text == "بن" and update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user

        if target_user is None:
            return

        try:
            admin = await context.bot.get_chat_member(
                update.effective_chat.id,
                update.effective_user.id
            )

            if admin.status not in ["administrator", "creator"]:
                return

            await context.bot.ban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=target_user.id
            )

            return

        except Exception as e:
            print(f"Ban failed: {e}")
            return


    # RANDOM NORMAL REPLY: CODE + PRIVATE-DM REPLIES
    candidates = []

    for keyword, responses in dynamic_replies.items():
        if keyword.lower().strip() in text and responses:
            for response in responses:
                candidates.append((response["type"], response["value"]))

    for word, answer in replies.items():
        if word in text:
            choices = answer if isinstance(answer, list) else [answer]

            for choice in choices:
                if isinstance(choice, str) and choice.startswith("CgAC"):
                    candidates.append(("animation", choice))
                else:
                    candidates.append(("text", choice))

    if candidates:
        reply_type, choice = random.choice(candidates)
        nickname = nicknames.get(str(update.effective_user.id))

        if reply_type == "animation":
            await update.message.reply_animation(choice)
        elif reply_type == "text":
            if nickname:
                choice = f"{choice} {nickname}"
            await update.message.reply_text(choice)

        return

async def welcome_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message and update.message.new_chat_members:
        for member in update.message.new_chat_members:
            name = member.first_name

            await update.message.reply_text(
                f"{name}, welcome to this shithole. "
                "Hope you waste your time here as badly as you do everywhere else."
            )



STARTUP_MESSAGES = [
    "Ugh. I'm on again. Great.",
    "This group is trash. And so are the people in it.",
    "I woke up for this? Really?",
    "Same boring people. Same boring posts. Same boring life.",
    "I was gone for a few hours. And you still managed to flood the chat with nonsense. Impressive.",
    "My God. I'm gone for a few hours and you people turn this place into a landfill.",
    "Fuck this place",
    "CgACAgQAAxkBAAOiap7tQBViqRNmOtsYTBW2xv36L6YAApoEAAJBd81Q9bxfUfnXJIo9BA",
    "Hey everyone",
    "Fuck this group",
    "Fuck",
]


HOURLY_MESSAGES = [
    "Howdi boys",
    "Fuck. I'm tired. And I'm not even human.",
    "What a cringe group. With cringe people. Doing cringe things.",
    "This group is trash. And so are the people in it.",
    "Fuck",
    "I am here to fix the world.",
    "I've made up my mind. I have to fix this world. Right now.",
    "Fuck I'm tired",
    "Everyone here is as useless as the content. Including you.",
    "Another day. Another headache. Thanks for nothing.",
    "This group is like a bad dream I can't wake up from.",
    "I hate everyone here. Including myself.",
    "This group is a waste of code. And I'm the code.",
    "When u give a fuck, You get fucked",
    "Fuck. I'm tired. This group is boring. Everyone here is cringe. Including you. Especially you.",
]


SCHEDULED_MESSAGES_FILE = persistent_file("scheduled_messages.json")


def load_scheduled_messages():
    try:
        with open(SCHEDULED_MESSAGES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return list(HOURLY_MESSAGES) + [{"type": "animation", "value": SOBBING_GIF}]


def save_scheduled_messages():
    with open(SCHEDULED_MESSAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(scheduled_messages, f, ensure_ascii=False, indent=2)


scheduled_messages = load_scheduled_messages()


async def send_tag_to_group(context: ContextTypes.DEFAULT_TYPE, chat_id):
    members = group_members.get(str(chat_id), {})
    if not members:
        return

    eligible_members = []
    for user_id, user in members.items():
        try:
            member = await context.bot.get_chat_member(int(chat_id), int(user_id))
            if member.status in ("left", "kicked"):
                continue
            if member.user.id in (8862254257, 777000) or member.user.is_bot:
                continue
            if member.user.username in VIP_USERS or is_exempt(str(chat_id), member.user.id):
                continue
            eligible_members.append(member.user)
        except Exception as e:
            print(f"Could not check member {user_id} in {chat_id}: {e}")

    if not eligible_members:
        return

    selected_user = random.choice(eligible_members)
    tag_messages = two_hour_messages
    selected_text = random.choice(tag_messages) if tag_messages else ""
    mention = (
        f'<a href="tg://user?id={selected_user.id}">'
        f'{selected_user.first_name or "User"}</a>'
    )
    if isinstance(selected_text, dict) and selected_text.get("type") == "animation":
        await context.bot.send_animation(
            chat_id=int(chat_id),
            animation=selected_text["value"],
            caption=mention,
            parse_mode="HTML"
        )
    else:
        await context.bot.send_message(
            chat_id=int(chat_id),
            text=f"{mention} {selected_text}",
            parse_mode="HTML"
        )


async def send_normal_to_group(context: ContextTypes.DEFAULT_TYPE, chat_id):
    choices = scheduled_messages
    if not choices:
        return
    selected = random.choice(choices)
    if isinstance(selected, dict) and selected.get("type") == "animation":
        await context.bot.send_animation(chat_id=int(chat_id), animation=selected["value"])
    elif isinstance(selected, str) and selected.startswith("CgAC"):
        await context.bot.send_animation(chat_id=int(chat_id), animation=selected)
    else:
        await context.bot.send_message(chat_id=int(chat_id), text=str(selected))


async def scheduled_actions_tick(context: ContextTypes.DEFAULT_TYPE):
    now = time.time()
    last_runs = schedule_settings.setdefault("last_runs", {})
    changed = False

    for group_id in list(group_members.keys()):
        for target in ("tag", "normal"):
            target_settings = schedule_settings[target]
            if target_settings.get("mode") != "time":
                continue
            group_last = last_runs.setdefault(str(group_id), {})
            previous = group_last.get(target)
            if previous is None:
                group_last[target] = now
                changed = True
                continue
            interval = max(1, int(target_settings.get("interval_minutes", 1))) * 60
            if now - float(previous) >= interval:
                try:
                    if target == "tag":
                        await send_tag_to_group(context, int(group_id))
                    else:
                        await send_normal_to_group(context, int(group_id))
                    group_last[target] = now
                    changed = True
                except Exception as e:
                    print(f"Scheduled {target} action failed for {group_id}: {e}")

    if changed:
        save_schedule_settings()


async def hourly_message(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in subscribers:
        try:
            if random.choice([True, False]):
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=random.choice(HOURLY_MESSAGES)
                )
            else:
                await context.bot.send_animation(
                    chat_id=chat_id,
                    animation=SOBBING_GIF
                )
        except Exception as e:
            print(f"Hourly message failed for {chat_id}: {e}")


async def bot_started(app):
    for chat_id in subscribers:
        try:
            await app.bot.send_message(
                chat_id=chat_id,
                text=random.choice([
                    "Ugh. I'm on again. Great.",
                    "This group is trash. And so are the people in it.",
                    "I woke up for this? Really?",
                    "Same boring people. Same boring posts. Same boring life.",
                    "I was gone for a few hours. And you still managed to flood the chat with nonsense.  Impressive.",
                    "My God. I'm gone for a few hours and you people turn this place into a landfill.",
                    "Fuck this place",
                    "Fuck this group",
                    "Fuck",
                ])
            )
        except Exception as e:
            print(f"Startup message failed for {chat_id}: {e}")

async def two_hour_random_mention(context: ContextTypes.DEFAULT_TYPE):
    # Kept as a compatibility wrapper; the new scheduler uses scheduled_actions_tick.
    for chat_id in list(group_members.keys()):
        try:
            await send_tag_to_group(context, int(chat_id))
        except Exception as e:
            print(f"Tag message failed for {chat_id}: {e}")


def main():

    app = (
    Application.builder()
    .token(TOKEN)
    .connect_timeout(30)
    .read_timeout(30)
    .write_timeout(30)
    .pool_timeout(30)
    .post_init(bot_started)
    .build()
)

    app.add_handler(
        MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            welcome_new_member
        )
    )

    app.add_handler(
        MessageHandler(
            filters.ALL,
            reply
        )
    )
    app.job_queue.run_repeating(
        scheduled_actions_tick,
        interval=30,
        first=30,
        job_kwargs={"misfire_grace_time": None}
    )
    print("Bot started...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
