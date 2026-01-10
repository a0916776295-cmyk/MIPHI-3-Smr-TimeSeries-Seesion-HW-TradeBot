#!/usr/bin/env python
# -*- coding: utf-8 -*-

def test_button_matching():
    """Тестирует точное совпадение текста кнопок"""
    print("🔍 ТЕСТ ТОЧНОГО СОВПАДЕНИЯ КНОПОК")
    print("=" * 50)
    
    # Кнопки, которые создаются в боте
    bot_button_texts = [
        "✅ Да, создать тест",
        "❌ Нет, спасибо"
    ]
    
    # Возможные варианты того, что может приходить от пользователя
    user_inputs = [
        "✅ Да, создать тест",  # Точное совпадение
        "✅Да, создать тест",   # Без пробела после эмодзи
        "✅ Да,создать тест",   # Без пробела после запятой
        "✅ Да, создать тест ",  # С пробелом в конце
        " ✅ Да, создать тест", # С пробелом в начале
        "Да, создать тест",     # Без эмодзи
    ]
    
    print("📱 Кнопки в боте:")
    for i, button in enumerate(bot_button_texts, 1):
        print(f"   {i}. '{button}' (длина: {len(button)})")
    
    print("\n📨 Тестирование входящих сообщений:")
    
    for user_input in user_inputs:
        matches = []
        for bot_button in bot_button_texts:
            if user_input == bot_button:
                matches.append("✅ ТОЧНОЕ СОВПАДЕНИЕ")
            elif user_input.strip() == bot_button:
                matches.append("🔧 СОВПАДЕНИЕ ПОСЛЕ STRIP")
            else:
                matches.append("❌ НЕТ СОВПАДЕНИЯ")
        
        print(f"   '{user_input}' (длина: {len(user_input)})")
        for j, match in enumerate(matches):
            print(f"      с кнопкой {j+1}: {match}")
    
    print("\n💡 РЕКОМЕНДАЦИИ:")
    print("1. Использовать text.strip() для удаления пробелов")
    print("2. Проверить кодировку эмодзи")
    print("3. Добавить альтернативные варианты проверки")
    
    # Тест с реальным кодом
    print("\n🧪 ТЕСТ С РЕАЛЬНЫМ КОДОМ:")
    
    test_text = "✅ Да, создать тест"
    
    if test_text == "✅ Да, создать тест":
        print("✅ Прямое сравнение работает")
    else:
        print("❌ Прямое сравнение НЕ работает")
        
    if test_text.strip() == "✅ Да, создать тест":
        print("✅ Сравнение с strip() работает") 
    else:
        print("❌ Сравнение с strip() НЕ работает")

if __name__ == "__main__":
    test_button_matching()