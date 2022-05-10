import subprocess
from jmespath import search
import pygame
from pygame.locals import *
import pygame_gui
import os
from multiprocessing import Pool
import docker

SPLASH_DOCKER_NAME = 'splash'

def start_cnn_search(data):
    print('Started new process pid=', os.getpid())
    proc = subprocess.Popen(f"scrapy crawl cnn_search_spider -a search_term={data['search_term']} -a sections={data['sections']} -a retry={data['retry']} -s LOG_ENABLED=False".split(" "),\
            cwd='../news_spider/news_spider', stdout=subprocess.PIPE, encoding='utf-8')
    proc.wait()
    proc.poll()
    print('completed with return code ', proc.returncode)
    return proc.returncode

def get_cnn_spider_data(search_term, sections, retry = False):
    return {'search_term': search_term, 'sections': sections, 'retry': retry}

def start_splash():
    client = docker.from_env()
    if client.containers.get(SPLASH_DOCKER_NAME) == None:
        client.containers.run('scrapinghub/splash', ports = {'8050': 8050}, name = 'splash')
    container = client.containers.get(SPLASH_DOCKER_NAME)

    for line in container.logs(stream=True):
        print(line.strip())

class Main():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('quick start')
        self.window_surface = pygame.display.set_mode((800,600))
        self.background = pygame.Surface((400,300))
        self.background.fill(pygame.Color('#000000'))
        self.manager = pygame_gui.UIManager((800,600))

    def run(self):
        # button_rect = pygame.Rect(55,25,100,50)
        # hello_button = pygame_gui.elements.UIButton(relative_rect=button_rect, text="Say hello", manager = self.manager)
        textbox = pygame_gui.elements.UITextBox(relative_rect=pygame.Rect(0,0,300,100), manager = self.manager, html_text='Hello')
        button1 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(0,200,150,30), text='Crawl', manager = self.manager)
        start_splash_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(0,300,200,30), text='Start splash docker', manager = self.manager)
        # button2 = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(0,300,150,30), text='CNN Search Tesla', manager = self.manager)

        clock = pygame.time.Clock()

        is_running = True

        while is_running:

            time_delta = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                self.manager.process_events(event)

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == start_splash_button:
                        start_splash()

                    if event.ui_element == button1:
                        print("Started crawler")
                        pool_data = (
                                get_cnn_spider_data('apple', 'business'),
                                # get_cnn_spider_data('tesla', 'business'),
                                # get_cnn_spider_data('amazon', 'business'),
                                # get_cnn_spider_data('microsoft', 'business'),
                                # get_cnn_spider_data('nvidia', 'business'),
                                # get_cnn_spider_data('amd', 'business'),
                                # get_cnn_spider_data('google', 'business'),
                                # get_cnn_spider_data('facebook', 'business'),
                            ) 
                        with Pool() as pool:
                            res = pool.map(start_cnn_search, pool_data)
                        
                        print(res)

                if event.type == pygame.QUIT:
                    is_running = False
            self.manager.update(time_delta)

            self.window_surface.blit(self.background, (0,0))

            self.manager.draw_ui(self.window_surface)
            
            pygame.display.update()

        pygame.quit()

def start_docker():
    print("Start docker process with pid=", os.getpid())

if __name__ == '__main__':
    print("pygame pid=", os.getpid())
    main = Main()
    main.run()