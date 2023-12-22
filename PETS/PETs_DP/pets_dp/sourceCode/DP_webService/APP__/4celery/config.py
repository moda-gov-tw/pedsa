#from kombu import Queue

#REDIS_URL = 'redis://redis:6379/0'

REDIS_URL = 'redis://:citcw200@redis:6379/0'

CELERY_BROKER_URL = REDIS_URL

CELERY_RESULT_BACKEND = REDIS_URL


CELERY_ROUTES={('task_router.TaskRouter',)}
#CELERY_QUEUES=(
        #Queue('default', routing_key='tasks.#'),
        #Queue('hipri', routing_key='hipri:killProcess'),
    #)
CELERY_ROUTES={'hipri:killProcess': {'queue': 'hipri'}}
CELERY_RESULT_SERIALIZER = 'json' 
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']
CELERY_TASK_SERIALIZER = 'json'

#task_serializer='json'
#result_serializer='json'
#accept_content='json'
