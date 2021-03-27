####


from telethon import TelegramClient, sync
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from collections import OrderedDict
from os import path, stat, remove, makedirs

import json

####


# Mijoz parametrlari
API_ID   = ''
API_HASH = '
PHONE_NUM    =''

# chat _link
CHAT_LINK  = ""

#####

### Telegramning asosiy funktsiyalari ###

# Telegram API-ga ulaning va tizimga kirish / tizimdan chiqish
def tlg_connect(api_id, api_hash, phone_number):
	'' 'Telegram API-ga ulanish va tizimga kirish / tizimga kirish. Birinchi ijro uchun tizimga kirish kodini sorang '' '
	print('Telegramga ulanishga harakat qilinmoqda ...')
	client = TelegramClient("Session", api_id, api_hash)
	if not client.start():
		print('Telegram serverlariga ulanib bolmadi.')
		return None
	else:
		if not client.is_user_authorized():
			print('Sessiya fayli topilmadi. Bu birinchi sorov, kod sorovini yuborish ...')
			client.sign_in(phone_number)
			self_user = None
			while self_user is None:
				code = input('Siz olgan kodni kiriting: ')
				try:
					self_user = client.sign_in(code=code)
				except SessionPasswordNeededError:
					pw = getpass('Ikki bosqichli tekshiruv yoqilgan. Parolingizni kiriting: ')
					self_user = client.sign_in(password=pw)
					if self_user is None:
						return None
	print('Mmuvaffaqiyatli kirildi.')
	print()
	return client


# Suhbatdan asosiy ma'lumotlarni olish
def tlg_get_basic_info(client, chat):
	'''Guruh / kanal / suhbatdan asosiy ma'lumotlarni (id, sarlavha, ism, raqamlar) olish'''
	# Tegishli suhbat mavjudligini olish
	chat_entity = client.get_entity(chat)
	# Suhbatdagi foydalanuvchilar sonini olish
	num_members_offset = client(GetParticipantsRequest(channel=chat_entity, \
		filter=ChannelParticipantsSearch(''), offset=0, limit=0, hash=0)).count
	num_members = client(GetParticipantsRequest(channel=chat_entity, \
		filter=ChannelParticipantsSearch(''), offset=num_members_offset, limit=0, hash=0)).count
	# Suhbatdagi xabarlar ma'lumotlarini olish va suhbat bilan bog'liq foydali ma'lumotlarni chiqarib olish
	msgs = client.get_messages(chat_entity, limit=1)
	basic_info = OrderedDict \
		([ \
			("id", msgs[0].chat_id), \
			("title", msgs[0].chat.title), \
			("username", msgs[0].chat.username), \
			("num_members", num_members), \
			("num_messages", msgs.total), \
			("supergroup", msgs[0].chat.megagroup) \
		])
	# Asosiy ma'lumot diktasini qaytarish
	return basic_info

 # Suhbatdan xabarlar ma'lumotlarini olish
def tlg_get_messages(client, chat, num_msg):
	'''Get all members information from a group/channel/chat'''
	# Natijalar ro'yxatini o'rnatish
	messages = []
	# Tegishli suhbatlar mavjudligini olish
	chat_entity = client.get_entity(chat)
	# Xabarlar ma'lumotlarini bitta ro'yxatga olish va saqlash
	msgs = client.get_messages(chat_entity, limit=num_msg)
	# Xabarlar tuzilmalarini yaratish va ularni ro'yxatga qo'shish
	for msg in reversed(msgs.data):
		msg_sender = msg.sender.first_name
		if msg.sender.last_name:
			msg_sender = "{} {}".format(msg_sender, msg.sender.last_name)
		if msg.sender.username:
			msg_sender = "{} ({})".format(msg_sender, msg.sender.username)
		msg_sent_date = "{}/{}/{}".format(msg.date.day, msg.date.month, msg.date.year)
		msg_sent_time = "{}:{}:{}".format(msg.date.hour, msg.date.minute, msg.date.second)
		msg_data = OrderedDict \
			([ \
				("id", msg.id), ("text", msg.message), 
				("sender_user_id", msg.sender.id), ("reply_to", msg.reply_to_msg_id) \
			])
		messages.append(msg_data)
	# Bizning xabarlarimiz tuzilmalarini yaratish va ularni ro'yxatga olish
	return messages


# Barcha xabarlarni suhbatdan olish
def tlg_get_all_messages(client, chat):
	'''Guruh / kanal / chat orqali barcha a'zolarning ma'lumotlarini olish'''
	# Natijalar ro'yxatini o'rnatish
	messages = []
	# Tegishli suhbat mavjudligini olish
	chat_entity = client.get_entity(chat)
	# Barcha xabarlarni bitta ro'yxatda olish va saqlash
	num_msg = client.get_messages(chat_entity, limit=1).total
	msgs = client.get_messages(chat_entity, limit=num_msg)
	# Bizning xabarlarimiz tuzilmalarini yaratish va ularni ro'yxatga qo'shish
	for msg in reversed(msgs):
		msg_sender = msg.sender.first_name
		if msg.sender.last_name:
			msg_sender = "{} {}".format(msg_sender, msg.sender.last_name)
		if msg.sender.username:
			msg_sender = "{} (@{})".format(msg_sender, msg.sender.username)
		msg_sent_date = "{}/{}/{}".format(msg.date.day, msg.date.month, msg.date.year)
		msg_sent_time = "{}:{}:{}".format(msg.date.hour, msg.date.minute, msg.date.second)
		msg_data = OrderedDict \
			([ \
				("id", msg.id), ("text", msg.message),  \
				("sender_user_id", msg.sender.id), ("reply_to", msg.reply_to_msg_id) \
			])
		messages.append(msg_data)
	# Xabarlar ma'lumotlar ro'yxatini qaytarish
	return messages

####################################################################################################

### Json fayli funktsiyalarni bajaradi ###

def json_write(file, data):
	'''JSON fayli tarkibiga element ma'lumotlarini yozish'''
	# Ma'lumotlarni bo'sh ro'yxatga qo'shish va write_list funktsiyasini bajarishdan foydalanish
	data_list = []
	data_list.append(data)
	json_write_list(file, data_list)


def json_write_list(file, list):
	'''Barcha ro'yxat elementlarini ma'lumotlarni JSON fayli tarkibiga yozish'''
	try:
		# Agar ular mavjud bo'lmasa, fayl yo'lining kataloglarini yarating
		directory = path.dirname(file)
		if not path.exists(directory):
			makedirs(directory)
		# Agar fayl mavjud bo'lmasa yoki bo'sh bo'lsa, JSON tarkib skeletini yozish
		if not path.exists(file) or not stat(file).st_size:
			with open(file, "w", encoding="utf-8") as f:
				f.write('\n{\n    "Content": []\n}\n')
		# Fayl tarkibini o'qish
		with open(file, "r", encoding="utf-8") as f:
			content = json.load(f, object_pairs_hook=OrderedDict)
		# Ro'yxatdagi har bir ma'lumot uchun json tarkibiga qo'shish
		for data in list:
			if data:
				content['Content'].append(data) 
		# O'zgartirilgan tarkib ma'lumotlari bilan JSON faylini qayta yozish
		with open(file, "w", encoding="utf-8") as f:
			json.dump(content, fp=f, ensure_ascii=False, indent=4)
	# Xatolarni ushlash va ko'rib chiqish
	except IOError as e:
		print("    I/O error({0}): {1}".format(e.errno, e.strerror))
	except ValueError:
		print("    Error: Faylga yozish uchun ma'lumot qiymatini o'zgartirib bo'lmaydi")
	except MemoryError:
		print("    Error: Siz juda ko'p ma'lumot yozishga harakat qilyapsiz")

#####

### Asosiy funktsiya ###
def main():
	'''Asosiy funktsiya'''
	print()
	# Mijozni yaratish
	client = tlg_connect(API_ID, API_HASH, PHONE_NUM)
	if client is not None:
    	# Suhbat haqida asosiy ma'lumotni olish
		print('Suhbat haqida asosiy malumot olinmoqda ...')
		chat_info = tlg_get_basic_info(client, CHAT_LINK)

		# JSON fayllarini asosiy ma'lumot chat nomidan yaratish
		if chat_info["username"]:
			files_name = chat_info["username"]
		else:
			files_name = chat_info["id"]
		
		fjson_messages = "./Natijalar/{}/chatlar.json".format(files_name) 

		

		# Suhbatdagi barcha xabarlarni olish va chiqadigan faylga saqlash		
		print('Suhbat xabarlari haqida malumot olinmoqda ...')
		messages = tlg_get_all_messages(client, CHAT_LINK)
		if path.exists(fjson_messages):
			remove(fjson_messages)
		json_write_list(fjson_messages, messages)

		print('Jarayon tugallandi')
		print()

####################################################################################################

### Agar fayl import qilingan modul bo'lmasa, asosiy funktsiyani bajaring ###
if __name__ == "__main__":
	main()

