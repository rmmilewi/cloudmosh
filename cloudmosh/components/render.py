from cloudmosh.components.base import CloudMoshComponent
import pyrender
import numpy as np
from nutsflow.base import NutSink

#TODO: Temporary fix so I can get the pose information I need
def cm_on_mouse_press(self, x, y, buttons, modifiers):
	self.original_mouse_press(x, y, buttons, modifiers)
	print(np.array2string(self._trackball.pose,separator=','))

#pyrender.Viewer.original_mouse_press = pyrender.Viewer.on_mouse_press
#pyrender.Viewer.on_mouse_press = cm_on_mouse_press

class SimpleCloudView(NutSink):
	"""
	Renders a cloud in a Pyrender-generated window.
	"""

	def __init__(self,point_size=9):
		super().__init__()
		self._point_size = point_size
		
	def __iter__(self):
		raise SyntaxError("SimpleCloudView is a data sink and does not produce outputs to iterate over.")
		
	def __rrshift__(self,iterable):
		scene = pyrender.Scene(ambient_light=[1.0, 1.0, 1.0, 1.0],bg_color=[0.0, 0.0, 0.0])
		for cloud in iterable:
			points = cloud.getPoints()
			colors = cloud.getColors()
			print("SimpleCloudView: points.shape == ", points.shape)
			print("SimpleCloudView: colors.shape == ", colors.shape)
			print(points[:,2])
		
			mesh = pyrender.Mesh.from_points(points,colors=colors)
			scene.add(mesh)
		pyrender.Viewer(scene, use_raymond_lighting=False,point_size=self._point_size)
	

			
class OffscreenCloudRender(CloudMoshComponent):
	def __init__(self):
		super().__init__()
		
	def _getDefaultCameraPose(self,scene):
		centroid = scene.centroid
		scale = 0.5 #The default is two
		s2 = 1.0 / np.sqrt(2.0)
		cp = np.eye(4)
		cp[:3,:3] = np.array([
			[0.0, -s2, s2],
			[1.0, 0.0, 0.0],
			[0.0, s2, s2]
		])
		hfov = np.pi / 6.0
		dist = scale / (2.0 * np.tan(hfov))
		cp[:3,3] = dist * np.array([1.0, 0.0, 1.0]) + centroid
		return cp

		
	def __rrshift__(self,iterable):
		renderer = pyrender.OffscreenRenderer(viewport_width=640,viewport_height=480,point_size=9.0)
		camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1.0)
		
		#TMP TMP TMP
		#fixed_pose = np.array([[ 3.48994967e-02,-9.96319684e-01,-7.82886503e-02,1.90910565e+02],
		#	[-9.99390827e-01,-3.47922500e-02,-2.73389991e-03,3.57034963e+02],
		#	[ 0.00000000e+00,7.83363707e-02,-9.96926985e-01,-3.85617716e+02],
		#	[ 0.00000000e+00,0.00000000e+00,0.00000000e+00,1.00000000e+00]])
		fixed_pose=[[  -0.67965718,  -0.67467772,   0.28788207, 218.90296805],
		[  -0.5763984 ,   0.24848092,  -0.77847422,-201.12334648],
		[   0.45368601,  -0.69503036,  -0.557765  , -31.37713392],
		[   0.        ,   0.        ,   0.        ,   1.        ]]
		#light = pyrender.SpotLight(color=np.ones(3), intensity=3.0, innerConeAngle=np.pi/16.0,outerConeAngle=np.pi/6.0)
		for cloud in iterable:
			points = cloud.getPoints()
			colors = cloud.getColors()
			mesh = pyrender.Mesh.from_points(points,colors=colors)
			scene = pyrender.Scene(ambient_light=[1.0, 1.0, 1.0, 1.0],bg_color=[0.0, 0.0, 0.0])
			scene.add(mesh)
			camera_pose = fixed_pose#self._getDefaultCameraPose(scene)
			scene.add(camera,pose=camera_pose)
			#scene.add(light,pose=camera_pose)
			colorImage, _ = renderer.render(scene)
			yield colorImage

		
		
	