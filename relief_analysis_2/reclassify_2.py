import arcpy

class Reclassify_2:
    def __init__(self) -> None:
        self.label = "Reclassify 2"
        self.description = "Reclassify a raster into 2 classes by specifying a break (Defaults to 0)"
        return None

    def getParameterInfo(self) -> list[arcpy.Parameter]:
        """Define the tool parameters."""
        param0 = arcpy.Parameter(
            displayName = "Input Raster",
            name = "in_ras",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param1 = arcpy.Parameter(
            displayName = "Output Raster",
            name = "out_ras",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Output")

        param2 = arcpy.Parameter(
            displayName = "Break",
            name = "br",
            datatype = "GPDouble",
            parameterType="Optional",
            direction="Input")

        param2.value = 0
        
        params = [param0, param1, param2]
        
        return params
            

    def isLicensed(self) -> bool:
        return True

    def execute(self, parameters, messages) -> None:
        in_ras = arcpy.Raster(parameters[0].valueAsText)
        out_ras = parameters[1].valueAsText
        br = parameters[2].value

        br = float(br)

        out = arcpy.sa.Con(in_ras >= br, 1, -1)
        out.save(out_ras)
    
        return None