import sys
import pygame
from pybm.Job import Status
from pybm.JenkinsMonitor import JenkinsMonitor
from pybm.ProgressBar import ProgressBar

OK = (0, 150, 0)
WARNING = (255, 204, 51)
ERROR = (150, 0, 0)
UNKNOWN = (172, 172, 172)
BUILDING = (0, 172, 172)

import argparse

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('url', metavar='Url', type=str,
                   help='jenkins url')
parser.add_argument('view', metavar='View', type=str,
                   help='view to visualise')

args = parser.parse_args()

print args.view, args.url

def get_color(state):
    if state == Status.OK:
        return OK
    elif state == Status.WARNING:
        return WARNING
    elif state == Status.ERROR:
        return ERROR
    elif state == Status.WARNING:
        return WARNING
    elif state == Status.BUILDING:
        return BUILDING
    else:
        return UNKNOWN

pygame.init()
clock = pygame.time.Clock()
size = width, height = 0, 0
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
font = pygame.font.SysFont('sans-serif', 160, True)
pygame.mouse.set_visible(0)

margin = 10

jobMonitor = JenkinsMonitor(args.url, args.view)
jobMonitor.start()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()  # Exit the main loop
            sys.exit()
        elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()  # Exit the main loop
                    sys.exit()

    screen.fill((0, 0, 0))

    jobs = jobMonitor.get_job_list()
    if len(jobs) > 0:
        bar_height = (screen.get_size()[1]-((len(jobs)+1)*margin))/len(jobs)
        bars = []
        j = 0

        for job in jobs:
            bar_x = margin
            bar_y = (margin*(j + 1)) + (bar_height * j)
            bar_width = screen.get_size()[0]-(margin*2)
            bars.append(ProgressBar(screen, bar_x, bar_y, bar_width, bar_height, job.get_name()))
            bars[j].set_color(get_color(job.get_status()))
            bars[j].update(job.get_percentage())
            j += 1

    pygame.display.flip()
    clock.tick(1)
