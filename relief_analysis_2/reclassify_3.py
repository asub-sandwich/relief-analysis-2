import arcpy

class Reclassify_3:
    def __init__(self) -> None:
        self.label = "Reclassify 3"
        self.description = "Reclassify a rasters into 3 classes by specifying 2 breaks"
        return None
    
    def getParameterInfo(self) -> list[arcpy.Parameter]:
        param0 = arcpy.Parameter(
            displayName = "Input Raster",
            name = "in_ras",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Input")
        param1 = arcpy.Parameter(
            displayName = "Output Raster",
            name = "out_ras",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Input")
        param2 = arcpy.Parameter(
            displayName="Lower Break",
            name="lower_break",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param3 = arcpy.Parameter(
            displayName="Upper Break",
            name="upper_break",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        return [param0, param1, param2, param3]
    
    def isLicensed(self) -> bool:
        return True
    
    def execute(self, parameters, messages) -> None:
        in_ras = arcpy.Raster(parameters[0].valueAsText)
        out_ras = parameters[1].valueAsText
        lbr = parameters[2].value
        ubr = parameters[3].value

        lbr, ubr = float(lbr), float(ubr)

        out = arcpy.sa.Con(in_ras < lbr, -1, arcpy.sa.Con(in_ras > ubr, 1, 0))
        out.save(out_ras)

        return None