import threading
import logging

# All-in-caps-for-emphasis
# THIS THREAD DOESN'T DOWNLOADS ANYTHING
# ONLY ADDS VIDEOS TO THE QUEUE AND THAT'S ALL.
class HelperThread(threading.Thread):
    def __init__(self, marshaller):
        super().__init__()
        self.marshaller = marshaller
        self.event = threading.Event()
    
    def add_video_to_download(self, url, outfolder, quality, VBRquality=2):
        self.marshaller.add_video_to_download(url, outfolder, quality, VBRquality)
        self.event.set()
    
    def run(self):
        self.marshaller.event_starter(self.event)
    
    def quit(self):
        self.marshaller.event_starter_quit = True
        self.event.set()
		
class InserterThread(threading.Thread):
    def __init__(self, helperThread):
        super().__init__()
        self.helperThread = helperThread
        self.queue = []
        self._quit = False
        self.event = threading.Event()
        # For status bar
        # When added_element is None, there is no element being processed.
        # This, plus len(queue) == 0, indicates the queue is empty.
        self.message_callback = lambda self, added_element: None
    
    def add_video_to_download(self, *args, **kwargs):
        self.queue.append([args, kwargs])
        self.event.set()
    
    def run(self):
        while not self._quit:
            self.event.wait()
            logging.info("InserterThread: Event recieved.")
            self.message_callback(self, None)
            for element in self.queue:
                self.helperThread.add_video_to_download(*element[0],
                                                        **element[1])
                self.message_callback(self, element)
                logging.info("InserterThread: Added video.")
            self.queue.clear()
            self.message_callback(self, None)
            self.event.clear()
    
    def quit(self):
        self._quit = True
        self.event.set()

