#! python3.8

from threading import Thread, Semaphore
from queue import Queue
import cv2 as cv
from cv_functions import *

class BlockingQueue():
	def __init__(self, max_size=10, name=''):
		self._queue_sema = Semaphore(max_size)
		self._dequeue_sema = Semaphore(0)
		self.name = name
		self._items = []

	def get(self):
		# print(f'\t{self.name} dequeu acquire')
		self._dequeue_sema.acquire()
		if len(self._items):
			val = self._items.pop(0)
			# print(f'\t{self.name} queue release')
			self._queue_sema.release()
			return val
		else:
			return None

	def put(self, value):
		# print(f'\t{self.name} queue acquire')
		self._queue_sema.acquire()
		self._items.append(value)
		# print(f'\t{self.name} dequeue release')
		self._dequeue_sema.release()

	def getSize(self): return len(self._items)

default_file = 'clip.mp4'
default_delay = 42
QUEUE_SIZE = 10

extractQueue, displayQueue = BlockingQueue(QUEUE_SIZE, "extract"), BlockingQueue(QUEUE_SIZE, "display")


def extractFrames(filePath):
	print('\t\t--Started Extract Thread--')
	vid = openVideoFile(filePath)
	success, frame = nextFrame(vid)
	count = 1
	while success:
		try:
			extractQueue.put(frame)
			print(f'extracting frame {count}')
			success, frame = nextFrame(vid)
		except Exception as err: print(str(err) + '\tfail 1')
		finally: count += 1


def convertFramesToGrayscale():
	print('\t\t--Started Convert Thread--')
	count = 1
	while True:
		try:
			frame = extractQueue.get()
			print(f'converting frame {count} to grayscale')
			frame = frame2grayscale(frame)
			displayQueue.put(frame)
			# displayQueue.put(frame2grayscale(inputQueue.get()))
		except Exception as err: print(str(err) + '\tfail 2')
		finally: count += 1


def displayFrames():
	print('\t\t--Started Display Thread--')
	count = 1
	while True:
		try:
			displayFrame(displayQueue.get(), default_delay)
			print(f'displaying frame {count}')
		except Exception as err: print(str(err) + '\tfail 3')
		finally: count += 1
	cv.destroyAllWindows()


if __name__ == '__main__':
	Thread(target=extractFrames, args=[default_file], name='Extract Frames Thread').start()
	Thread(target=convertFramesToGrayscale, name='Convert To Grayscale Thread', daemon=True).start()
	displayFrames()
