"""
Проверка совместимости зависимостей
"""
import sys
import importlib

def check_dependency(module_name, min_version=None):
    """Проверка наличия и версии зависимости"""
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, '__version__', 'unknown')
        
        if min_version:
            # Простая проверка версии (для демонстрации)
            print(f"✅ {module_name}: {version} (требуется: {min_version}+)")
        else:
            print(f"✅ {module_name}: {version}")
            
        return True
    except ImportError:
        print(f"❌ {module_name}: не установлен")
        return False

def main():
    print("🔍 Проверка зависимостей Auction Bot")
    print("=" * 40)
    
    # Основные зависимости
    dependencies = {
        'playwright': None,
        'telegram': None,  # python-telegram-bot
        'yaml': None,      # PyYAML
        'aiohttp': None,
        'pytest': None,
        'PyQt6': None,
        'qasync': None,
    }
    
    all_ok = True
    
    for dep, min_version in dependencies.items():
        if not check_dependency(dep, min_version):
            all_ok = False
    
    print("=" * 40)
    if all_ok:
        print("✅ Все зависимости установлены корректно")
    else:
        print("❌ Некоторые зависимости отсутствуют")
        print("\nУстановите недостающие зависимости:")
        print("pip install -r requirements.txt")
    
    # Проверка специфических атрибутов PyQt6
    try:
        from PyQt6 import QtCore
        print(f"✅ PyQt6 Qt версия: {QtCore.QT_VERSION_STR}")
    except ImportError as e:
        print(f"❌ Ошибка PyQt6: {e}")

if __name__ == "__main__":
    main()
