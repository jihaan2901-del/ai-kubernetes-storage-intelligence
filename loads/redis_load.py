import redis
import random
import string
import time

r = redis.Redis(
    host="localhost",
    port=30007,
    decode_responses=True
)

while True:

    key = ''.join(random.choices(string.ascii_letters, k=10))
    value = ''.join(random.choices(string.ascii_letters, k=20000))

    r.set(key, value)

    print("Inserted redis key:", key)

    time.sleep(0.05)