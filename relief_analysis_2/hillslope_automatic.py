import arcpy
import os
from glob import glob
from relative_elevation import RelativeElevation
from hillslope_manual import HillslopeManual

class HillslopeAutomatic:
    def __init__(self) -> None:
        self.label = "Hillslope Position (Automatic)"
        self.description = "Calculates hillslope position from DEM"
        return None
    
    def getParameterInfo(self) -> list[arcpy.Parameter]:
        param0 = arcpy.Parameter(
            displayName = "Input DEM",
            name="dem",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
            displayName="Output Raster",
            name="output",
            datatype="DERasterDataset",
            parameterType="Required",
            direction="Output")
        return [param0, param1]
    
    def isLicensed(self) -> bool:
        return True
    
    def execute(self, parameters, messages) -> None:
        dem = arcpy.Raster(parameters[0].valueAsText)

        # create scratch folder
        tmpdir = r"c:\tmp"
        if not os.path.isdir(tmpdir):
            os.mkdir(tmpdir, 0o0777)
        else:
            os.chmod(tmpdir, 0o0777)
        arcpy.env.workspace = tmpdir

        # Calculate Slope
        with arcpy.EnvManager(parallelProcessingFactor="75%"):
            arcpy.ddd.SurfaceParameters(
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
        slope = arcpy.Raster(os.path.join(tmpdir, r"slope.tif"))
        out_ras = os.path.join(tmpdir, r"slope_class.tif")
        lbr = 2.4
        ubr = 5.1
        out = arcpy.sa.Con(slope < lbr, -1, arcpy.sa.Con(slope > ubr, 1, 0))
        out.save(out_ras)

        # Calculate Profile Curvature
        with arcpy.EnvManager(parallelProcessingFactor="75%"):
            arcpy.ddd.SurfaceParameters(
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
        profc = arcpy.Raster(os.path.join(tmpdir, r"profc.tif"))
        out_ras = os.path.join(tmpdir, r"profc_class.tif")
        br = 0
        out = arcpy.sa.Con(profc >= br, 1, -1)
        out.save(out_ras)

        # Calculate Relative Elevation
        rel = RelativeElevation()
        rel_out = arcpy.Parameter()
        rel_out.value = os.path.join(tmpdir, r"rel_elev.tif")
        scale = arcpy.Parameter()
        scale.value = 135
        rel.execute([parameters[0], rel_out, scale], None)

        # Reclassify Relative Elevation
        relel = arcpy.Raster(os.path.join(tmpdir, r"rel_elev.tif"))
        out_ras = os.path.join(tmpdir, r"rel_elev_class.tif")
        br = 0
        out = arcpy.sa.Con(relel >= br, 1, -1)
        out.save(out_ras)

        # Perform Hillslope Calculation
        dhp = HillslopeManual()
        slope = arcpy.Parameter()
        slope.value = os.path.join(tmpdir, r"slope_class.tif")
        profc = arcpy.Parameter()
        profc.value = os.path.join(tmpdir, r"profc_class.tif")
        relel = arcpy.Parameter()
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