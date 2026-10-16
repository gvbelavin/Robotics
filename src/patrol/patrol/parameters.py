"""Проверка настроек движения до изменения таймера и команды."""

import math

LINEAR_SPEED_MIN = 0.0
LINEAR_SPEED_MAX = 1.0
TURN_RATE_MIN = -1.0
TURN_RATE_MAX = 1.0
PUBLISH_HZ_MIN = 1.0
PUBLISH_HZ_MAX = 30.0

_FIELDS = (
    ('linear_speed', LINEAR_SPEED_MIN, LINEAR_SPEED_MAX),
    ('turn_rate', TURN_RATE_MIN, TURN_RATE_MAX),
    ('publish_hz', PUBLISH_HZ_MIN, PUBLISH_HZ_MAX),
)


def values_with_update(linear_speed, turn_rate, publish_hz, updates):
    """Собрать тройку настроек: неизвестные поля остаются прежними."""
    values = {
        'linear_speed': linear_speed,
        'turn_rate': turn_rate,
        'publish_hz': publish_hz,
    }
    for name, value in updates.items():
        if name in values:
            values[name] = value
    return values['linear_speed'], values['turn_rate'], values['publish_hz']


def validate_values(linear_speed, turn_rate, publish_hz):
    """
    Вернуть (True, '') либо (False, причина), не меняя состояние ноды.

    Допустимы только конечные числа: скорость 0–1 м/с, поворот −1–1 рад/с,
    частота 1–30 Гц.
    """
    candidate = {
        'linear_speed': linear_speed,
        'turn_rate': turn_rate,
        'publish_hz': publish_hz,
    }
    for name, low, high in _FIELDS:
        value = candidate[name]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False, f'{name} должен быть числом'
        number = float(value)
        if not math.isfinite(number):
            return False, f'{name} должен быть конечным числом'
        if number < low or number > high:
            return False, f'{name} вне диапазона [{low:.1f}, {high:.1f}]'
    return True, ''
