REDIS_URL = 'redis://:citcw200@redis_dir:6387/0'
#REDIS_URL = 'redis://:citcw200@redis:6379/0'
#REDIS_URL = 'redis://redis:6379/0'
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
