from inspect import stack
from typing import ClassVar, Dict, Union, Type
from dataclasses import dataclass, asdict


NOT_IMPLEM_ERROR_MESSAGE: str = ('в классе {} необходимо '
                                 'переопределить метод {}')


@dataclass
class InfoMessage:
    """Информационное сообщение о тренировке."""

    training_type: str
    duration: float
    distance: float
    speed: float
    calories: float

    MESSAGE_TEXT: ClassVar[str] = ('Тип тренировки: {training_type}; '
                                   'Длительность: {duration:.3f} ч.; '
                                   'Дистанция: {distance:.3f} км; '
                                   'Ср. скорость: {speed:.3f} км/ч; '
                                   'Потрачено ккал: {calories:.3f}.')

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
        raise NotImplementedError(
            NOT_IMPLEM_ERROR_MESSAGE.format(
                self.__class__.__name__, stack()[0][3]
            )
        )

    def show_training_info(self) -> InfoMessage:
        """Вернуть информационное сообщение о выполненной тренировке."""
        return InfoMessage(self.__class__.__name__,
                           self.duration,
                           self.get_distance(),
                           self.get_mean_speed(),
                           self.get_spent_calories(),)


class Running(Training):
    """Тренировка: бег."""

    SPEED_MULTIPLIER: int = 18
    SPEED_SUBTRACTOR: int = 20

    def get_spent_calories(self) -> float:
        """Получить количество затраченных калорий."""
        return ((self.SPEED_MULTIPLIER
                * self.get_mean_speed()
                - self.SPEED_SUBTRACTOR)
                * self.weight
                / self.M_IN_KM
                * self.duration
                * self.COEFF_MIN_TO_HOURS)


class SportsWalking(Training):
    """Тренировка: спортивная ходьба."""

    WEIGHT_COEFFICIENT: float = 0.035
    SPEED_WEIGHT_COEFFICIENT: float = 0.029

    def __init__(self,
                 action: int,
                 duration: float,
                 weight: float,
                 height: int,
                 ) -> None:
        super().__init__(action, duration, weight)
        self.height = height

    def get_spent_calories(self) -> float:
        return ((self.WEIGHT_COEFFICIENT
                * self.weight
                + (self.get_mean_speed() ** 2 // self.height)
                * self.SPEED_WEIGHT_COEFFICIENT
                * self.weight)
                * self.duration
                * self.COEFF_MIN_TO_HOURS)


class Swimming(Training):
    """Тренировка: плавание."""

    LEN_STEP: float = 1.38
    SPEED_ADD_COEFFICIENT: float = 1.1
    SPEED_MULTIPLIER: int = 2

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
                + self.SPEED_ADD_COEFFICIENT)
                * self.SPEED_MULTIPLIER
                * self.weight)


TrainingTypesDict = Dict[str, Union[Type[Swimming],
                                    Type[Running],
                                    Type[SportsWalking]]]

TRAINING_TYPES: TrainingTypesDict = {
    'SWM': Swimming,
    'RUN': Running,
    'WLK': SportsWalking,
}


def read_package(workout_type: str, data: list) -> Training:
    """Прочитать данные полученные от датчиков."""
    if workout_type not in TRAINING_TYPES:
        raise ValueError('Запрашиваемый тип тренировки '
                         'отсутствует в БД фитнесс-трекера')
    return TRAINING_TYPES[workout_type](*data)


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
