import ee
from ee import batch


# Authenticate to erth engine
def ee_init():
    try:
        ee.Initialize()
        print('Google Earth Engine API Initialized')
    except Exception:
        ee.Authenticate()
        ee.Initialize()


# make the data 8-bit.
def convertBit(image):
    return image.multiply(512).uint8()


ee_init()
# Draw rectangle around Aral sea
coo_roi = [
    [57.2, 47],
    [62, 47],
    [62, 43.2],
    [57.2, 43.2]
]

roi = ee.Geometry.Polygon(coo_roi)

# Define collection
l8 = ee.ImageCollection('LANDSAT/LC8_L1T_TOA')\
 .filterBounds(roi)
l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_TOA')\
 .filterBounds(roi)
l5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_TOA')\
 .filterBounds(roi)

collection = l5.merge(l7.merge(l8))
# Filter cloudy scenes
clouds = collection.filter(ee.Filter.lt('CLOUD_COVER', 5))

# Select the bands, we are going for true colour... but could be any!
bands = clouds.select(['B4', 'B3', 'B2'])

# convert to 8 bit
outputVideo = bands.map(convertBit)

# Export to video.
out = batch.Export.video.toDrive(
    outputVideo,
    description='aral_video',
    dimensions=720,
    framesPerSecond=2,
    region=(roi),
    maxFrames=10000)

# process the image
process = batch.Task.start(out)
