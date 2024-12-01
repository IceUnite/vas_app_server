import enum
from enum import Enum


# Перечисление для статуса документа
class DocumentStatus(enum.Enum):
    READY = "готов"
    CANCELED = "отменён"
    COMPLETED = "выполнен"
    IN_PROGRESS = "в работе"
