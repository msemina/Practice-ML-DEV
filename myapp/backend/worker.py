import redis
from rq import Queue
from model_processing import process_model 

# Set up a Redis connection
redis_conn = redis.Redis()
queue = Queue(connection=redis_conn)

# Function to add tasks to the queue
def add_task_to_queue(file_path, model_id):
    job = queue.enqueue(process_model, file_path, model_id)
    return job.get_id()
 