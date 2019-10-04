from cloudmosh.components.io import ReadImage,SaveImage,ReadVideoOrGIF,SaveGIF
import nutsflow
import pytest
import numpy as np

#TODO: Test transparent PNGs
#TODO: Test load image-as-binary and conversion to RGB.

def test_ReadImage_PNG():
	result = ReadImage("test/testdata/colorbars.png") >> nutsflow.Collect()
	assert(len(result) == 1)
	img = result[0]
	assert(img.shape == (1,48,64,3))
	
def test_ReadImage_JPG():
	result = ReadImage("test/testdata/colorbars.jpg") >> nutsflow.Collect()
	assert(len(result) == 1)
	img = result[0]
	assert(img.shape == (1,48,64,3))

def test_ReadImage_FileNotFoundError():
	with pytest.raises(FileNotFoundError):
		result = ReadImage("garbage") >> nutsflow.Collect()
		
def test_ReadImage_RRShiftUnsupported():
	with pytest.raises(SyntaxError):
		[1,2,3] >> ReadImage("test/testdata/colorbars.jpg")

def test_ReadImage_MultipleFiles():
	result = ReadImage("test/testdata/colorbars.png","test/testdata/colorbars.jpg") >> nutsflow.Collect()
	assert(len(result) == 2)
	
def test_ReadImage_RepeatLoad():
	resultA = ReadImage("test/testdata/colorbars.png") >> nutsflow.Collect()
	resultB = ReadImage("test/testdata/colorbars.png") >> nutsflow.Collect()
	assert(id(resultA[0]) != id(resultB[0]))
	
def test_SaveImage_PNG(tmpdir_factory):
	fn = tmpdir_factory.mktemp("temporaryfiles").join("tmp.png")
	ReadImage("test/testdata/colorbars.png") >> SaveImage(str(fn))
	
def test_SaveImage_JPG(tmpdir_factory):
	fn = tmpdir_factory.mktemp("temporaryfiles").join("tmp.jpg")
	ReadImage("test/testdata/colorbars.jpg") >> SaveImage(str(fn))
	
def test_SaveImage_MultipleFiles_MultiRead(tmpdir_factory):
	result = ReadImage("test/testdata/colorbars.png","test/testdata/colorbars.jpg")
	fnA = tmpdir_factory.mktemp("temporaryfiles").join("tmpA.png")
	fnB = tmpdir_factory.mktemp("temporaryfiles").join("tmpB.png")
	result >> SaveImage(str(fnA),str(fnB))

def test_SaveImage_MultipleFiles_MultiRead_Mismatch(tmpdir_factory):
	with pytest.raises(OSError):
		result = ReadImage("test/testdata/colorbars.png","test/testdata/colorbars.jpg")
		fnA = tmpdir_factory.mktemp("temporaryfiles").join("tmpA.png")
		result >> SaveImage(str(fnA))
	
def test_SaveImage_MultipleFiles_SingleReads(tmpdir_factory):
	resultA = ReadImage("test/testdata/colorbars.png") >> nutsflow.Collect()
	resultB = ReadImage("test/testdata/colorbars.jpg") >> nutsflow.Collect()
	fnA = tmpdir_factory.mktemp("temporaryfiles").join("tmpA.png")
	fnB = tmpdir_factory.mktemp("temporaryfiles").join("tmpB.png")
	[resultA[0],resultB[0]] >> SaveImage(str(fnA),str(fnB))
	
def test_SaveImage_then_ReadImage_PNG(tmpdir_factory):
	fn = tmpdir_factory.mktemp("temporaryfiles").join("tmp.png")
	resultA = ReadImage("test/testdata/colorbars.png") >> nutsflow.Collect()
	resultA >> SaveImage(str(fn))
	resultB = (ReadImage(str(fn)) >> nutsflow.Collect())
	img_original = resultA[0]
	img_reloaded = resultB[0]
	assert(img_original.shape == img_reloaded.shape)
	assert(np.array_equal(img_original,img_reloaded))

def test_SaveImage_then_ReadImage_JPG_NotEqual(tmpdir_factory):
	fn = tmpdir_factory.mktemp("temporaryfiles").join("tmp.jpg")
	resultA = ReadImage("test/testdata/colorbars.jpg") >> nutsflow.Collect()
	resultA >> SaveImage(str(fn))
	resultB = (ReadImage(str(fn)) >> nutsflow.Collect())
	img_original = resultA[0]
	img_reloaded = resultB[0]
	assert(img_original.shape == img_reloaded.shape)
	assert(not np.array_equal(img_original,img_reloaded))
	
def test_ReadVideoOrGIF_GIF():
	result = ReadVideoOrGIF("test/testdata/shore.gif") >> nutsflow.Collect()
	assert(len(result) == 1)
	gif = result[0]
	assert(len(gif) == 21)
	assert(gif[0].shape == gif[1].shape)

def test_ReadVideoOrGIF_MP4():
	result = ReadVideoOrGIF("test/testdata/video.mp4") >> nutsflow.Collect()
	assert(len(result) == 1)
	video = result[0]
	assert(len(video) == 205)
	assert(video[0].shape == video[1].shape)
	
def test_ReadVideoOrGIF_MultipleFiles():
	result = ReadVideoOrGIF("test/testdata/shore.gif","test/testdata/video.mp4") >> nutsflow.Collect()
	assert(len(result) == 2)
	
def test_ReadVideoOrGIF_RRShiftUnsupported():
	with pytest.raises(SyntaxError):
		[1,2,3] >> ReadVideoOrGIF("test/testdata/shore.gif")
	
#TODO: I need to figure out why this test takes 12 seconds...
#def test_ReadVideoOrGIF_then_SaveGIF_MP4(tmpdir_factory):
#	fn = tmpdir_factory.mktemp("temporaryfiles").join("tmp.gif")
#	ReadVideoOrGIF("test/testdata/video.mp4") >> SaveGIF(str(fn))
	

def test_ReadGIF_then_SaveGIF(tmpdir_factory):
	fn = tmpdir_factory.mktemp("temporaryfiles").join("tmp.gif")
	ReadVideoOrGIF("test/testdata/shore.gif") >> SaveGIF(str(fn))

def test_ReadVideoOrGIF_RepeatLoad():
	resultA = ReadVideoOrGIF("test/testdata/shore.gif") >> nutsflow.Collect()
	resultB = ReadVideoOrGIF("test/testdata/shore.gif") >> nutsflow.Collect()
	assert(id(resultA[0]) != id(resultB[0]))
	
def test_SaveGIF_MultipleFiles_MultiRead(tmpdir_factory):
	result = ReadVideoOrGIF("test/testdata/shore.gif","test/testdata/shore.gif")
	fnA = tmpdir_factory.mktemp("temporaryfiles").join("tmpA.gif")
	fnB = tmpdir_factory.mktemp("temporaryfiles").join("tmpB.gif")
	result >> SaveGIF(str(fnA),str(fnB))
	
	
	
