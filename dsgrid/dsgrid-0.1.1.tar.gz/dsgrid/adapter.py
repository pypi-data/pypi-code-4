import docker


class DockerAdapter:
    def __init__(self):
        self.client = docker.Client(base_url='unix://var/run/docker.sock', version="1.4")

    def find_image(self, repo_name):
        images = self.client.images()
        for image in images:
            name = image.get('Repository', 'unknown')
            if name == repo_name:
                return image

        return None

    def find_container(self, image_name):
        containers = self.client.containers()
        for container in containers:
            name = container.get('Image', 'unknown')
            if name == image_name:
                return container

    def find_all_containers(self, image_name):
        matches = []
        containers = self.client.containers()
        for container in containers:
            name = container.get('Image', 'unknown')
            if name == image_name:
                matches.append(container)
        return matches

    def inspect(self, container_id):
        return self.client.inspect_container(container_id)

    def restart(self, container_id):
        self.client.restart(container_id)
