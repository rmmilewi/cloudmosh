from cloudmosh.components.base import CloudMoshComponent
import os
import numpy as np
# Keras / TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'
from keras.models import load_model
import skimage.io
from skimage.transform import resize
from keras.engine.topology import Layer, InputSpec
import keras.utils.conv_utils as conv_utils
import tensorflow as tf
import keras.backend as K

from nutsflow.base import Nut,NutSink, NutSource, NutFunction

class AWBilinearUpSampling2D(Layer):
    """
    This is a custom-defined layer needed by the Alhashim-Wonka network.
    """
    def __init__(self, size=(2, 2), data_format=None, **kwargs):
        super(AWBilinearUpSampling2D, self).__init__(**kwargs)
        self.data_format = K.normalize_data_format(data_format)
        self.size = conv_utils.normalize_tuple(size, 2, 'size')
        self.input_spec = InputSpec(ndim=4)

    def compute_output_shape(self, input_shape):
        if self.data_format == 'channels_first':
            height = self.size[0] * input_shape[2] if input_shape[2] is not None else None
            width = self.size[1] * input_shape[3] if input_shape[3] is not None else None
            return (input_shape[0],
                    input_shape[1],
                    height,
                    width)
        elif self.data_format == 'channels_last':
            height = self.size[0] * input_shape[1] if input_shape[1] is not None else None
            width = self.size[1] * input_shape[2] if input_shape[2] is not None else None
            return (input_shape[0],
                    height,
                    width,
                    input_shape[3])

    def call(self, inputs):
        input_shape = K.shape(inputs)
        if self.data_format == 'channels_first':
            height = self.size[0] * input_shape[2] if input_shape[2] is not None else None
            width = self.size[1] * input_shape[3] if input_shape[3] is not None else None
        elif self.data_format == 'channels_last':
            height = self.size[0] * input_shape[1] if input_shape[1] is not None else None
            width = self.size[1] * input_shape[2] if input_shape[2] is not None else None
        
        return tf.image.resize_images(inputs, [height, width], method=tf.image.ResizeMethod.BILINEAR, align_corners=True)

    def get_config(self):
        config = {'size': self.size, 'data_format': self.data_format}
        base_config = super(AWBilinearUpSampling2D, self).get_config()
        return dict(list(base_config.items()) + list(config.items()))

class AWDepthEstimator(Nut):
	"""
	Contains the code for the depth detection step, adapted
	from https://github.com/ialhashim/DenseDepth, the repository
	for the 2018 pre-print by Alhashim and Wonka entitled
    'High Quality Monocular Depth Estimation via Transfer Learning'.
	"""
	
	#The network used by the Depth Detector expects images to be of size 640x480
	EXPECTED_IMAGE_WIDTH = 640
	EXPECTED_IMAGE_HEIGHT = 480
	
	def __init__(self,modelPath,minDepth=10,maxDepth=1000,batchSize=2):
		"""
		modelPath: The path to the model file that contains the trained network (e.g. 'data/nyu.h5').
		minDepth (optional): The minimum depth that the network is allowed to assign a pixel. Default 10.
		maxDepth (optional): The maximum depth that the network is allowed to assign a pixel. Default 1000.
		batchSize (optional): How many images the network should process at once. Default 2.
		"""
		super().__init__()
		
		self._depthModelPath = modelPath
		self._minDepth = minDepth
		self._maxDepth = maxDepth
		self._batchSize = batchSize
		
		#Custom object needed for inference and training
		custom_objects = {'BilinearUpSampling2D': AWBilinearUpSampling2D, 'depth_loss_function': None}
		
		self._model = load_model(self._depthModelPath, custom_objects=custom_objects, compile=False)
		
		
	def setMinDepth(self,minDepth):
		self._minDepth = minDepth
		
	def setMaxDepth(self,maxDepth):
		self._maxDepth = maxDepth
		
	def setBatchSize(self,batchSize):
		self._batchSize = batchSize
		
	def __resize(self,images,width,height):
		"""
		width: The desired width of the resulting image(s).
		height: The desired height of the resulting image(s).
		"""
		shape = (images.shape[0],width,height,images.shape[3])
		return resize(images, shape, preserve_range=True, mode='reflect')
		
	def __depthNorm(self,x):
		return self._maxDepth / x
		
	def __rrshift__(self,iterable):
		for data in iterable:
			if len(data.shape) == 3:
				#(width,height,color)
				originalWidth = data.shape[0]
				originalHeight = data.shape[1]
			else:
				#(index,width,height,color)
				originalWidth = data.shape[1]
				originalHeight = data.shape[2]
		
			data = np.clip(data / 255, 0, 1)
			
			# Support multiple RGBs, one RGB image, even grayscale
			if len(data.shape) < 3:
				#If the image(s) are grayscale, we convert them to an RGB equivalent (v -> <v,v,v>).
				data = np.stack((data,data,data), axis=2)
			if len(data.shape) < 4:
				data = data.reshape((1, data.shape[0], data.shape[1], data.shape[2]))
			
			if data.shape[-1] == 4:
				#Drop the alpha component from RGBA. The network only cares about RGB.
				#e.g. (1,640,480,4) -> (1,640,480,3)
				data = data[:,:,:,:3]

		
			#The network used by the Depth Detector expects images to be of size 640x480
			data = self.__resize(data,width=AWDepthEstimator.EXPECTED_IMAGE_WIDTH,height=AWDepthEstimator.EXPECTED_IMAGE_HEIGHT)
		
			# Compute predictions
			predictions = self._model.predict(data, batch_size=self._batchSize)
			# Put in expected range
			predictions = np.clip(self.__depthNorm(predictions), self._minDepth, self._maxDepth)
			#Resize to original width and height.
		
			predictions = self.__resize(predictions,width=originalWidth,height=originalHeight)
		
			yield predictions
		