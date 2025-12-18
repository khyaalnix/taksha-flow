import threading
class SingleTonClass(object):
    """Created a singleton class"""
    _lock = threading.Lock()
    _instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

