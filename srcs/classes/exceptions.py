from logger import logger


class ConnectionError(RuntimeError):
    pass


class BattleLostError(RuntimeError):
    pass


class NotEnoughStamina(RuntimeError):
    pass


class DomainNotSpecifiedError(KeyError):
    pass