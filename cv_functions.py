
import cv2 as cv

def openVideoFile(filePath): return cv.VideoCapture(filePath)

def nextFrame(video): return video.read()

def frame2grayscale(frame): return cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

def displayFrame(frame=None, frameDelay=42):
	cv.imshow('Video', frame)  # Display the frame in a window called "Video"
	cv.waitKey(frameDelay) # Delay execution

__all__ = ['openVideoFile', 'nextFrame', 'frame2grayscale', 'displayFrame']
