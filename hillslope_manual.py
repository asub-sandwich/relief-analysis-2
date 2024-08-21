import arcpy

class HillslopeManual:
    def __init__(self) -> None:
        self.label = "Hillslope Position (Manual)"
        self.description = "Calculate hillslope positions in a DEM given classified Slope, classified Profile Curvature, and classified Relative Elevation. Based on the algorithm proposed in (Miller & Schaetzl 2015), https://doi.org/10.2136/sssaj2014.07.0287"
        return None
    
    def getParameterInfo(self) -> list[arcpy.Parameter] :
        param0 = arcpy.Parameter(
            displayName="Slope Gradient (3 Classes)",
            name="slope",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
            displayName="Profile Curvature (2 Classes)",
            name="profc",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")
        param2 = arcpy.Parameter(
            displayName="Relative Elevation (2 Classes)",
            name="rel_elev",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")
        param3 = arcpy.Parameter(
            displayName="Output Raster",
            name="output",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output"
        )
        return [param0, param1, param2, param3]
    
    def isLicensed(self) -> bool:
        return True
    
    def execute(self, parameters, messages) -> None:
        slope = arcpy.Raster(parameters[0].valueAsText)
        profc = arcpy.Raster(parameters[1].valueAsText)
        relel = arcpy.Raster(parameters[2].valueAsText)
        out_ras = parameters[3].valueAsText

        out = arcpy.sa.Con(slope == 1, 3, 
                           arcpy.sa.Con(slope == 0,
                                        arcpy.sa.Con(profc == 1, 2, 4),
                                        arcpy.sa.Con(relel == 1, 1, 5)))
        out.save(out_ras)
        return None
        