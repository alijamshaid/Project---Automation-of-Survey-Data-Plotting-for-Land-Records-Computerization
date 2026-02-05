import geopandas as gpd
import pandas as pd
filePath = "G:/gis_python/Number/RabatNumber.shp"
outputPath = "G:/gis_python/Number/RabatNumber2.shp"
shapeFile = gpd.read_file(filePath)
print(shapeFile.columns)
shapeCentroid = shapeFile.centroid
shapeFile['center']=shapeCentroid.replace(" ",",")
shapeFile['latitude'] = shapeFile['center'].x
shapeFile['longitude'] = shapeFile['center'].y
sortedShapeFile = shapeFile.sort_values(by=["longitude"],ascending=[False])
sortedShapeFile["NumberRavaRabat"]=0
p=1
for lo,pa,i in zip(sortedShapeFile['longitude'],sortedShapeFile['Parcel_No'],sortedShapeFile.index):
    sortedShapeFile.loc[i,"NumberRavaRabat"]=p
    p=p+1

sortedShapeFile[["Parcel_No","NumberRavaRabat"]].to_csv("G:/gis_python/Number/RabatNumber.csv")


