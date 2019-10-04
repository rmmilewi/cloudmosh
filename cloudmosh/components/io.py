import os
import imageio
import numpy as np
from nutsflow.base import NutSink, NutSource
import nutsflow
from cloudmosh.components.base import CloudMoshSource

class ReadImageAsBinary(NutSource):
	"""
		Reads (non-animated) image(s) from file(s) as bytes.
	"""
	def __init__(self,*paths):
		self._paths = paths
		
	def __rrshift__(self, iterable):
		"""
		Like the base implementation of NutSource, ReadImage will raise an exception
		if the user tries to right-shift input into it. We're overriding this method so that the exception
		is generated within the cloudmosh codebase and not the dependency (nutsflow).
		"""
		raise SyntaxError("ReadImageAsBinary is a data source, '__ >> source' is an invalid operation.")
		
	def __iter__(self):
		return self
		
	def __next__(self):
		pass #TODO
		#for imagePath in self._paths:


class ReadImage(NutSource):
	"""
	Reads (non-animated) image(s) from file(s) as arrays of RGB values.
	"""
	def __init__(self,*paths):
		"""
		paths: One or more path strings to image files in formats like JPG or PNG.
		"""
		self._paths = paths
		
	def __rrshift__(self, iterable):
		"""
		Like the base implementation of NutSource, ReadImage will raise an exception
		if the user tries to right-shift input into it. We're overriding this method so that the exception
		is generated within the cloudmosh codebase and not the dependency (nutsflow).
		"""
		raise SyntaxError("ReadImage is a data source, '__ >> source' is an invalid operation.")
	
	def __iter__(self):
		self._index = 0
		return self
	
	def __next__(self):
		if self._index >= len(self._paths):
			self._index = 0
			raise StopIteration
		imagePath = self._paths[self._index]
		img = imageio.imread(imagePath)
		arr = imageio.core.asarray(img)
		if len(arr.shape) == 3:
			output = arr.reshape((1, arr.shape[0], arr.shape[1], arr.shape[2]))
		else: #arr == 2, this is a depth image
			output = arr.reshape((1, arr.shape[0], arr.shape[1], 1))
		self._index += 1
		return output

class SaveImage(NutSink):
	"""
	Saves an image as a file.
	"""
	def __init__(self,*paths):
		"""
		paths: One or more path strings to image files in formats like JPG or PNG.
		"""
		self._paths = paths
	
	def __iter__(self):
		"""
		Like the base implementation of NutSink, SaveImage will raise an exception
		if the user tries to read output from it. We're overriding this method so that the exception
		is generated within the cloudmosh codebase and not the dependency (nutsflow).
		"""
		raise SyntaxError("SaveImage is a data sink and does not produce outputs to iterate over.")
		
	def __rrshift__(self,iterable):
		images = iterable >> nutsflow.Collect()
		paths = self._paths >> nutsflow.Collect()
		if len(images) != len(paths):
			raise IOError("SaveImage received an unequal number of images and paths to which to save them ({0} images, {1} paths).".format(len(images),len(paths)))
		for i in range(len(paths)):
			img = images[i]
			path = paths[i]
			if len(img.shape) == 4:
				img = img.reshape((img.shape[1], img.shape[2], img.shape[3]))
			imageio.imsave(path, img)

class ReadVideoOrGIF(NutSource):
	def __init__(self,*paths):
		"""
		paths: One or more paths to video or GIF files.
		"""
		self._paths = paths
		
	def __rrshift__(self, iterable):
		"""
		Like the base implementation of NutSource, ReadVideoOrGIF will raise an exception
		if the user tries to right-shift input into it. We're overriding this method so that the exception
		is generated within the cloudmosh codebase and not the dependency (nutsflow).
		"""
		raise SyntaxError("ReadVideoOrGIF is a data source, '__ >> source' is an invalid operation.")
		
	def __iter__(self):
		self._index = 0
		return self
		
	def __next__(self):
		if self._index >= len(self._paths):
			self._index = 0
			raise StopIteration
		fPath = self._paths[self._index]
		reader = imageio.get_reader(fPath)
		output = []
		for num, img in enumerate(reader):
			arr = imageio.core.asarray(img)
			if len(arr.shape) == 3:
				arr = arr.reshape((1, arr.shape[0], arr.shape[1], arr.shape[2]))
			else: #arr == 2, this is a depth image
				arr = arr.reshape((1, arr.shape[0], arr.shape[1], 1))
			output.append(arr)
		self._index += 1
		return output

class SaveGIF(NutSink):
	"""
	Saves one or more iterables of images as GIFs.
	"""
	def __init__(self,*paths):
		"""
		paths: One or more path strings to image files in formats like JPG or PNG.
		"""
		self._paths = paths
	
	def __iter__(self):
		"""
		Like the base implementation of NutSink, SaveGIF will raise an exception
		if the user tries to read output from it. We're overriding this method so that the exception
		is generated within the cloudmosh codebase and not the dependency (nutsflow).
		"""
		raise SyntaxError("SaveGIF is a data sink and does not produce outputs to iterate over.")
		
	def __rrshift__(self,iterable):
		sequences = iterable >> nutsflow.Collect()
		paths = self._paths >> nutsflow.Collect()
		if len(sequences) != len(paths):
			raise IOError("SaveGIF received an unequal number of sequences and paths to which to save them ({0} sequences, {1} paths).".format(len(sequences),len(paths)))
		for i in range(len(paths)):
			sequence = sequences[i]
			path = paths[i]
			for i in range(len(sequence)):
				if len(sequence[i].shape) == 4:
					sequence[i] = sequence[i].reshape((sequence[i].shape[1], sequence[i].shape[2], sequence[i].shape[3]))
			imageio.mimsave(path, sequence)