from worker.tasks import echo_task

result = echo_task.delay("Hello from test!")
print("Task sent, waiting for result...")
print("Result:", result.get(timeout=10))
