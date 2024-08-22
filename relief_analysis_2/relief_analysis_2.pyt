# -*- coding: utf-8 -*-
from arcpy import Raster, Parameter, EnvManager
from arcpy.sa import Con, NbrRectangle, FocalStatistics
from arcpy.ddd import SurfaceParameters
from arcpy.env import workspace

import os
from glob import glob



# PLANNED: Using an acrpy clone with rasterio installed will allow the processing of tifs larger than of what can fit into memory. 
# Rasterio is also generally more stable than arcpy, so if error 999999 keeps biting you, try installing rasterio
is_rasterio = False
try:
    import rasterio
except:
    pass


class Toolbox:
    def __init__(self) -> None:
        self.label = "Relief Analysis 2.0"
        self.alias = "relief_analysis_2"

        self.tools = [HillslopeAutomatic, HillslopeManual, Reclassify_2, Reclassify_3, RelativeElevation]
        return None
    
class HillslopeAutomatic:
    def __init__(self) -> None:
        self.label = "Hillslope Position (Automatic)"
        self.description = "Calculates hillslope position from DEM"
        return None
    
    def getParameterInfo(self) -> list[Parameter]:
        param0 = Parameter(
            displayName = "Input DEM",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")
        param1 = Parameter(
            displayName="Output Raster",
            name="output",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
        return [param0, param1]
    
    def isLicensed(self) -> bool:
        return True
    
    def execute(self, parameters, messages) -> None:
        dem = Raster(parameters[0].valueAsText)

        # create scratch folder
        tmpdir = r"c:\tmp"
        if not os.path.isdir(tmpdir):
            os.mkdir(tmpdir, 0o0777)
        else:
            os.chmod(tmpdir, 0o0777)
        workspace = tmpdir

        # Calculate Slope
        with EnvManager(parallelProcessingFactor="75%"):
            SurfaceParameters(
                in_raster=dem,
                out_raster=os.path.join(tmpdir, r"slope.tif"),
                parameter_type="SLOPE",
                local_surface_type="QUADRATIC",
                neighborhood_distance="9 Meters",
                use_adaptive_neighborhood="FIXED_NEIGHBORHOOD",
                z_unit="Meter",
                output_slope_measurement="PERCENT_RISE",
                project_geodesic_azimuths="GEODESIC_AZIMUTHS",
                use_equatorial_aspect="NORTH_POLE_ASPECT",
                in_analysis_mask=None)
        
        # Reclassify Slope
        slope = Raster(os.path.join(tmpdir, r"slope.tif"))
        out_ras = os.path.join(tmpdir, r"slope_class.tif")
        lbr = 2.4
        ubr = 5.1
        out = Con(slope < lbr, -1, Con(slope > ubr, 1, 0))
        out.save(out_ras)

        # Calculate Profile Curvature
        with EnvManager(parallelProcessingFactor="75%"):
            SurfaceParameters(
                in_raster=dem,
                out_raster=os.path.join(tmpdir, r"profc.tif"),
                parameter_type="PROFILE_CURVATURE",
                local_surface_type="QUADRATIC",
                neighborhood_distance="63 Meters",
                use_adaptive_neighborhood="FIXED_NEIGHBORHOOD",
                z_unit="Meter",
                output_slope_measurement="PERCENT_RISE",
                project_geodesic_azimuths="GEODESIC_AZIMUTHS",
                use_equatorial_aspect="NORTH_POLE_ASPECT",
                in_analysis_mask=None)

        # Reclassify Profile Curvature
        profc = Raster(os.path.join(tmpdir, r"profc.tif"))
        out_ras = os.path.join(tmpdir, r"profc_class.tif")
        br = 0
        out = Con(profc >= br, 1, -1)
        out.save(out_ras)

        # Calculate Relative Elevation
        rel = RelativeElevation()
        rel_out = Parameter()
        rel_out.value = os.path.join(tmpdir, r"rel_elev.tif")
        scale = Parameter()
        scale.value = 135
        rel.execute([parameters[0], rel_out, scale], None)

        # Reclassify Relative Elevation
        relel = Raster(os.path.join(tmpdir, r"rel_elev.tif"))
        out_ras = os.path.join(tmpdir, r"rel_elev_class.tif")
        br = 0
        out = Con(relel >= br, 1, -1)
        out.save(out_ras)

        # Perform Hillslope Calculation
        dhp = HillslopeManual()
        slope = Parameter()
        slope.value = os.path.join(tmpdir, r"slope_class.tif")
        profc = Parameter()
        profc.value = os.path.join(tmpdir, r"profc_class.tif")
        relel = Parameter()
        relel.value = os.path.join(tmpdir, r"rel_elev_class.tif")
        dhp.execute([slope, profc, relel, parameters[1]], None)
            
        return None
    
    def postExecute(self, parameters) -> None:
        tmpdir = r"c:\tmp"
        files = ["slope*", "rel_elev*", "profc*"]
        for file in files:
            for f in glob("c:\\tmp\\" + file):
                os.remove(f)

        if len(os.listdir(tmpdir)) == 0:
            os.rmdir(tmpdir)
    
class Reclassify_2:
    def __init__(self) -> None:
        self.label = "Reclassify 2"
        self.description = "Reclassify a raster into 2 classes by specifying a break (Defaults to 0)"
        return None

    def getParameterInfo(self) -> list[Parameter]:
        """Define the tool parameters."""
        param0 = Parameter(
            displayName = "Input Raster",
            name = "in_ras",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")

        param1 = Parameter(
            displayName = "Output Raster",
            name = "out_ras",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Output")

        param2 = Parameter(
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
        in_ras = Raster(parameters[0].valueAsText)
        out_ras = parameters[1].valueAsText
        br = parameters[2].value

        br = float(br)

        out = Con(in_ras >= br, 1, -1)
        out.save(out_ras)
    
        return None

class Reclassify_3:
    def __init__(self) -> None:
        self.label = "Reclassify 3"
        self.description = "Reclassify a rasters into 3 classes by specifying 2 breaks"
        return None
    
    def getParameterInfo(self) -> list[Parameter]:
        param0 = Parameter(
            displayName = "Input Raster",
            name = "in_ras",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Input")
        param1 = Parameter(
            displayName = "Output Raster",
            name = "out_ras",
            datatype = "DERasterDataset",
            parameterType = "Required",
            direction = "Input")
        param2 = Parameter(
            displayName="Lower Break",
            name="lower_break",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        param3 = Parameter(
            displayName="Upper Break",
            name="upper_break",
            datatype="GPDouble",
            parameterType="Required",
            direction="Input")
        return [param0, param1, param2, param3]
    
    def isLicensed(self) -> bool:
        return True
    
    def execute(self, parameters, messages) -> None:
        if not is_rasterio:
            in_ras = Raster(parameters[0].valueAsText)
            out_ras = parameters[1].valueAsText
            lbr = parameters[2].value
            ubr = parameters[3].value

            lbr, ubr = float(lbr), float(ubr)

            out = Con(in_ras < lbr, -1, Con(in_ras > ubr, 1, 0))
            out.save(out_ras)

            return None

class HillslopeManual:
    def __init__(self) -> None:
        self.label = "Hillslope Position (Manual)"
        self.description = "Calculate hillslope positions in a DEM given classified Slope, classified Profile Curvature, and classified Relative Elevation. Based on the algorithm proposed in (Miller & Schaetzl 2015), https://doi.org/10.2136/sssaj2014.07.0287"
        return None
    
    def getParameterInfo(self) -> list[Parameter] :
        param0 = Parameter(
            displayName="Slope Gradient (3 Classes)",
            name="slope",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")
        param1 = Parameter(
            displayName="Profile Curvature (2 Classes)",
            name="profc",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")
        param2 = Parameter(
            displayName="Relative Elevation (2 Classes)",
            name="rel_elev",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")
        param3 = Parameter(
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
        if not is_rasterio:
            slope = Raster(parameters[0].valueAsText)
            profc = Raster(parameters[1].valueAsText)
            relel = Raster(parameters[2].valueAsText)
            out_ras = parameters[3].valueAsText

            out = Con(slope == 1, 3, 
                            Con(slope == 0,
                                            Con(profc == 1, 2, 4),
                                            Con(relel == 1, 1, 5)))
            out.save(out_ras)
            return None
        
class RelativeElevation:
    def __init__(self) -> None:
        self.label = "Relative Elevation"
        self.description = "Calculates Relative Elevation of an input DEM"
        return None
    
    def isLicensed(self) -> bool:
        return True
    
    def getParameterInfo(self) -> list[Parameter]:
        param0 = Parameter(
            displayName="Input DEM",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")
        param1 = Parameter(
            displayName="Output Raster",
            name="out_ras",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
        param2 = Parameter(
            displayName="Analysis Scale",
            name="scale",
            datatype="GPLong",
            parameterType="Optional",
            direction="Input")
        param2.value = 135
        return [param0, param1, param2]
    
    def execute(self, parameters, messages) -> None:
        dem = Raster(parameters[0].valueAsText)
        out_ras = parameters[1].valueAsText
        scale = int(parameters[2].value)
        window = NbrRectangle(scale, scale, "MAP")
        max_focal = FocalStatistics(dem, window, "MAXIMUM", "")
        min_focal = FocalStatistics(dem, window, "MINIMUM", "")
        out = dem - ((min_focal + max_focal) - dem)
        out.save(out_ras)
        return None
    
