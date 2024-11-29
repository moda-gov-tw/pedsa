REDIS_URL = 'redis://:citcw200@redis_syn1:6380/0'
#REDIS_URL = 'redis://:citcw200@redis:6379/0'
#REDIS_URL = 'redis://redis:6379/0'
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
