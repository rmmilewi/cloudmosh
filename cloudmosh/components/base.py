from abc import ABC,abstractmethod

from nutsflow.base import Nut, NutSink, NutSource, NutFunction

class CloudMoshMixIn:
	pass
	
class CloudMoshNut(Nut,CloudMoshMixIn):
	pass

class CloudMoshSink(NutSink,CloudMoshMixIn):
	pass
	
class CloudMoshSource(NutSource,CloudMoshMixIn):
	pass
	
class CloudMoshFunction(NutFunction,CloudMoshMixIn):
	pass


	

class CloudMoshComponent(ABC):
	def __init__(self):
		#"""
		#params (optional): A dictionary mapping strings to values for setting
		#the parameters of a component.
		#"""
		super().__init__()
	
	@abstractmethod
	def __rrshift__(self,data):
		"""
		This is the primary method of any component. A component
		takes in input (data) and produces some output. Overriding
		the '>>' operator allows the frontend code to chain together
		a pipeline in a clean way, like so:
		originalInput >> componentA >> componentB >> componentC
		which is equivalent to writing:
		componentC.__rshift__(componentB.__rshift__(componentA.__rshift__(originalInput)))
		"""
		pass