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

DEFAULT_MIN = 0
DEFAULT_MAX = 99

def check_length(content="", input_name=None):
    return len(content.strip()) >= get_min(input_name) and len(content) <= get_max(input_name)

def get_min(input_name=None):
    return min_lengths.get(input_name, DEFAULT_MIN)

def get_max(input_name=None):
    return max_lengths.get(input_name, DEFAULT_MAX)
