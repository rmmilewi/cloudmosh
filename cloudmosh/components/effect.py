from nutsflow.base import Nut,NutSink, NutSource, NutFunction
from scipy.cluster.vq import vq, kmeans, whiten
import numpy as np

class PosterizeDepth(NutFunction):
	"""
	Reduces the number of depth levels (distinct Z values) in a point cloud. This is analogous to
	posterizing colors in 2D images.
	"""
	def __init__(self,levels=5,zPadding=None):
		"""
		levels: The number of intervals of z-values.
		zPadding: Add this much distance in between each Z layer.
		"""
		self._levels = levels
		self._zPadding = zPadding
		
	def __call__(self, element):
		"""
		element: A DepthCloud
		"""
		points = element.getPoints()
		zValues = points[:,2]
		whitenedValues = whiten(zValues)
		centroids,distortion = kmeans(whitenedValues,self._levels)
		clusterIndices,_ = vq(whitenedValues,centroids) 
		centroids = centroids * np.std(zValues) #unwhiten the centroids
		if self._zPadding != None:
			#padding = np.array([self._zPadding*(i+1) for i in range(self._levels)])
			padding = np.array([self._zPadding for i in range(self._levels)])
			centroids = centroids + padding
		for i in range(self._levels):
			clusterIndices[clusterIndices==i] = centroids[i]
		points[:,2] = clusterIndices
		element.setPoints(points)
		return element
		
