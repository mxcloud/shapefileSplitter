from qgis.core import *
import processing   # utilize the Processing Framework
import os, errno

districtNumber = "districts100" #Congressional Districts came in this lumped files name for the entire united states
inputURI = "//path//to//shapefile//" +districtNumber+".shp"
outputURI = r"//path//to//saved//file//" + districtNumber + "//"
CongressNumber = districtNumber[-3:] + "_Congress"

# attribute with values to use for splittting and getting a list of Unique names from the Shapefile's Attribute Table.
field = 'STATENAME' 
districtField = 'DISTRICT'
#neccessary argument which means 'equals'
operator = 0 

def uniqueFields(inputURI, field):
    # obtain dictionary object that contains unique values from specified field
    unique = processing.runalg('qgis:listuniquevalues', inputURI, field, None)
    # get the list of unique values from the dictionary's UNIQUE_VALUES key
    # unique values are in a semicolan delimeted string, so split them at them
    # at the same time to a Python array
    values = unique['UNIQUE_VALUES'].split(';')
    return values

def addDir(outputURI):
    #makes a directory to section off data by state or file format
    try:
        os.makedirs(outputURI)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

stateName = uniqueFields(inputURI, field) #puts state names into a list used later to seperate shape files
addDir(outputURI)
#seperate shapefiles by unique shape name
for s in stateName:
    processing.runalg('qgis:extractbyattribute', inputURI, field, operator, s, outputURI + districtNumber + "_"+s)

for s in stateName:
    #get the State's unique District number's
    districts = uniqueFields( outputURI + districtNumber+"_"+s+".shp", districtField)
    #Create seperate directory for that state
    stateURI = outputURI + s + "//"
    addDir(stateURI)
    #While splitting the states shapefile into distinct districts
    #The shapefiles are also saved as GEOJSON
    for d in districts:
        processing.runalg('qgis:extractbyattribute', outputURI + districtNumber+"_"+s+".shp",districtField, operator, d, stateURI + CongressNumber+ "_" + s +"_district"+ d)
        addDir(stateURI + "GeoJSON")
        #To save the shape file as GEOJSON the shapefile needs to be loaded as a vector layer
        vectorLyr= QgsVectorLayer(stateURI + CongressNumber+ "_" + s +"_district"+ d +".shp",CongressNumber+ "_" + s +"_district"+ d , "ogr")
        error =QgsVectorFileWriter.writeAsVectorFormat(vectorLyr, stateURI + "GeoJSON//" + CongressNumber+ "_" + s +"_district"+ d +".json", "utf-8", None, "GeoJSON")
        if error == QgsVectorFileWriter.NoError:
            print ("success!")
        QgsMapLayerRegistry.instance().removeMapLayer(vectorLyr)