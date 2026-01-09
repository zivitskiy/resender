import asyncio
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetDialogFiltersRequest

api_id = 14112604
api_hash = '57b9029961529f2aa11a0b87acd64606'
session = 'bot'

SOURCE_FOLDER = "Каналы"
TARGET_CHANNEL = -1001234567890  # замени на свой таргет канал id
MY_CHANNEL_TAG = "@PayscrowTeamleadBoost"  # твой тег канала

client = TelegramClient(session, api_id, api_hash)

async def get_folder_chats():
    """получаем все чаты из папки"""
    filters = await client(GetDialogFiltersRequest())
    
    for f in filters.filters:
        if hasattr(f, "title"):
            title = f.title.text if hasattr(f.title, "text") else str(f.title)
            if title.lower() == SOURCE_FOLDER.lower():
                peers = getattr(f, "include_peers", [])
                return [p for p in peers]
    
    return []

@client.on(events.NewMessage())
async def handler(event):
    """ловим все сообщения и чекаем откуда они"""
    try:
        # получаем список чатов из папки
        folder_chats = await get_folder_chats()
        
        # чекаем откуда пришло сообщение
        chat_id = event.chat_id
        is_from_folder = any(
            (hasattr(p, 'channel_id') and p.channel_id == chat_id) or
            (hasattr(p, 'chat_id') and p.chat_id == chat_id) or
            (hasattr(p, 'user_id') and p.user_id == chat_id)
            for p in folder_chats
        )
        
        if not is_from_folder:
            return
        
        # получаем инфу о канале-источнике
        chat = await event.get_chat()
        chat_title = chat.title if hasattr(chat, 'title') else "Unknown"
        chat_username = f"@{chat.username}" if hasattr(chat, 'username') and chat.username else ""
        
        # формируем хештег
        hashtag = f"#from_{str(chat_id).replace('-100', '')}"
        
        # собираем текст сообщения
        original_text = event.message.text or ""
        
        formatted_text = f"{hashtag}\n{chat_title} {chat_username}\n\n{original_text}\n\n{MY_CHANNEL_TAG}"
        
        # пересылаем в таргет канал с медиа если есть
        if event.message.media:
            await client.send_message(
                TARGET_CHANNEL,
                formatted_text,
                file=event.message.media
            )
        else:
            await client.send_message(
                TARGET_CHANNEL,
                formatted_text
            )
        
        print(f"✅ переслал с {chat_id}")
        
    except Exception as e:
        print(f"❌ ошибка: {e}")

async def main():
    await client.start(phone="+380958249338")
    
    folder_chats = await get_folder_chats()
    if not folder_chats:
        print("❌ папка не найдена")
        return
    
    print(f"✅ найдено {len(folder_chats)} чатов в папке")
    print("🔥 бот запущен, жду сообщения...")
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
