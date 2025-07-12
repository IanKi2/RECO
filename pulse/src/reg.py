import requests
import time
from datetime import datetime

print("=== Автоматическая регистрация на раунд DatsPulse ===")
print("Скрипт будет пытаться зарегистрироваться каждую минуту\n")

TOKEN = "63bf8b86-1505-4f25-b160-27342aa20c58"  # Ваш токен
URL = "https://games-test.datsteam.dev/api/register"

def try_register():
    """Попытка регистрации"""
    try:
        response = requests.post(
            URL,
            headers={
                "accept": "application/json",
                "X-Auth-Token": TOKEN
            },
            data='',
            timeout=5  # Таймаут 5 секунд
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Успешная регистрация!")
            print(f"Раунд: {data.get('name', 'N/A')}")
            print(f"Сервер: {data.get('realm', 'N/A')}")
            print(f"Лобби закончится через: {data.get('lobbyEndsIn', 'N/A')} сек")
            return True
            
        else:
            error = response.json() if response.content else {}
            print(f"❌ Ошибка {response.status_code}: {error.get('message', response.text)}")
            return False
            
    except Exception as e:
        print(f"🚫 Ошибка соединения: {str(e)}")
        return False

# Бесконечный цикл с попытками регистрации
attempt = 1
while True:
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"\n[{current_time}] Попытка регистрации #{attempt}...")
    
    if try_register():
        print("\n🎉 Регистрация успешна! Скрипт завершает работу.")
    
    # Пауза 60 секунд до следующей попытки
    print(f"⏳ Следующая попытка через 60 секунд...")
    time.sleep(60)
    attempt += 1