import docker

client = docker.from_env()

print(client.containers.list())

id = client.containers.list()[0].id

container = client.containers.get(id)

for line in container.logs(stream=True):
    print(line.strip())
