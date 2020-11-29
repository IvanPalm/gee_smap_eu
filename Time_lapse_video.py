import ee
from ee import batch

def ee_init():
    try:
        ee.Initialize()
        print('Google Earth Engine API Initialized')
    except Exception:
        ee.Authenticate()
        ee.Initialize()

ee_init()

# Define region of interest for Aral Sea
coo_roi = [
    [56.42475, 47.00722],
    [62.94932,47.00722],
    [56.42475,42.75721],
    [62.94932,42.75721]
]
roi = ee.Geometry.Polygon(coo_roi)

## define your collection
# l4 = ee.ImageCollection('LANDSAT/LT04/C01/T1_SR')\
#     .filter(ee.Filter.calendarRange(8, 8, 'month'))\
#     .filterBounds(roi)\
#     .filter(ee.Filter.lt('CLOUD_COVER_LAND', 5))
# l4.size().getInfo()
#
# l5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR')\
#     .filter(ee.Filter.calendarRange(8, 8, 'month'))\
#     .filterBounds(roi)\
#     .filter(ee.Filter.lt('CLOUD_COVER_LAND', 5))
# l5.size().getInfo()
#
# l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')\
#     .filter(ee.Filter.calendarRange(8, 8, 'month'))\
#     .filterBounds(roi)\
#     .filter(ee.Filter.lt('CLOUD_COVER_LAND', 5))
# l7.size().getInfo()
#
# l8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')\
#     .filter(ee.Filter.calendarRange(8, 8, 'month'))\
#     .filterBounds(roi)\
#     .filter(ee.Filter.lt('CLOUD_COVER_LAND', 5))
# l8.size().getInfo()

# col = coll8412.merge(coll1320)
# print(f'{col.size().getInfo()} Landsat images gathered for the region of interest')
#
# # Composite by month each year
# startYear = 1984
# endYear = 2020
#
# # Define a reducer.
# myReducer = ee.Reducer.mean()
#
# # Make a list of years to generate composites for
# yearList = ee.List.sequence(startYear, endYear)
#
# def compbyYear(year):
#   # Filter the merged collection by the given year
#   yearCol = col.filter(ee.Filter.calendarRange(year, year, 'year'))
#   # Make a list of filtered images for this year as a record
#   imgList = yearCol.aggregate_array('LANDSAT_ID')
#   # Reduce (composite) the images for this year
#   yearComp = yearCol.reduce(myReducer)
#   # Count the number of bands (used as a filter in a following step)
#   nBands = yearComp.bandNames().size()
#   # Return the intra-annual composite - set properties just defined
#   return yearComp.set({
#     'year': year,
#     'image_list': imgList,
#     'n_bands': nBands
#   })
#
# # Map over the list of years to generate a composite for each year - returns an List.
# yearCompList = yearList.map(compbyYear)
#
# # Convert the annual composite image List to an ImageCollection
# yearCompCol = ee.ImageCollection.fromImages(yearCompList)
#
# # Filter out years with no bands (it can happen if there were no images to composite)
# yearCompCol = yearCompCol.filter(ee.Filter.gt('n_bands', 0))
# print('Images have been composite by year')
# # select bands for true colour
# truecol = yearCompCol.select(['B4_mean', 'B3_mean', 'B2_mean'])
# # truecol.size().getInfo()
#
# # make the data 8-bit.
# def convertBit(image):
#     return image.multiply(512).uint8()
#
# # call the conversion
# outputVideo = truecol.map(convertBit)
#
# print("Generating export task")
#
# # Export to video
# out = batch.Export.video.toDrive(outputVideo,
#     description='aral_timelapse_1984_2020',
#     dimensions = 720,
#     framesPerSecond = 2,
#     region=(roi),
#     maxFrames=10000)
#
# # process the image
# process = batch.Task.start(out)
#
# print("Process on the way to your Google Drive!")

# set cloud threshold and time window
cloud_thresh = 20
start_year = 1982
end_year = 2020
print(f'The cloud threshold is set to {cloud_thresh}%')

# import collections
l4 = ee.ImageCollection('LANDSAT/LT04/C01/T1_TOA')\
    .filter(ee.Filter.lt('CLOUD_COVER_LAND', cloud_thresh))
l5 = ee.ImageCollection('LANDSAT/LT05/C01/T1_TOA')\
    .filter(ee.Filter.lt('CLOUD_COVER_LAND', cloud_thresh))
l7 = ee.ImageCollection('LANDSAT/LE07/C01/T1_TOA')\
    .filter(ee.Filter.lt('CLOUD_COVER_LAND', cloud_thresh))
l8 = ee.ImageCollection('LANDSAT/LC08/C01/T1_TOA')\
    .filter(ee.Filter.lt('CLOUD_COVER_LAND', cloud_thresh))
print(f'Image collections for the period {start_year}-{end_year} are ready for processing')

# define the period
years = ee.List.sequence(start_year, end_year, 1)

l4names = ee.List(["B1","B2","B3","B4","B5","B6","B7","BQA"])
l5names = ee.List(["B1","B2","B3","B4","B5","B6","B7","BQA"])
l7names = ee.List(["B1","B2","B3","B4","B5","B6_VCID_1","B6_VCID_2","B7","B8","BQA"])
l8names = ee.List(["B1","B2","B3","B4","B5","B6","B7","B8","B9","B10","B11","BQA"])

# bands
l4Bands = ee.List(['blue','green','red','nir','swir1','tir','swir2','fmask'])
l5Bands = ee.List(['blue','green','red','nir','swir1','tir','swir2','fmask'])
l7Bands = ee.List(['blue','green','red','nir','swir1','tir1','tir2', 'swir2','pan','fmask'])
l8Bands = ee.List(['coast_aerosol','blue','green','red','nir','swir1','swir2','cir','tir1','tir2','pan','BQA'])

# Filter based on location
l4images  = l4.filterBounds(roi)
l5images  = l5.filterBounds(roi)
l7images  = l7.filterBounds(roi)
l8images  = l8.filterBounds(roi)

# Functions
def getQABits(image, start, end, mask):
    # Compute the bits we need to extract.
    pattern = 0
    for i in range(start, end+1):
        pattern += 2**i
    # Return a single band image of the extracted QA bits, giving the     band a new name.
    return image.select([0], [mask]).bitwiseAnd(pattern).rightShift(start)

def maskQuality(image):
    # Select the QA band.
    QA = image.select('BQA')
    # Get the internal_cloud_algorithm_flag bit.
    shade = getQABits(QA, 3, 3, 'cloud_shadow')
    cloud = getQABits(QA, 5, 5, 'cloud')
    #  var cloud_confidence = getQABits(QA,6,7,  'cloud_confidence')
    cirrus_detected = getQABits(QA, 9, 9, 'cirrus_detected')
    #Return an image masking out cloudy areas.
    return image.updateMask(shade.eq(0)).updateMask(cloud.eq(0).updateMask(cirrus_detected.eq(0)))

# mask all clouds in the image collection
l4images = l4images.map(maskQuality)
l5images = l5images.map(maskQuality)
l7images = l7images.map(maskQuality)
l8images = l8images.map(maskQuality)

# Change the bandnames
l4images = l4images.select(l4names,l4Bands)
l5images = l5images.select(l5names,l5Bands)
l7images = l7images.select(l7names,l7Bands)
l8images = l8images.select(l8names,l8Bands)

# Combine all data in single collection
myCollection = ee.ImageCollection(
    l4images.merge(l5images)
    .merge(l7images)
    .merge(l8images))

# Select the red, green an blue bands
myCollection = myCollection.select(['red','green','blue'])

# calculate an image for every year
def compYear(y):
    image = myCollection.filter(ee.Filter.calendarRange(y, y, 'year')).median()
    return image.set('year', 2000)\
        .set('date', ee.Date.fromYMD(y, 1, 1))\
        .set('system:time_start',ee.Date.fromYMD(y, 1, 1))

yearlymap = ee.ImageCollection(years.map(compYear))
# Filter out years with no bands (it can happen if there were no images to composite)
yearlymap = yearlymap.filter(ee.Filter.gt('n_bands', 0))
print('Images are composite by year')

# we need an 8-bit format
def convertBit(image):
    return image.multiply(512).uint8()

coll4Video = yearlymap.map(convertBit)

# Export to video
out = batch.Export.video.toDrive(coll4Video,
    description='aral_timelapse_1984_2020',
    dimensions = 720,
    framesPerSecond = 2,
    region=(roi),
    maxFrames=10000)

# process the image
process = batch.Task.start(out)

print("Process on the way to your Google Drive!")
