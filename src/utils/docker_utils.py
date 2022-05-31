import docker

class SplashContainer():

    class ContainerNotRunningException(Exception):
        pass
    SPLASH_DOCKER_NAME = 'splash'
    container = None

    def  __init__(self):
        pass

    def start(self):
        client = docker.from_env()
        client.containers.run('scrapinghub/splash', ports = {'8050': 8050}, name = self.SPLASH_DOCKER_NAME, detach = True)
        self.container = client.containers.get(self.SPLASH_DOCKER_NAME)

    def is_running(self):
        client = docker.from_env()
        try:
            self.container = client.containers.get(self.SPLASH_DOCKER_NAME) 
            return True
        except Exception as e:
            return False

    def get_stream_output(self):
        if self.container != None:
            return self.container.logs(stream=True)
        raise SplashContainer.ContainerNotRunnerException("Container is stopped or not running")

    def stop(self):
        self.container.stop()
    
if __name__ == '__main__':
    splash = SplashContainer()
    if splash.is_running() == False:
        print("Splash is not running. Starting docker ... ")
        splash.start()

    print("Logging starts")
    try:
        logs = splash.get_stream_output()
        for log in logs:
            print(log.strip())
    except SplashContainer.ContainerNotRunningException as e:
        print(str(e))
