"""
Скрипт для скачивания голосовых сообщений из Telegram-канала
"""

from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument, InputPeerChannel
from telethon.errors import ChannelInvalidError, UsernameNotOccupiedError
import os
import asyncio
from datetime import datetime
import sys

# ANSI цветовые коды для красивого вывода
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    MAGENTA = '\033[35m'

# Настройки API (получите на https://my.telegram.org)
API_ID = ''  # Замените на ваш API ID
API_HASH = ''  # Замените на ваш API Hash
PHONE = ''  # Ваш номер телефона
DOWNLOAD_FOLDER = ''  # Папка для сохранения

def clear_screen():
    """Очистка экрана"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Красивый заголовок"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}║{Colors.END}  {Colors.MAGENTA}{Colors.BOLD}🎤 Telegram Voice Messages Downloader 🎤{Colors.END}  {Colors.CYAN}{Colors.BOLD}║{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}\n")

def print_box(text, color=Colors.CYAN):
    """Вывод текста в рамке"""
    lines = text.split('\n')
    max_len = max(len(line) for line in lines)
    print(f"{color}{Colors.BOLD}╔{'═'*(max_len+2)}╗{Colors.END}")
    for line in lines:
        print(f"{color}{Colors.BOLD}║{Colors.END} {line.ljust(max_len)} {color}{Colors.BOLD}║{Colors.END}")
    print(f"{color}{Colors.BOLD}╚{'═'*(max_len+2)}╝{Colors.END}\n")

def print_success(text):
    """Вывод успешного сообщения"""
    print(f"{Colors.GREEN}{Colors.BOLD}✓{Colors.END} {Colors.GREEN}{text}{Colors.END}")

def print_error(text):
    """Вывод сообщения об ошибке"""
    print(f"{Colors.RED}{Colors.BOLD}✗{Colors.END} {Colors.RED}{text}{Colors.END}")

def print_info(text):
    """Вывод информационного сообщения"""
    print(f"{Colors.BLUE}{Colors.BOLD}ℹ{Colors.END} {Colors.BLUE}{text}{Colors.END}")

def print_warning(text):
    """Вывод предупреждения"""
    print(f"{Colors.YELLOW}{Colors.BOLD}⚠{Colors.END} {Colors.YELLOW}{text}{Colors.END}")

def show_menu():
    """Главное меню программы"""
    clear_screen()
    print_header()
    print_box(f"{Colors.YELLOW}ГЛАВНОЕ МЕНЮ{Colors.END}", Colors.YELLOW)
    print(f"{Colors.CYAN}  {Colors.BOLD}1.{Colors.END} Выбрать канал и скачать голосовые сообщения")
    print(f"{Colors.CYAN}  {Colors.BOLD}2.{Colors.END} Показать доступные каналы")
    print(f"{Colors.CYAN}  {Colors.BOLD}0.{Colors.END} Выход из программы")
    print(f"\n{Colors.YELLOW}{Colors.BOLD}{'─'*60}{Colors.END}")
    choice = input(f"{Colors.GREEN}{Colors.BOLD}👉 Ваш выбор: {Colors.END}").strip()
    return choice

async def select_channel(client):
    """Интерактивный выбор канала"""
    print_box(f"{Colors.YELLOW}🔍 ВЫБОР КАНАЛА{Colors.END}", Colors.YELLOW)
    print(f"{Colors.CYAN}  {Colors.BOLD}1.{Colors.END} Выбрать по ID")
    print(f"{Colors.CYAN}  {Colors.BOLD}2.{Colors.END} Выбрать по названию (username)")
    print(f"{Colors.CYAN}  {Colors.BOLD}3.{Colors.END} Выбрать из списка доступных каналов")
    print(f"{Colors.CYAN}  {Colors.BOLD}0.{Colors.END} Вернуться в главное меню\n")
    
    choice = input(f"{Colors.GREEN}{Colors.BOLD}👉 Ваш выбор: {Colors.END}").strip()
    
    channel = None
    
    if choice == '1':
        # Выбор по ID
        print(f"\n{Colors.BLUE}Введите ID канала (например: -1001585046838):{Colors.END}")
        channel_id_input = input(f"{Colors.GREEN}👉 ID: {Colors.END}").strip()
        try:
            channel_id = int(channel_id_input)
            try:
                channel = await client.get_entity(channel_id)
                print_success(f"Канал найден по ID: {Colors.BOLD}{channel.title}{Colors.END}")
            except Exception:
                # Ищем в диалогах
                target_id = abs(channel_id)
                print_info("Поиск канала в ваших диалогах...")
                async for dialog in client.iter_dialogs():
                    entity = dialog.entity
                    if hasattr(entity, 'id'):
                        entity_id = entity.id
                        if abs(entity_id) == target_id:
                            channel = entity
                            print_success(f"Канал найден: {Colors.BOLD}{channel.title}{Colors.END} (ID: {entity_id})")
                            break
                if channel is None:
                    print_error(f"Канал с ID '{channel_id_input}' не найден!")
                    return None
        except ValueError:
            print_error("Неверный формат ID! ID должен быть числом.")
            return None
    
    elif choice == '2':
        # Выбор по username
        print(f"\n{Colors.BLUE}Введите username канала (например: @sirius или sirius):{Colors.END}")
        username_input = input(f"{Colors.GREEN}👉 Username: {Colors.END}").strip()
        if not username_input.startswith('@'):
            username_input = '@' + username_input
        
        try:
            channel = await client.get_entity(username_input)
            print_success(f"Канал найден по username: {Colors.BOLD}{channel.title}{Colors.END}")
        except Exception as e:
            print_error(f"Не удалось найти канал: {e}")
            return None
    
    elif choice == '3':
        # Выбор из списка
        print_box(f"{Colors.YELLOW}📋 ДОСТУПНЫЕ КАНАЛЫ{Colors.END}", Colors.YELLOW)
        channels_list = []
        count = 0
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            if hasattr(entity, 'broadcast') and entity.broadcast:
                count += 1
                entity_id = getattr(entity, 'id', 'N/A')
                title = getattr(entity, 'title', 'N/A')
                username = getattr(entity, 'username', None)
                username_str = f"@{username}" if username else "Нет username"
                channels_list.append(entity)
                print(f"{Colors.CYAN}  {Colors.BOLD}{count}.{Colors.END} {Colors.BOLD}{title}{Colors.END}")
                print(f"      {Colors.BLUE}Username:{Colors.END} {username_str}")
                print(f"      {Colors.BLUE}ID:{Colors.END} {Colors.MAGENTA}{entity_id}{Colors.END}\n")
        
        if not channels_list:
            print_error("Не найдено доступных каналов!")
            return None
        
        try:
            selection = int(input(f"\n{Colors.GREEN}{Colors.BOLD}👉 Выберите номер канала (1-{count}): {Colors.END}").strip())
            if 1 <= selection <= len(channels_list):
                channel = channels_list[selection - 1]
                print_success(f"Выбран канал: {Colors.BOLD}{channel.title}{Colors.END}")
            else:
                print_error("Неверный номер!")
                return None
        except ValueError:
            print_error("Введите число!")
            return None
    
    elif choice == '0':
        return None
    
    else:
        print_error("Неверный выбор!")
        return None
    
    return channel

async def download_voice_messages(client):
    """Основная функция для скачивания голосовых сообщений"""
    
    # Создаем папку для загрузок, если её нет
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.makedirs(DOWNLOAD_FOLDER)
        print_info(f"Создана папка: {Colors.BOLD}{DOWNLOAD_FOLDER}{Colors.END}")
    
    try:
        # Выбираем канал через меню
        channel = await select_channel(client)
        
        if channel is None:
            return
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*60}{Colors.END}")
        print_info(f"Обработка канала: {Colors.BOLD}{channel.title}{Colors.END}")
        print(f"{Colors.CYAN}{Colors.BOLD}{'─'*60}{Colors.END}\n")
        
        voice_count = 0
        total_messages = 0
        
        print_info("Начинаю сканирование сообщений канала...")
        print(f"{Colors.CYAN}{Colors.BOLD}{'─'*60}{Colors.END}\n")
        
        # Проходим по всем сообщениям канала
        async for message in client.iter_messages(channel):
            total_messages += 1
            # Показываем прогресс каждые 50 сообщений
            if total_messages % 50 == 0:
                print_info(f"Проверено сообщений: {Colors.BOLD}{total_messages}{Colors.END} | Найдено голосовых: {Colors.BOLD}{voice_count}{Colors.END}")
            
            # Проверяем, есть ли в сообщении голосовое сообщение
            if message.voice:
                voice_count += 1
                
                # Получаем дату сообщения
                date_str = message.date.strftime('%Y-%m-%d_%H-%M-%S')
                
                # Формируем имя файла
                file_name = f"voice_{date_str}_{message.id}.ogg"
                file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
                
                # Скачиваем файл
                duration = message.voice.attributes[0].duration if message.voice.attributes else 0
                print(f"{Colors.YELLOW}[{voice_count}]{Colors.END} {Colors.GREEN}⬇{Colors.END} {Colors.BOLD}{file_name}{Colors.END} ({duration} сек)")
                await client.download_media(message.voice, file_path)
                print_success(f"Скачано: {file_name}")
                
                # Создаем текстовый файл с метаданными
                info_file = file_path.replace('.ogg', '_info.txt')
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"ID сообщения: {message.id}\n")
                    f.write(f"Дата: {message.date.strftime('%d.%m.%Y %H:%M:%S')}\n")
                    f.write(f"Длительность: {duration} сек\n")
                    if message.message:
                        f.write(f"Текст сообщения: {message.message}\n")
        
        print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.END}")
        print_box(f"{Colors.GREEN}{Colors.BOLD}✓ ГОТОВО!{Colors.END}\n"
                  f"{Colors.CYAN}Проверено сообщений:{Colors.END} {Colors.BOLD}{total_messages}{Colors.END}\n"
                  f"{Colors.GREEN}Скачано голосовых сообщений:{Colors.END} {Colors.BOLD}{voice_count}{Colors.END}\n"
                  f"{Colors.BLUE}Папка сохранения:{Colors.END} {Colors.BOLD}{DOWNLOAD_FOLDER}{Colors.END}", Colors.GREEN)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}{Colors.BOLD}⚠ Прервано пользователем{Colors.END}")
    except Exception as e:
        print_error(f"Произошла ошибка: {e}")

async def show_channels_list(client):
    """Показать список доступных каналов"""
    print_box(f"{Colors.YELLOW}📋 СПИСОК ДОСТУПНЫХ КАНАЛОВ{Colors.END}", Colors.YELLOW)
    channels = []
    count = 0
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if hasattr(entity, 'broadcast') and entity.broadcast:
            count += 1
            entity_id = getattr(entity, 'id', 'N/A')
            title = getattr(entity, 'title', 'N/A')
            username = getattr(entity, 'username', None)
            username_str = f"@{username}" if username else f"{Colors.YELLOW}Нет username{Colors.END}"
            channels.append(entity)
            print(f"{Colors.CYAN}  {Colors.BOLD}{count}.{Colors.END} {Colors.BOLD}{title}{Colors.END}")
            print(f"      {Colors.BLUE}Username:{Colors.END} {username_str}")
            print(f"      {Colors.BLUE}ID:{Colors.END} {Colors.MAGENTA}{entity_id}{Colors.END}\n")
    
    if not channels:
        print_error("Не найдено доступных каналов!")
    else:
        print_success(f"Найдено каналов: {Colors.BOLD}{count}{Colors.END}")
    
    print_warning("\nНажмите Enter, чтобы вернуться в меню...")
    input()

async def main_menu():
    """Главное меню программы"""
    # Проверка настроек
    if API_ID == 'ВАШ_API_ID' or API_HASH == 'ВАШ_API_HASH':
        print_error("Необходимо указать API_ID и API_HASH!")
        print_info("Получите их на https://my.telegram.org")
        return
    
    client = None
    
    while True:
        try:
            choice = show_menu()
            
            if choice == '0':
                clear_screen()
                print_header()
                print_box(f"{Colors.GREEN}{Colors.BOLD}👋 До свидания!{Colors.END}\n{Colors.CYAN}Спасибо за использование программы!{Colors.END}", Colors.GREEN)
                if client:
                    await client.disconnect()
                break
            
            elif choice == '1':
                # Выбрать канал и скачать
                if client is None or not client.is_connected():
                    if client:
                        await client.disconnect()
                    client = TelegramClient('session_name', API_ID, API_HASH)
                    await client.start(phone=PHONE)
                    print_success("Подключение к Telegram успешно!")
                
                await download_voice_messages(client)
                
                print_warning("\nНажмите Enter, чтобы вернуться в меню...")
                input()
            
            elif choice == '2':
                # Показать доступные каналы
                if client is None or not client.is_connected():
                    if client:
                        await client.disconnect()
                    client = TelegramClient('session_name', API_ID, API_HASH)
                    await client.start(phone=PHONE)
                    print_success("Подключение к Telegram успешно!")
                
                await show_channels_list(client)
            
            else:
                print_error("Неверный выбор! Попробуйте снова.")
                input()
        
        except KeyboardInterrupt:
            clear_screen()
            print_header()
            print_box(f"{Colors.YELLOW}{Colors.BOLD}⚠ Прервано пользователем{Colors.END}", Colors.YELLOW)
            if client:
                await client.disconnect()
            break
        except Exception as e:
            print_error(f"Произошла ошибка: {e}")
            print_warning("\nНажмите Enter, чтобы продолжить...")
            input()

def main():
    """Запуск программы"""
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        clear_screen()
        print_header()
        print_box(f"{Colors.YELLOW}{Colors.BOLD}⚠ Программа завершена{Colors.END}", Colors.YELLOW)

if __name__ == '__main__':
    main()

