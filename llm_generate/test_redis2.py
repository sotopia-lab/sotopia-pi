from redis_om import JsonModel, get_redis_connection

class Person(JsonModel):
    name: str
    age: int

# Create an instance of your model
person = Person(name="John", age=30)

# Save to Redis
person.save()

# Retrieve from Redis
retrieved_person = Person.load(person.id)

# Print the retrieved data
print(retrieved_person.name)  # Output: John
print(retrieved_person.age)   # Output: 30