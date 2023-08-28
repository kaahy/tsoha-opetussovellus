min_lengths = {"name": 1,
           "password": 5,
           "course name": 1,
           "page title": 1,
           "page content": 0,
           "question": 1,
           "choice": 1
    }

max_lengths = {"name": 50,
           "password": 100,
           "course name": 100,
           "page title": 100,
           "page content": 50000,
           "question": 500,
           "choice": 200
    }

default_min = 0
default_max = 99

def check_length(content="", type=None):
    min = default_min
    max = default_max
    if type in min_lengths:
        min = min_lengths[type]
    if type in max_lengths:
        max = max_lengths[type]
    if len(content.strip()) < min or len(content) > max:
        return False
    return True

def get_min(type=None):
    if type in min_lengths:
        return min_lengths[type]
    return default_min

def get_max(type=None):
    if type in max_lengths:
        return max_lengths[type]
    return default_max
