# Asteroids Game

Простая реализация игры Asteroids на Python.

## Установка

pip install -r requirements.txt

## Запуск

python main.py

## Управление

В меню:
- UP/DOWN - выбор
- ENTER - выбрать
- ESC - выход

В игре:
- LEFT/RIGHT - вращение
- UP - движение
- SPACE - стрельба
- 1 - Щит (Shield)
- 2 - Ускорение (Speed Boost)
- 3 - Замедление (Slow Motion)

## Структура

main.py - входная точка
game.py - основная логика игры и главный цикл
player.py - класс корабля игрока
bullet.py - класс пули
asteroid.py - класс астероида
vector2.py - класс вектора
sounds.py - система звуков
config_manager.py - работа с конфигом
config.json - параметры игры
highscores.json - таблица рекордов

## Модификаторы

Shield - поглощает 1 удар, кулдаун 8 сек
Speed Boost - 2x скорость, кулдаун 6 сек
Slow Motion - 0.5x скорость врагов, кулдаун 6 сек

## Требования

Python 3.7+
pygame>=2.0.0
numpy>=1.19.0

## Музыка

Для проигрывания музыки при запуске игры:

1. Добавьте файл iowa.mp3 в корень папки проекта
2. Или запустите python add_music.py для генерирования музыки

Музыка будет проигрываться по кругу во время игры и останавливаться при завершении.

## Тестирование

python -m pytest tests/ -v
python -m pytest tests/ --cov=. --cov-report=term-missing
