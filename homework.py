from __future__ import annotations
import sys

from typing import ClassVar, Dict, Type
from dataclasses import dataclass, asdict


TRAINING_TYPES: Dict[str, str] = {
    'SWM': 'Swimming',
    'RUN': 'Running',
    'WLK': 'SportsWalking',
}


class TrainingTypeError(KeyError):
    """Класс-исключение для класса Training"""


@dataclass
class InfoMessage:
    """Информационное сообщение о тренировке."""

    MESSAGE_TEXT: ClassVar[str] = ('Тип тренировки: {training_type}; '
                                   'Длительность: {duration} ч.; '
                                   'Дистанция: {distance} км; '
                                   'Ср. скорость: {speed} км/ч; '
                                   'Потрачено ккал: {calories}.')
    training_type: str
    duration: str
    distance: str
    speed: str
    calories: str

    def get_message(self) -> str:
        """Получить строку сообщения о тренировке."""
        return self.MESSAGE_TEXT.format(**asdict(self))


class Training:
    """Базовый класс тренировки."""

    LEN_STEP: float = 0.65
    M_IN_KM: int = 1000
    COEFF_MIN_TO_HOURS: int = 60

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 ) -> None:
        self.action = action
        self.duration = duration
        self.weight = weight

    def get_distance(self) -> float:
        """Получить дистанцию в км."""
        return (self.action
                * self.LEN_STEP
                / self.M_IN_KM)

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        return self.get_distance() / self.duration

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        raise NotImplementedError('в классе не переопределен '
                                  'метод get_spent_calories')

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage(self.__class__.__name__,
                           format(self.duration, '.3f'),
                           format(self.get_distance(), '.3f'),
                           format(self.get_mean_speed(), '.3f'),
                           format(self.get_spent_calories(), '.3f'))


class Running(Training):
    """Тренировка: бег."""

    COEFF_CALORIE_1: float = 18
    COEFF_CALORIE_2: float = 20

    def get_spent_calories(self) -> float:

        return ((self.COEFF_CALORIE_1
                * self.get_mean_speed()
                - self.COEFF_CALORIE_2)
                * self.weight
                / self.M_IN_KM
                * self.duration
                * self.COEFF_MIN_TO_HOURS)


class SportsWalking(Training):
    """Тренировка: спортивная ходьба."""

    COEFF_CALORIE_1: float = 0.035
    COEFF_CALORIE_2: float = 0.029

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 height: int,
                 ) -> None:
        super().__init__(action, duration, weight)
        self.height = height

    def get_spent_calories(self) -> float:
        return ((self.COEFF_CALORIE_1
                * self.weight
                + (self.get_mean_speed() ** 2 // self.height)
                * self.COEFF_CALORIE_2
                * self.weight)
                * self.duration
                * self.COEFF_MIN_TO_HOURS)


class Swimming(Training):
    """Тренировка: плавание."""

    LEN_STEP: float = 1.38
    COEFF_CALORIE_1: float = 1.1
    COEFF_CALORIE_2: int = 2

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 length_pool: int,
                 count_pool: int,
                 ) -> None:
        super().__init__(action, duration, weight)
        self.length_pool = length_pool
        self.count_pool = count_pool

    def get_mean_speed(self) -> float:
        """Получить среднюю скорость движения."""
        return (self.length_pool
                * self.count_pool
                / self.M_IN_KM
                / self.duration)

    def get_spent_calories(self) -> float:
        return ((self.get_mean_speed()
                + self.COEFF_CALORIE_1)
                * self.COEFF_CALORIE_2
                * self.weight)


def read_package(workout_type: str, data: list) -> Training:
    """Прочитать данные полученные от датчиков."""
    if workout_type not in TRAINING_TYPES:
        raise TrainingTypeError('Запрашиваемый тип тренировки '
                                'отсутствует в БД фитнесс-трекера')

    class_name: str = TRAINING_TYPES[workout_type]
    request_class: Type[Training] = getattr(sys.modules[__name__], class_name)

    return request_class(*data)


def main(training: Training) -> None:
    """Главная функция."""
    info: InfoMessage = training.show_training_info()
    print(info.get_message())


if __name__ == '__main__':
    packages = [
        ('SWM', [720, 1, 80, 25, 40]),
        ('RUN', [15000, 1, 75]),
        ('WLK', [9000, 1, 75, 180]),
    ]

    for workout_type, data in packages:
        training: Training = read_package(workout_type, data)
        main(training)
