#! python3.8

from threading import Thread, Semaphore
import sys, cv2 as cv


class BlockingQueue(): # Blocking Queue implemented with list; less ops/sec
	def __init__(self, max_size=10):
		self._queue_sema = Semaphore(max_size) # Tracks num of available incoming items
		self._dequeue_sema = Semaphore(0) # Tracks num of available outgoing items
		self._items = []

	def get(self):
		self._dequeue_sema.acquire() # Remove spot for outgoing items
		if len(self._items):
			val = self._items.pop(0)
			self._queue_sema.release() # Add spot for incoming items
			return val
		else: return None

	def put(self, value):
		self._queue_sema.acquire() # Remove spot from incoming items
		self._items.append(value)
		self._dequeue_sema.release() # Add spot for outgoing items

	def getSize(self): return len(self._items)


default_file = 'clip.mp4' # Path to video file
frame_delay = 1 # Delay after rendering frames
QUEUE_SIZE = 10 # Number of elements a queue can hold at one time

extractQueue, displayQueue = BlockingQueue(QUEUE_SIZE), BlockingQueue(QUEUE_SIZE)
complete = False # Global flag for determining if no frames left in video


def extractFrames(filePath):
	print('--Starting Extract Thread--')
	video = cv.VideoCapture(filePath) # Open video
	success, frame = video.read() # Get first video frame
	count = 1
	while success:
		try:
			extractQueue.put(frame) # Add frame to extract queue to be converted
			print(f'\textracting frame {count}\n')
			success, frame = video.read() # Get next video frame
		except Exception as err: print(err)
		finally: count += 1
	global complete
	complete = True


def convertFramesToGrayscale():
	print('--Starting Convert Thread--')
	count = 1
	while True:
		try:
			frame = cv.cvtColor(extractQueue.get(), cv.COLOR_BGR2GRAY) # Convert frame to grayscale
			print(f'\t\tconverting frame {count} to grayscale\n')
			displayQueue.put(frame) # Add frame to display queue
		except Exception as err: print(err)
		finally: count += 1


def displayFrames():
	print('--Starting Display Thread--')
	count = 1
	while displayQueue.getSize() > 0 or not complete:
		try:
			frame = displayQueue.get()
			cv.imshow('Video', frame)  # Display the frame in a window called "Video"
			cv.waitKey(frame_delay)  # Delay execution
			print(f'\t\t\tdisplaying frame {count}\n')
		except Exception as err: print(err)
		finally: count += 1
	cv.destroyAllWindows() # Close video window


if __name__ == '__main__':
	try:
		Thread(target=extractFrames, args=[default_file], name='Extract Frames Thread', daemon=True).start() # Helper thread
		Thread(target=convertFramesToGrayscale, name='Convert To Grayscale Thread', daemon=True).start() # Helper thread
		displayFrames() # Main thread
	except KeyboardInterrupt: sys.exit(1)
