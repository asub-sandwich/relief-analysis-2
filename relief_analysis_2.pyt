# -*- coding: utf-8 -*-

from reclassify_2 import Reclassify_2
from reclassify_3 import Reclassify_3
from relative_elevation import RelativeElevation
from hillslope_manual import HillslopeManual
from hillslope_automatic import HillslopeAutomatic


class Toolbox:
    def __init__(self) -> None:
        self.label = "Relief Analysis 2.0"
        self.alias = "relief_analysis_2"

        self.tools = [HillslopeAutomatic, HillslopeManual, Reclassify_2, Reclassify_3, RelativeElevation]
        return None



