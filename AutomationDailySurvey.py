import arcpy
import pandas as pd
from datetime import date
import subprocess
import shutil
import os
date= date.today()
esriDate=str(date).replace('-','')
mxd_path = r"G:/gis_automation/automationSurvey.mxd"
mxd = arcpy.mapping.MapDocument(mxd_path)
for df in arcpy.mapping.ListDataFrames(mxd):
    layers = arcpy.mapping.ListLayers(mxd,"",df)
    for lyr in layers:
        arcpy.mapping.RemoveLayer(df,lyr)
mxd.save()
folderPath = "G:/gis_automation/%s_AutomationSurvey"%date
if os.path.isdir(folderPath):
    shutil.rmtree(folderPath)
    os.makedirs(folderPath)
else:
    os.makedirs(folderPath)
spatialReference = arcpy.SpatialReference(4326)
arcpy.env.overwriteOutput = True
surveyData =r"G:/gis_python/2025-12-18_Hybrid_csv_120617.csv"
dfSurveyData = pd.read_csv(surveyData)
savedLayer = (r"%s/%sSurvey.lyr" %(folderPath,date))
arcpy.management.MakeXYEventLayer(surveyData,"E","N",("%ssurvey"%esriDate),
                                  spatialReference,"Z")
arcpy.SaveToLayerFile_management("%ssurvey"%esriDate, savedLayer)
outputFcName=("%sline_fc.shp"%esriDate)
arcpy.CreateFeatureclass_management(
    out_path=folderPath,
    out_name=outputFcName,
    geometry_type="POLYLINE",
    spatial_reference=spatialReference
    )
cursor = arcpy.da.InsertCursor("%s/%s"%(folderPath,outputFcName),["SHAPE@"])
array=arcpy.Array()
for e,n,d in zip(dfSurveyData['E'],dfSurveyData['N'],dfSurveyData['Desc']):
    if (d=='set_base'):
        pass
    else:
        point = arcpy.Point(e,n)
        array.add(point)
polyline = arcpy.Polyline(array,spatialReference)
cursor.insertRow([polyline])
del cursor
lineToPolygon="%sLineToPolygon.shp"%esriDate
arcpy.management.FeatureToPolygon(
        in_features="%s/%s"%(folderPath,outputFcName), 
        out_feature_class="%s/%s"%(folderPath,lineToPolygon)
    )
attributeFields= ["Remarks","Date","Parcel_No","Area"]
for each in attributeFields:
    if each=="Area":
        arcpy.AddField_management("%s/%s"%(folderPath,lineToPolygon),
                           each,"DOUBLE")
    else:
        arcpy.AddField_management("%s/%s"%(folderPath,lineToPolygon),
                           each,"Text")
cursor = arcpy.UpdateCursor("%s/%s"%(folderPath,lineToPolygon))
parcel=1
for row in cursor:
    row.setValue("Remarks", "By Muhammad Ali")
    row.setValue("Date", str(date))
    row.setValue("Parcel_No", str(parcel))
    parcel=parcel+1
    cursor.updateRow(row)
del cursor
arcpy.CalculateField_management("%s/%s"%(folderPath,lineToPolygon), "Area", "!shape!.area", "Python")
line = "%s/%s"%(folderPath,outputFcName)
polygon = "%s/%s"%(folderPath,lineToPolygon)
shapefiles = [savedLayer,line,polygon]
dfTwo = arcpy.mapping.ListDataFrames(mxd, "*")[0]
for each in shapefiles:    
    new_layer = arcpy.mapping.Layer(each)
    arcpy.mapping.AddLayer(dfTwo, new_layer, "BOTTOM")
mxd.save()
subprocess.Popen(["C:\\Program Files (x86)\\ArcGIS\\Desktop10.8\\bin\\ArcMap.exe",mxd_path])
