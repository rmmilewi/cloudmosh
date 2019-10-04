from cloudmosh.components.base import CloudMoshComponent
import numpy as np
from nutsflow.base import Nut
import nutsflow

class DepthCloud:
	def __init__(self,depth):
		"""
		depth: a numpy array of shape (width,height,1) that we want to represent as a point cloud.
		"""
		
		#(width,height,1) --> (width*height,[x,y,z])
		if len(depth.shape) == 3:
			points = np.array([ (row,column,depth[row][column][0]) for row in range(depth.shape[0]) for column in range(depth.shape[1])])
			self._points = points
		else:
			#Already in point form.
			self._points = depth
		self._colors = None
		
	def getPoints(self):
		return self._points
		
	def setPoints(self,points):
		self._points = points
		
	def getColors(self):
		return self._colors
		
	def hasColors(self):
		return self._colors != None
		
	def setColors(self,colors):
		self._colors = colors

	def setDepthByImage(self,depthImage):
		points = np.array([ (row,column,depthImage[row][column][0]) for row in range(depthImage.shape[0]) for column in range(depthImage.shape[1])])
		self._points = points
		
	def setColorsByImage(self,colorImage):
		"""
		colorImage: A numpy array of (width,height,3) that we will reshape as (width*height,[r,g,b]).
		"""
		colors = np.array([ (colorImage[row][column][0],colorImage[row][column][1],colorImage[row][column][2]) for row in range(colorImage.shape[0]) for column in range(colorImage.shape[1])])
		self._colors = colors
		
		
class DepthToClouds(Nut):
	def __init__(self):
		super().__init__()
		
	def __rrshift__(self,iterable):
		"""
		depthData.shape: (N,width,height,1)
		"""
		for depthData in iterable:
			for i in range(depthData.shape[0]):
				depthImage = depthData[i]
				cloud = DepthCloud(depthImage)
				print("DepthToClouds:",cloud)
				yield cloud
				
class PaintClouds(Nut):
	def __init__(self,images):
		"""
		images: An iterable of image objects where each image is of shape (1,width,height,3).
		"""
		super().__init__()
		self._images = images
	
	def __rrshift__(self,iterable):
		"""
		Expected arguments: an iterable of DepthCloud objects
		"""
		
		#(cloud_0,image_0), ... (cloud_n,image_n)
		#iterable = iterable >> nutsflow.Zip(self._images)
		
		clouds = iterable >> nutsflow.Collect()
		images = self._images >> nutsflow.Collect()
		
		iterable = clouds >> nutsflow.Zip(images)
		
		print("PAINT CLOUDS: hello!")
		for cloud,image in iterable:
			image = image[0]
			print("PAINT CLOUDS: cloud.points.shape == ",cloud.getPoints().shape)
			print("PAINT CLOUDS: image.shape == ",image.shape)
			cloud.setColorsByImage(image)
			yield cloud


class ChangeDepthOfClouds(Nut):
	def __init__(self):
		super().__init__()	
	
	def __rrshift__(self,iterable):
		"""
		Expected arguments: [ clouds, depthData ]
		depthData.shape == (N,width,height,1)
		len(clouds) == N
		"""
		clouds = iterable[0]
		depthData = iterable[1]
		
		for i in range(len(clouds)):
			cloud = clouds[i]
			depthImage = depthData[i]
			cloud.setDepthByImage(depthImage)


			
class InterpolateClouds(CloudMoshComponent):
	def __init__(self,stepFunction,tStart,tStop,tStepSize):
		"""
		stepFunction: A real-valued function f(t) -> [0,1].
		tStart: The initial value of t.
		tStop: The final value of t.
		tStepSize: How much we should increment t at each time step.
		"""
		super().__init__()
		self._stepFunction = stepFunction
		self._tStart = tStart
		self._tStop = tStop
		self._tStepSize = tStepSize
		
	def __rrshift__(self,iterable):
		"""
		Expected arguments: [cloud0,cloud1...cloudN]
		"""
		for i in range(len(iterable)-1):
			cloudAtZero = iterable[i]
			cloudAtOne = iterable[i+1]
		
			tCurrent = self._tStart
			coordinates = cloudAtZero.getPoints()[:,[0,1]] #The x and y positions of the points should stay the same.
		
			while tCurrent <= self._tStop:
				ft = self._stepFunction(tCurrent)
			
				currentDepth = (1 - ft) * cloudAtZero.getPoints() + ft * cloudAtOne.getPoints()
				currentColors = (1 - ft) * cloudAtZero.getColors() + ft * cloudAtOne.getColors()
			
				currentPoints = np.hstack((coordinates, currentDepth))
				currentCloud = DepthCloud(currentDepth)
				currentCloud.setColors(currentColors.astype(int))
	
				tCurrent += self._tStepSize
				yield currentCloud
				
			
		
		