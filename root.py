import os


def get_root():
    return os.path.dirname(os.path.abspath(__file__))


def get_log():
    return os.path.join(get_root(), 'log')
