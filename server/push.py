import json
import redis

# Connect to Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Load JSON data
with open('hust_courses.json', 'r', encoding='utf-8') as f:
    courses = json.load(f)

# Push each course to Redis
for course in courses:
    course_code = course['Mã học phần']
    course_name = course['Tên học phần']

    main_key = f"course:{course_code}"
    r.hset(main_key, mapping=course)

    # Add alias key for name-based lookup
    alias_key = f"course_name:{course_name.lower()}"
    r.set(alias_key, main_key)


print("Courses have been pushed to Redis.")
