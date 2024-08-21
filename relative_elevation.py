import arcpy

class RelativeElevation:
    def __init__(self) -> None:
        self.label = "Relative Elevation"
        self.description = "Calculates Relative Elevation of an input DEM"
        return None
    
    def isLicensed(self) -> bool:
        return True
    
    def getParameterInfo(self) -> list[arcpy.Parameter]:
        param0 = arcpy.Parameter(
            displayName="Input DEM",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
            displayName="Output Raster",
            name="out_ras",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
        param2 = arcpy.Parameter(
            displayName="Analysis Scale",
            name="scale",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        param2.value = 135
        return [param0, param1, param2]
    
    def execute(self, parameters, messages) -> None:
        dem = arcpy.Raster(parameters[0].valueAsText)
        out_ras = parameters[1].valueAsText
        scale = int(parameters[2].value)
        window = arcpy.sa.NbrRectangle(scale, scale, "MAP")
        max_focal = arcpy.sa.FocalStatistics(dem, window, "MAXIMUM", "")
        min_focal = arcpy.sa.FocalStatistics(dem, window, "MINIMUM", "")
        out = dem - ((min_focal + max_focal) - dem)
        out.save(out_ras)
        return None
    