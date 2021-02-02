# standard libraries
import os
import sys
import datetime
import logging
import argparse
import math

# data manipilation libraries
import numpy as np
import pandas as pd

# graphing libraries
from plotly import tools
from plotly.offline import plot
import plotly.graph_objs as go
import plotly.io as pio


def CreateLogger(log_file):
    """ Zack's Generic Logger function to create onscreen and file logger

    Parameters
    ----------
    log_file: string
        `log_file` is the string of the absolute filepathname for writing the
        log file too which is a mirror of the onscreen display.

    Returns
    -------
    logger: logging object

    Notes
    -----
    This function is completely generic and can be used in any python code.
    The handler.setLevel can be adjusted from logging.INFO to any of the other
    options such as DEBUG, ERROR, WARNING in order to restrict what is logged.

    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    # create error file handler and set level to info
    handler = logging.FileHandler(log_file,  "w", encoding=None, delay="true")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def ReadInputs(ini_dict):
    """ Main Data Read-in from user *.csv files
    """
    input_folder = ini_dict.get("input_folder")
    input_dict = {"scenario": {},
                  "location": {},
                  "manage": {},
                  "soil": {},
                  "crop": {}}
    for k in list(input_dict.keys()):
        filename = "{}_inputs.csv".format(str(k))
        new_path = os.path.join(input_folder, filename)
        input_dict[k]["path"] = new_path
        if k == "scenario":
            temp_df = pd.read_csv(new_path, header=0)
        elif k == "location":
            temp_df = pd.read_csv(new_path, header=0,
                                  index_col=None, skipfooter=5)
        elif k == "soil":
            temp_df = pd.read_csv(new_path, header=0,
                                  index_col=None, skiprows=[32, 33])
        else:
            temp_df = pd.read_csv(new_path, header=0, index_col=None)
        input_dict[k]["df"] = temp_df
    return input_dict


class Crop:
    """ Main Crop Class for Simulation
    """
    def __init__(self, manage_df, crop_df, soil_df, location_df, weather_df,
                 scenario_name=None, LocRowNo=None, MangRowNo=None, SoilRowNo=None, CropRowNo=None,
                 location_name=None, manage_name=None, soil_name=None, crop_name=None,
                 weather_file=None, weather_first_row=None,
                 Pyear=None, yrno=None, water=None):
        # Dataframe Inputs Initialization
        self. manage_df = manage_df
        self.crop_df = crop_df
        self.soil_df = soil_df
        self.location_df = location_df
        self.weather_df = weather_df
        # Running Parameters Initialization
        self.LocRowNo = LocRowNo
        self.MangRowNo = MangRowNo
        self.SoilRowNo = SoilRowNo
        self.CropRowNo = CropRowNo
        self.scenario_name = scenario_name
        self.wthRow = weather_first_row
        self.location_name = location_name
        self.weather_file = weather_file
        self.manage_name = manage_name
        self.soil_name = soil_name
        self.crop_name = crop_name
        self.Pyear = Pyear
        self.yrno = yrno
        self.water = water

    def LocManagInputs(self):
        # initialize every new year
        self.MAT = 0
        self.iniPheno = 0
        self.iniLAI = 0
        self.iniDMP = 0
        self.iniSW = 0
        self.SNOW = 0
        # added Soltani 20210127
        self.NDS = 0
        self.DAS = 0
        self.DAP = 0
        self.CUMBNF = 0
        self.WSFL = 1
        self.WSFG = 1
        self.WSFN = 1
        self.WSFDS = 1
        self.WSXF = 1
        # added Soltani 20210127
        # Zack added
        self.WatDep = 0
        # assign value from df
        self.LAT = self.location_df.Latitute.iloc[0]
        self.VPDF = self.location_df.VPDF.iloc[0]
        self.tchng = self.location_df.tchng.iloc[0]
        self.pchng = self.location_df.pchng.iloc[0]
        self.CO2 = self.location_df.CO2.iloc[0]        
        self.FixFind = self.manage_df.FixFind.iloc[0]
        self.SimDoy = self.manage_df.SimDoy.iloc[0]
        self.Pdoy = self.manage_df.Fpdoy.iloc[0]
        if self.SimDoy == self.Pdoy: 
            self.SimDoy = self.Pdoy - 1
        self.SearchDur = self.manage_df.SearchDur.iloc[0]
        self.RfreeP = self.manage_df.RfreeP.iloc[0]
        # hardwired RfreeP
        self.RfreeP = 5
        self.SowTmp = self.manage_df.SowTmp.iloc[0]
        self.SowWat = self.manage_df.SowWat.iloc[0]        
        self.water = self.manage_df.water.iloc[0]
        self.IRGLVL = self.manage_df.IRGLVL.iloc[0]
        self.StopDoy = self.manage_df.StopDoy.iloc[0]
        self.ClipNo = self.manage_df.ClipNo.iloc[0]
        self.minWH = self.manage_df.mnWH.iloc[0]
        self.maxWH = self.manage_df.mxWH.iloc[0]
        return 0

    def FindSimSowDate(self):
        if self.SimDoy == 400:
            """ This appears to never fire as MAT is immediately 1
            Sheet10.Cells(scyrCntr + 1, 1).Formula = scnName
            Sheet10.Cells(scyrCntr + 1, 2).Formula = locName
            Sheet10.Cells(scyrCntr + 1, 3).Formula = mngName
            Sheet10.Cells(scyrCntr + 1, 4).Formula = solName
            Sheet10.Cells(scyrCntr + 1, 5).Formula = crpName
            Sheet10.Cells(scyrCntr + 1, 6) = Pyear
            Pdoy = "":     dtBSG = "":   dtTSG = "":    dtHAR = "": WTOP = "": WGRN = "": HI99 = "":
            ISOLWAT = "":  CRAIN = "":   CIRGW = "":    IRGNO = "": ATSW = "": CRUNOF = "": CE = "": CTR = "": WSTORG = ""
            ET99 = "":     EET99 = "":   SUMIPAR = "":  AVGFINT = "": RUE99 = "": WI99 = "": Ft99 = "": TE99 = "":
            MXXLAI = "":   Ysalt = "":   Ywet = "":     SRAINT = "":  MTMINT = "":  MTMAXT = "":  SSRADT = "":  SUMETT = "":
            SRAIN2 = "":   MTMIN2 = "":  MTMAX2 = "":   SSRAD2 = "": SUMET2 = "": SRAIN3 = "": MTMIN3 = "":
            MTMAX3 = "":   SSRAD3 = "":  SUMET3 = "":
            MAT = 1
            """
            return
        if self.FixFind == 91:
            self.SimDoy = 1
            self.Pdoy = 2
        # this finds start simulation date
        # weather file is used to find weather data selection
        # using Yr = Pyear (Fyear) and DOY = SimDoy
        while True:
            self.Yr = self.weather_df.Year.iloc[self.wthRow]
            self.DOY = self.weather_df.DOY.iloc[self.wthRow]
            self.SRAD = self.weather_df.SRAD.iloc[self.wthRow]
            self.TMAX = self.weather_df.TMAX.iloc[self.wthRow]
            self.TMIN = self.weather_df.TMIN.iloc[self.wthRow]
            self.RAIN = self.weather_df.RAIN.iloc[self.wthRow]
            self.wthRow += 1
            if self.Yr == self.Pyear and self.DOY == self.SimDoy:
                break     
        # this finds sowing date (FixFind=0)
        # or first date in the sowing window
        while True:
            self.Yr = self.weather_df.Year.iloc[self.wthRow]
            self.DOY = self.weather_df.DOY.iloc[self.wthRow]
            self.SRAD = self.weather_df.SRAD.iloc[self.wthRow]
            self.TMAX = self.weather_df.TMAX.iloc[self.wthRow]
            self.TMIN = self.weather_df.TMIN.iloc[self.wthRow]
            self.RAIN = self.weather_df.RAIN.iloc[self.wthRow]
            self.wthRow += 1
            self.TMIN = self.TMIN + self.tchng
            self.TMAX = self.TMAX + self.tchng
            self.RAIN = self.RAIN * self.pchng
            self.TMP = (self.TMAX + self.TMIN) / 2
            if self.water == 1 or self.water == 2 or self.water == 3:
                self.SoilWater()
            self.NDS = 0
            self.DTU = 0
            self.DAP = 0 # added Soltani 20210127
            if self.Yr == self.Pyear and self.DOY == self.Pdoy:
                break
        # Loop Until Yr = Pyear And DOY = Pdoy
        if self.FixFind == 0:
            pass
        elif self.FixFind == 1:
            # Sow in the 5-th day of a 5-day rainfree period
            self.R1 = 99
            self.R2 = 99
            self.R3 = 99
            self.R4 = 99
            self.R5 = 99
            self.Nfixfind = 0
            self.SUMRAIN = 99
            self.CumFind = 0
            while True:
                self.Yr = self.weather_df.Year.iloc[self.wthRow]
                self.DOY = self.weather_df.DOY.iloc[self.wthRow]
                self.SRAD = self.weather_df.SRAD.iloc[self.wthRow]
                self.TMAX = self.weather_df.TMAX.iloc[self.wthRow]
                self.TMIN = self.weather_df.TMIN.iloc[self.wthRow]
                self.RAIN = self.weather_df.RAIN.iloc[self.wthRow]
                self.wthRow += 1
                self.TMIN = self.TMIN + self.tchng
                self.TMAX = self.TMAX + self.tchng
                self.RAIN = self.RAIN * self.pchng
                self.TMP = (self.TMAX + self.TMIN) / 2
                self.R5 = self.R4
                self.R4 = self.R3
                self.R3 = self.R2
                self.R2 = self.R1
                self.R1 = self.RAIN
                self.SUMRAIN = self.R1 + self.R2 + self.R3 + self.R4 + self.R5
                self.Nfixfind += 1            
                if self.water == 1 or self.water == 2 or self.water == 3:
                    self.SoilWater()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 7
                if self.SUMRAIN == 0 and self.Nfixfind >= self.RfreeP:
                    break
                if self.MAT == 1:
                    break
            self.Pdoy = self.DOY    
        elif self.FixFind == 2:
            # Sow in the 5th day of a 5-day rainfree period + temp> x oC
            self.T1 = 0
            self.T2 = 0
            self.T3 = 0
            self.T4 = 0
            self.T5 = 0
            self.R1 = 99
            self.R2 = 99
            self.R3 = 99
            self.R4 = 99
            self.R5 = 99
            self.Nfixfind = 0
            self.SUMRAIN = 99
            self.CumFind = 0
            while True:
                self.Yr = self.weather_df.Year.iloc[self.wthRow]
                self.DOY = self.weather_df.DOY.iloc[self.wthRow]
                self.SRAD = self.weather_df.SRAD.iloc[self.wthRow]
                self.TMAX = self.weather_df.TMAX.iloc[self.wthRow]
                self.TMIN = self.weather_df.TMIN.iloc[self.wthRow]
                self.RAIN = self.weather_df.RAIN.iloc[self.wthRow]
                self.wthRow += 1
                self.TMIN = self.TMIN + self.tchng
                self.TMAX = self.TMAX + self.tchng
                self.RAIN = self.RAIN * self.pchng
                self.TMP = (self.TMAX + self.TMIN) / 2
                self.T5 = self.T4
                self.R5 = self.R4
                self.T4 = self.T3
                self.R4 = self.R3
                self.T3 = self.T2
                self.R3 = self.R2
                self.T2 = self.T1
                self.R2 = self.R1
                self.T1 = self.TMP
                self.R1 = self.RAIN
                self.MVMTMP = (self.T1 + self.T2 + self.T3 + self.T4 + self.T5) / 5
                self.SUMRAIN = self.R1 + self.R2 + self.R3 + self.R4 + self.R5
                self.Nfixfind += 1
                if self.water == 1 or self.water == 2 or self.water == 3:
                    self.SoilWater()                    
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 7
                if self.MVMTMP > self.SowTmp and self.SUMRAIN==0 and self.Nfixfind >= self.RfreeP:
                    break
                if self.MAT == 1:
                    break             
            self.Pdoy = self.DOY
        elif self.FixFind == 3:
        # Sow in the 5th day of a 5-day rainfree period + temp< x oC
            self.T1 = 0
            self.T2 = 0
            self.T3 = 0
            self.T4 = 0
            self.T5 = 0
            self.R1 = 99
            self.R2 = 99
            self.R3 = 99
            self.R4 = 99
            self.R5 = 99
            self.Nfixfind = 0
            self.SUMRAIN = 99
            self.CumFind = 0
            while True:
                self.Yr = self.weather_df.Year.iloc[self.wthRow]
                self.DOY = self.weather_df.DOY.iloc[self.wthRow]
                self.SRAD = self.weather_df.SRAD.iloc[self.wthRow]
                self.TMAX = self.weather_df.TMAX.iloc[self.wthRow]
                self.TMIN = self.weather_df.TMIN.iloc[self.wthRow]
                self.RAIN = self.weather_df.RAIN.iloc[self.wthRow]
                self.wthRow += 1
                self.TMIN = self.TMIN + self.tchng
                self.TMAX = self.TMAX + self.tchng
                self.RAIN = self.RAIN * self.pchng
                self.TMP = (self.TMAX + self.TMIN) / 2
                self.T5 = self.T4
                self.R5 = self.R4
                self.T4 = self.T3
                self.R4 = self.R3
                self.T3 = self.T2
                self.R3 = self.R2
                self.T2 = self.T1
                self.R2 = self.R1
                self.T1 = self.TMP
                self.R1 = self.RAIN
                self.MVMTMP = (self.T1 + self.T2 + self.T3 + self.T4 + self.T5) / 5
                self.SUMRAIN = self.R1 + self.R2 + self.R3 + self.R4 + self.R5
                self.Nfixfind += 1    
                if self.water == 1 or self.water == 2 or self.water == 3:
                    self.SoilWater()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 7
                if self.MVMTMP < self.SowTmp and self.SUMRAIN==0 and self.Nfixfind >= self.RfreeP:
                    break
                if self.MAT == 1:
                    break             
            self.Pdoy = self.DOY
        elif self.FixFind == 4:
        # Sow when top-layer FTSW1 => SowWat; soilWater should be 'ON'
            self.CumFind = 0
            while True:
                self.Yr = self.weather_df.Year.iloc[self.wthRow]
                self.DOY = self.weather_df.DOY.iloc[self.wthRow]
                self.SRAD = self.weather_df.SRAD.iloc[self.wthRow]
                self.TMAX = self.weather_df.TMAX.iloc[self.wthRow]
                self.TMIN = self.weather_df.TMIN.iloc[self.wthRow]
                self.RAIN = self.weather_df.RAIN.iloc[self.wthRow]
                self.wthRow += 1
                self.TMIN = self.TMIN + self.tchng
                self.TMAX = self.TMAX + self.tchng
                self.RAIN = self.RAIN * self.pchng
                self.TMP = (self.TMAX + self.TMIN) / 2
                if self.water == 1 or self.water == 2 or self.water == 3:
                    self.SoilWater()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 7
                if self.FTSW1 >= self.SowWat or self.MAT == 1:
                    break
            self.Pdoy = self.DOY        
        elif self.FixFind == 5:
        # Sow when top-layer FTSW1 <= SowWat; soilWater should be 'ON'
            self.CumFind = 0
            while True:
                self.Yr = self.weather_df.Year.iloc[self.wthRow]
                self.DOY = self.weather_df.DOY.iloc[self.wthRow]
                self.SRAD = self.weather_df.SRAD.iloc[self.wthRow]
                self.TMAX = self.weather_df.TMAX.iloc[self.wthRow]
                self.TMIN = self.weather_df.TMIN.iloc[self.wthRow]
                self.RAIN = self.weather_df.RAIN.iloc[self.wthRow]
                self.wthRow += 1
                self.TMIN = self.TMIN + self.tchng
                self.TMAX = self.TMAX + self.tchng
                self.RAIN = self.RAIN * self.pchng
                self.TMP = (self.TMAX + self.TMIN) / 2
                if self.water == 1 or self.water == 2 or self.water == 3:
                    self.SoilWater()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 7
                if self.FTSW1 <= self.SowWat or self.MAT == 1:
                    break
            self.Pdoy = self.DOY        
        elif self.FixFind == 6:
        # Sow when cum rain > SowWat over a 5-day period
            self.T1 = 0
            self.T2 = 0
            self.T3 = 0
            self.T4 = 0
            self.T5 = 0
            self.R1 = 99
            self.R2 = 99
            self.R3 = 99
            self.R4 = 99
            self.R5 = 99
            self.Nfixfind = 0
            self.SUMRAIN = 99
            self.CumFind = 0
            while True:
                self.Yr = self.weather_df.Year.iloc[self.wthRow]
                self.DOY = self.weather_df.DOY.iloc[self.wthRow]
                self.SRAD = self.weather_df.SRAD.iloc[self.wthRow]
                self.TMAX = self.weather_df.TMAX.iloc[self.wthRow]
                self.TMIN = self.weather_df.TMIN.iloc[self.wthRow]
                self.RAIN = self.weather_df.RAIN.iloc[self.wthRow]
                self.wthRow += 1
                self.TMIN = self.TMIN + self.tchng
                self.TMAX = self.TMAX + self.tchng
                self.RAIN = self.RAIN * self.pchng
                self.TMP = (self.TMAX + self.TMIN) / 2
                self.T5 = self.T4
                self.R5 = self.R4
                self.T4 = self.T3
                self.R4 = self.R3
                self.T3 = self.T2
                self.R3 = self.R2
                self.T2 = self.T1
                self.R2 = self.R1
                self.T1 = self.TMP
                self.R1 = self.RAIN
                self.MVMTMP = (self.T1 + self.T2 + self.T3 + self.T4 + self.T5) / 5
                self.SUMRAIN = self.R1 + self.R2 + self.R3 + self.R4 + self.R5
                self.Nfixfind += 1
                if self.water == 1 or self.water == 2 or self.water == 3:
                    self.SoilWater()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 7
                if self.SUMRAIN >= self.SowWat and self.Nfixfind >= self.RfreeP:
                    break
                if self.MAT == 1:
                    break
            self.Pdoy = self.DOY     
        elif self.FixFind == 7:
        # Sow when cum rain > SowWat over a 5-day period plus avg temp < SowTmp
            self.T1 = 0
            self.T2 = 0
            self.T3 = 0
            self.T4 = 0
            self.T5 = 0
            self.R1 = 99
            self.R2 = 99
            self.R3 = 99
            self.R4 = 99
            self.R5 = 99
            self.Nfixfind = 0
            self.SUMRAIN = 99
            self.CumFind = 0
            while True:
                self.Yr = self.weather_df.Year.iloc[self.wthRow]
                self.DOY = self.weather_df.DOY.iloc[self.wthRow]
                self.SRAD = self.weather_df.SRAD.iloc[self.wthRow]
                self.TMAX = self.weather_df.TMAX.iloc[self.wthRow]
                self.TMIN = self.weather_df.TMIN.iloc[self.wthRow]
                self.RAIN = self.weather_df.RAIN.iloc[self.wthRow]
                self.wthRow += 1
                self.TMIN = self.TMIN + self.tchng
                self.TMAX = self.TMAX + self.tchng
                self.RAIN = self.RAIN * self.pchng
                self.TMP = (self.TMAX + self.TMIN) / 2
                self.T5 = self.T4
                self.R5 = self.R4
                self.T4 = self.T3
                self.R4 = self.R3
                self.T3 = self.T2
                self.R3 = self.R2
                self.T2 = self.T1
                self.R2 = self.R1
                self.T1 = self.TMP
                self.R1 = self.RAIN
                self.MVMTMP = (self.T1 + self.T2 + self.T3 + self.T4 + self.T5) / 5
                self.SUMRAIN = self.R1 + self.R2 + self.R3 + self.R4 + self.R5
                self.Nfixfind += 1
                if self.water == 1 or self.water == 2 or self.water == 3:
                    self.SoilWater()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 7
                if self.SUMRAIN >= self.SowWat and self.MVMTMP < self.SowTmp and self.Nfixfind >= self.RfreeP:
                    break
                if self.MAT == 1:
                    break
            self.Pdoy = self.DOY
        elif self.FixFind == 91:
        # Finding bud burst based on TU accumulation from 1st Jan.
            self.SForc = 0
            self.ForcTB = self.crop_df.TBD.iloc[0]
            self.ForcReq = self.crop_df.ForceReq.iloc[0]
            while True:
                self.Yr = self.weather_df.Year.iloc[self.wthRow]
                self.DOY = self.weather_df.DOY.iloc[self.wthRow]
                self.SRAD = self.weather_df.SRAD.iloc[self.wthRow]
                self.TMAX = self.weather_df.TMAX.iloc[self.wthRow]
                self.TMIN = self.weather_df.TMIN.iloc[self.wthRow]
                self.RAIN = self.weather_df.RAIN.iloc[self.wthRow]
                self.wthRow += 1
                self.TMIN = self.TMIN + self.tchng
                self.TMAX = self.TMAX + self.tchng
                self.RAIN = self.RAIN * self.pchng
                self.TMP = (self.TMAX + self.TMIN) / 2      
                self.DForc = self.TMP - self.ForcTB
                if self.DForc < 0:
                    self.DForc = 0
                self.SForc = self.SForc + self.DForc
                if self.water == 1 or self.water == 2 or self.water == 3:
                    self.SoilWater()
                if self.SForc >= self.ForcReq:
                    break
            self.Pdoy = self.DOY
        if self.MAT == 1:
            return 1
        return 0

    def Weather(self):
        self.Yr = self.weather_df.Year.iloc[self.wthRow]
        self.DOY = self.weather_df.DOY.iloc[self.wthRow]
        self.SRAD = self.weather_df.SRAD.iloc[self.wthRow]
        self.TMAX = self.weather_df.TMAX.iloc[self.wthRow]
        self.TMIN = self.weather_df.TMIN.iloc[self.wthRow]
        self.RAIN = self.weather_df.RAIN.iloc[self.wthRow]
        self.TMIN += self.tchng
        self.TMAX += self.tchng
        self.RAIN *= self.pchng
        self.TMP = (self.TMAX + self.TMIN) / 2
        self.SNOMLT = 0
        if self.TMAX <= 1:
            self.SNOW = self.SNOW + self.RAIN
            self.RAIN = 0
        elif self.TMAX > 1 and self.SNOW > 0:
            self.SNOMLT = self.TMAX + self.RAIN * 0.4
            if self.SNOMLT > self.SNOW:
                self.SNOMLT = self.SNOW
            self.SNOW = self.SNOW - self.SNOMLT
            self.RAIN = self.RAIN + self.SNOMLT
        self.wthRow += 1

    def PhenologyBD(self):
        if self.iniPheno == 0:
            self.TBD = self.crop_df.TBD.iloc[0]
            self.TP1D = self.crop_df.TP1D.iloc[0]
            self.TP2D = self.crop_df.TP2D.iloc[0]
            self.TCD = self.crop_df.TCD.iloc[0]
            self.tuHAR = self.crop_df.tuHAR.iloc[0]
            self.frEMR = self.crop_df.frEMR.iloc[0]
            self.frBSG = self.crop_df.frBSG.iloc[0]
            self.frTSG = self.crop_df.frTSG.iloc[0]
            self.frPM = self.crop_df.frPM.iloc[0]
            self.frBLS = self.crop_df.frBLS.iloc[0]
            self.DAP = 0
            self.NDS = 0
            self.CTU = 0
            self.WSFDS = 1
            self.DAYT = 0
            self.SRAINT = 0
            self.STMINT = 0
            self.STMAXT = 0
            self.SSRADT = 0
            self.SUMETT = 0
            self.DAY3 = 0
            self.SRAIN3 = 0
            self.STMIN3 = 0
            self.STMAX3 = 0
            self.SSRAD3 = 0
            self.SUMET3 = 0
            self.DAY2 = 0
            self.SRAIN2 = 0
            self.STMIN2 = 0
            self.STMAX2 = 0
            self.SSRAD2 = 0
            self.SUMET2 = 0    
            self.iniPheno = 1
        # Temperature unit calculation
        if self.TMP <= self.TBD or self.TMP >= self.TCD:
            self.tempfun = 0
        elif self.TMP > self.TBD and self.TMP < self.TP1D:
            self.tempfun = (self.TMP - self.TBD) / (self.TP1D - self.TBD)
        elif self.TMP > self.TP2D and self.TMP < self.TCD:
            self.tempfun = (self.TCD - self.TMP) / (self.TCD - self.TP2D)
        elif self.TMP >= self.TP1D and self.TMP <= self.TP2D:
            self.tempfun = 1
        else:
            logging.error('Crop: {} failed temperature process'
                            .format(self.crop_name))
        self.DTU = (self.TP1D - self.TBD) * self.tempfun
        if self.NDS > self.frEMR:
            self.DTU = self.DTU * self.WSFDS
        self.CTU = self.CTU + self.DTU
        self.NDS = self.CTU / self.tuHAR
        self.DAP = self.DAP + 1
        if self.NDS < self.frBSG:
            self.dtBSG = self.DAP + 1
        if self.NDS < self.frTSG:
            self.dtTSG = self.DAP + 1
        if self.NDS < 1:
            self.dtHAR = self.DAP + 1
        if self.NDS >= 1:
            self.MAT = 1
        if self.DOY == self.StopDoy:
            self.MAT = 1
        if self.NDS <= 1: # sowing to MAT
            self.DAYT = self.DAYT + 1
            self.SRAINT = self.SRAINT + self.RAIN
            self.STMINT = self.STMINT + self.TMIN
            self.STMAXT = self.STMAXT + self.TMAX
            self.SSRADT = self.SSRADT + self.SRAD
            self.SUMETT = self.SUMETT + self.SEVP + self.TR
            self.MTMINT = self.STMINT / self.DAYT
            self.MTMAXT = self.STMAXT / self.DAYT
        if self.NDS <= self.frBSG:  # sowing to BSG
            self.DAY2 = self.DAY2 + 1
            self.SRAIN2 = self.SRAIN2 + self.RAIN
            self.STMIN2 = self.STMIN2 + self.TMIN
            self.STMAX2 = self.STMAX2 + self.TMAX
            self.SSRAD2 = self.SSRAD2 + self.SRAD
            self.SUMET2 = self.SUMET2 + self.SEVP + self.TR
            self.MTMIN2 = self.STMIN2 / self.DAY2
            self.MTMAX2 = self.STMAX2 / self.DAY2
        if self.NDS > self.frBSG and self.NDS <= 1: # BSG to MAT
            self.DAY3 = self.DAY3 + 1
            self.SRAIN3 = self.SRAIN3 + self.RAIN
            self.STMIN3 = self.STMIN3 + self.TMIN
            self.STMAX3 = self.STMAX3 + self.TMAX
            self.SSRAD3 = self.SSRAD3 + self.SRAD
            self.SUMET3 = self.SUMET3 + self.SEVP + self.TR
            self.MTMIN3 = self.STMIN3 / self.DAY3
            self.MTMAX3 = self.STMAX3 / self.DAY3
        return 0

    def CropLAI(self):
        # Crop LAI No N
        # LAI initials and pars
        if self.iniLAI == 0:
            self.x1NDS = self.crop_df['x1'].iloc[0]
            self.y1LAI = self.crop_df['y1'].iloc[0]
            self.x2NDS = self.crop_df['x2'].iloc[0]
            self.y2LAI = self.crop_df['y2'].iloc[0]
            self.LAIMX = self.crop_df.LAIMX.iloc[0]
            self.SRATE = self.crop_df.SRATE.iloc[0]
            self.FrzTh = self.crop_df.FrzTh.iloc[0]
            self.FrzLDR = self.crop_df.FrzLDR.iloc[0]
            self.HeatTh = self.crop_df.HeatTH.iloc[0]
            self.HtLDR = self.crop_df.HtLDR.iloc[0]
            self.PART1 = np.log((1 / self.y1LAI - 1) / (1 / self.x1NDS))
            self.PART2 = np.log((1 / self.y2LAI - 1) / (1 / self.x2NDS))
            self.BL = (self.PART2 - self.PART1) / (self.x1NDS - self.x2NDS)
            self.AL = self.PART1 + self.BL * self.x1NDS
            self.LAI1 = 0
            self.LAI2 = 0
            self.LAI = 0
            self.BLSLAI = 0 # added Soltani 20210127
            self.MXXLAI = 0
            self.iniLAI = 1 
        self.GLAI = 0
        self.DLAI = 0
        if self.NDS >= self.frEMR and self.NDS < self.frBLS:
            self.LAI2 = self.NDS / (self.NDS + math.exp(self.AL - self.BL * self.NDS)) * self.LAIMX
            self.GLAI = (self.LAI2 - self.LAI1) * self.WSFL
            self.LAI1 = self.LAI2
            self.BLSLAI = self.LAI # Saving the value of LAI at BLS
        elif self.NDS >= self.frBLS:
        # LAI2 = BLSLAI * ((1.000001 - NDS) / (1 - frBLS)) ^ SRATE
        # DLAI = (LAI1 - LAI2) * WSFDS
        # LAI1 = LAI2
            self.LAI2 = self.BLSLAI * ((1.000001 - self.NDS) / (1 - self.frBLS)) ** self.SRATE
            self.DLAI = (self.LAI - self.LAI2) * self.WSFDS
        # Frost & Heat
        self.DLAIF = 0
        if self.NDS > self.frEMR and self.TMIN < self.FrzTh:
            self.frstf = abs(self.TMIN - self.FrzTh) * self.FrzLDR
            if self.frstf < 0:
                self.frstf = 0
            if self.frstf > 1:
                self.frstf = 1
            self.DLAIF = self.LAI * self.frstf
        if self.DLAI < self.DLAIF:
            self.DLAI = self.DLAIF
        self.DLAIH = self.DLAI
        if self.NDS > self.frEMR and self.TMAX > self.HeatTh:
        # heatf = 4 - (1 - (TMAX - 34) / 2)   Asseng-APSIM
        # If DLAI = 0 Then DLAI = DTU * 0.0002
            self.heatf = 1 + (self.TMAX - self.HeatTh) * self.HtLDR # Semenov-Sirius
            if self.heatf < 1:
                self.heatf = 1
            self.DLAIH = self.DLAI * self.heatf
        if self.DLAI < self.DLAIH:
            self.DLAI = self.DLAIH
        self.LAI = self.LAI + self.GLAI - self.DLAI
        if self.LAI < 0:
            self.LAI = 0
        if self.LAI > self.MXXLAI:
            self.MXXLAI = self.LAI # Saving the value of actual maximum LAI
        return 0

    def DMProduction(self):
        # Parameters and Initials
        if self.iniDMP == 0:
            self.TBRUE = self.crop_df.TBRUE.iloc[0]
            self.TP1RUE = self.crop_df.TP1RUE.iloc[0]
            self.TP2RUE = self.crop_df.TP2RUE.iloc[0]
            self.TCRUE = self.crop_df.TCRUE.iloc[0]
            self.KPAR = self.crop_df.KPAR.iloc[0]
            self.IRUE = self.crop_df.IRUE.iloc[0]
            self.HIMAX = self.crop_df.HImax.iloc[0]
            self.HIMIN = self.crop_df.FRTRL.iloc[0]
            self.PDHI = self.HIMAX / (self.tuHAR * (self.frTSG - self.frBSG))  # per oC
            self.GCC = self.crop_df.GCC.iloc[0]
            self.c3c4 = self.crop_df['C3/C4'].iloc[0]
            self.RUE385 = 1 * (1 + self.c3c4 * (np.log10(385/330)))
            self.RUECO2 = 1 * (1 + self.c3c4 * (np.log10(self.CO2 / 330)))
            self.CO2RUE = self.RUECO2 / self.RUE385
            self.IRUE = self.IRUE * self.CO2RUE
            self.SUMFINT = 0
            self.SUMIPAR = 0
            self.WVEG = 1
            self.WGRN = 0
            self.WTOP = self.WVEG + self.WGRN
            self.WSFG = 1
            self.ClipCount = 0
            self.TRLDM = 0 # added Soltani 20210128
            self.iniDMP = 1    
        # Adjustment of RUE
        if self.TMP <= self.TBRUE or self.TMP >= self.TCRUE:
            self.TCFRUE = 0
        elif self.TMP > self.TBRUE and self.TMP < self.TP1RUE:
            self.TCFRUE = (self.TMP - self.TBRUE) / (self.TP1RUE - self.TBRUE)
        elif self.TMP > self.TP2RUE and self.TMP < self.TCRUE:
            self.TCFRUE = (self.TCRUE - self.TMP) / (self.TCRUE - self.TP2RUE)
        elif self.TMP >= self.TP1RUE and self.TMP <= self.TP2RUE:
            self.TCFRUE = 1
        self.RUE = self.IRUE * self.TCFRUE * self.WSFG
        if self.NDS < self.frEMR or self.NDS > self.frPM:
            self.RUE = 0
        self.FINT = 1 - math.exp(-self.KPAR * self.LAI)
        self.DDMP = self.SRAD * 0.48 * self.FINT * self.RUE
        self.HI = self.WGRN / self.WTOP
        self.TRANSL = 0
        self.SGR = 0
        if self.NDS < self.frBSG:
            self.BSGDM = self.WTOP # Saving WTOP at BSG
            self.TRLDM = self.BSGDM * self.HIMIN
        elif self.NDS >= self.frBSG and self.NDS <= self.frTSG:
            self.DHI = self.PDHI * self.DTU # from mm per oC to mm per day
            self.SGR = self.DHI * (self.WTOP + self.DDMP) + self.DDMP * self.HI
            if self.HI >= self.HIMAX:
                self.SGR = 0
            if (self.SGR / self.GCC) > self.DDMP:
                self.TRANSL = (self.SGR / self.GCC) - self.DDMP
                if self.TRANSL > self.TRLDM:
                    self.TRANSL = self.TRLDM
            elif (self.SGR / self.GCC) <= self.DDMP:
                self.TRANSL = 0
            self.TRLDM = self.TRLDM - self.TRANSL
            if self.SGR > ((self.DDMP + self.TRANSL) * self.GCC):
                self.SGR = (self.DDMP + self.TRANSL) * self.GCC
        self.WGRN = self.WGRN + self.SGR
        self.WVEG = self.WVEG + self.DDMP - (self.SGR / self.GCC)
        self.WTOP = self.WVEG + self.WGRN
        self.SUMFINT = self.SUMFINT + self.FINT
        self.AVGFINT = self.SUMFINT / self.DAP
        self.SUMIPAR = self.SUMIPAR + self.SRAD * 0.48
        # Clipping forages
        if self.ClipNo > 0 and self.DOY != self.StopDoy:
            if self.MAT == 1:
                self.ClipCount += 1
                if self.ClipCount < self.ClipNo:
                    self.MAT = 0
                    self.NDS = 0
                    self.CTU = 0
                    self.LAI1 = 0
                    self.LAI2 = 0
                    self.LAI = 0
        return 0

    def SoilWater(self):
        # Parameters and Initials
        if self.iniSW == 0:
            self.DEPORT = self.crop_df.iDEPORT.iloc[0]
            self.frBRG = self.crop_df.frBRG.iloc[0]
            self.frTRG = self.crop_df.frTRG.iloc[0]
            self.MEED = self.crop_df.MEED.iloc[0]
            self.TECREF = self.crop_df.TEC.iloc[0]
            self.WSSG = self.crop_df.WSSG.iloc[0]
            self.WSSL = self.crop_df.WSSL.iloc[0]
            self.WSSD = self.crop_df.WSSD.iloc[0]
            self.tuHAR = self.crop_df.tuHAR.iloc[0]
            self.GRTDP = (self.MEED - self.DEPORT) / ((self.frTRG - self.frBRG) * self.tuHAR) # mm per oC
            self.c3c4 = self.crop_df['C3/C4'].iloc[0]
            self.RUE385 = 1 * (1 + self.c3c4 * (np.log10(385 / 330)))
            self.RUECO2 = 1 * (1 + self.c3c4 * (np.log10(self.CO2 / 330)))
            self.CO2RUE = self.RUECO2 / self.RUE385
            self.CO2TEC = self.CO2RUE
            self.TEC = self.TECREF * self.CO2TEC
            self.SOLDEP = self.soil_df.SOLDEP.iloc[0]
            self.DEP1 = self.soil_df.DEP1.iloc[0]
            self.SALB = self.soil_df.SALB.iloc[0]
            self.CN2 = self.soil_df.CN.iloc[0]
            self.DRAINF = self.soil_df.DRAINF.iloc[0]
            self.SAT = self.soil_df.SAT.iloc[0]
            self.DUL = self.soil_df.DUL.iloc[0]
            self.EXTR = self.soil_df.EXTR.iloc[0]
            self.CLL = self.DUL - self.EXTR
            self.SDRAINF = self.soil_df.SDRAINF.iloc[0]
            self.Slope = self.soil_df.SLOPE.iloc[0]                
            self.MAI1 = self.manage_df.MAI1.iloc[0]
            self.MAI = self.manage_df.MAI.iloc[0]
            # changed IPATSW to ISOLWAT 20210202
            self.ISOLWAT = self.SOLDEP * self.EXTR * self.MAI
            self.ATSW = self.DEPORT * self.EXTR * self.MAI
            self.TTSW = self.DEPORT * self.EXTR
            self.FTSW = self.ATSW / self.TTSW
            # changed IPATSW to ISOLWAT 20210202
            self.WSTORG = self.ISOLWAT - self.ATSW
            self.ATSW1 = self.DEP1 * self.EXTR * self.MAI1
            self.TTSW1 = self.DEP1 * self.EXTR
            self.FTSW1 = self.ATSW1 / self.TTSW1
            self.WLL1 = self.DEP1 * self.CLL
            self.WAT1 = self.WLL1 + self.ATSW1
            self.WSAT1 = self.DEP1 * self.SAT
            self.HYDDEP = 600
            if self.HYDDEP > self.SOLDEP:
                self.HYDDEP = self.SOLDEP
            self.ATSW60 = self.HYDDEP * self.EXTR * self.MAI
            self.TTSW60 = self.HYDDEP * self.EXTR
            self.WLL60 = self.HYDDEP * self.CLL
            self.WSAT60 = self.HYDDEP * self.SAT
            self.WAT60 = self.WLL60 + self.ATSW60
            self.EOSMIN = 1.5
            self.WETWAT = 10
            self.KET = 0.5
            self.CALB = 0.23
            self.LAI = 0
            self.BLSLAI = 0
            # added Soltani 20210127
            self.DTU = 0
            self.NDS = 0
            self.DDMP = 0
            self.IRGW = 0
            # added Soltani 20210127
            if self.DEPORT > 800:
                self.ETLAIMN = 1
            else:
                self.ETLAIMN = 0
            self.DYSE = 1
            self.CTR = 0
            self.CE = 0
            self.CRAIN = 0
            self.CRUNOF = 0
            self.CIRGW = 0
            # added Soltani 20210128
            self.frBLS = 0
            self.EWAT = 0
            # added Soltani 20210128
            self.IRGNO = 0
            self.DTU = 0
            self.iniSW = 1
        # Balance at DAP=1
        if self.DAP == 1:
            self.ISOLWAT = self.ATSW + self.WSTORG
            self.CTR0 = self.CTR
            self.CTR = 0
            self.CE0 = self.CE
            self.CE = 0
            self.CRAIN0 = self.CRAIN
            self.CRAIN = 0
            self.CRUNOF0 = self.CRUNOF
            self.CRUNOF = 0
    
        # LAI for soil evaporation
        if self.NDS <= self.frBLS:
            self.ETLAI = self.LAI
        else:
            self.ETLAI = self.BLSLAI
        if self.ETLAI < self.ETLAIMN:
            self.ETLAI = self.ETLAIMN
        # Drainage
        if self.ATSW1 <= self.TTSW1:
            self.DRAIN1 = 0
        elif self.ATSW1 > self.TTSW1:
            self.DRAIN1 = (self.ATSW1 - self.TTSW1) * self.DRAINF  
        if self.ATSW <= self.TTSW:
            self.DRAIN = 0
        elif self.ATSW > self.TTSW:
            self.DRAIN = (self.ATSW - self.TTSW) * self.DRAINF  
        # Drain from Hyddep (60 cm)
        if self.ATSW60 <= self.TTSW60:
            self.DRAIN60 = 0
        elif self.ATSW60 > self.TTSW60:
            self.DRAIN60 = (self.ATSW60 - self.TTSW60) * self.DRAINF  
        self.WSTORG = self.WSTORG + self.DRAIN - self.EWAT
        if self.WSTORG < 0:
            self.WSTORG = 0
        # Irrigation
        if self.water == 1 and self.FTSW <= self.IRGLVL and self.NDS > 0 and self.NDS < (0.95 * self.frPM):
            self.IRGW = (self.TTSW - self.ATSW)
            self.IRGNO = self.IRGNO + 1
        else:
            self.IRGW = 0  
        self.CIRGW = self.CIRGW + self.IRGW
        # Rice water balance
        if self.minWH > 0:
            self.WatDep = (self.WAT1 - self.DRAIN1 - self.WSAT1)
            if self.WatDep < 0:
                self.WatDep = 0
            if self.water == 1 and self.WatDep <= self.minWH and self.NDS > 0 and self.NDS < (0.95 * self.frTSG):
                self.IRGW = (self.maxWH - self.WatDep)
                self.IRGNO = self.IRGNO + 1
            else:
                self.IRGW = 0
            self.CIRGW = self.CIRGW + self.IRGW
        # Water exploitation by root growth
        self.GRTD = self.GRTDP * self.DTU # from mm per oC to mm per day
        if self.NDS < self.frBRG:
            self.GRTD = 0
        if self.NDS > self.frTRG:
            self.GRTD = 0
        if self.DDMP == 0:
            self.GRTD = 0
        if self.DEPORT >= self.SOLDEP:
            self.GRTD = 0
        if self.DEPORT >= self.MEED:
            self.GRTD = 0
        if self.WSTORG == 0:
            self.GRTD = 0
        self.DEPORT = self.DEPORT + self.GRTD
        self.EWAT = self.GRTD * self.EXTR
        if self.EWAT > self.WSTORG:
            self.EWAT = self.WSTORG
        # Runoff
        # from rainfed lands only
        self.RUNOF = 0
        self.RAIN2 = self.RAIN
        if self.water == 2:
            self.CN3 = self.CN2 * math.exp(0.00673 * (100 - self.CN2))
            self.CN2S = 0.333 * (self.CN3 - self.CN2) * (1 - 2 * math.exp(-13.86 * self.Slope)) + self.CN2
            self.COVER = (1 - math.exp(-self.KET * self.ETLAI)) * 100
            self.CN2C = self.CN2S - self.COVER * 0.25
            if (self.CN2S - self.CN2C) > 20: 
                self.CN2C = self.CN2S - 20
            self.CN1 = self.CN2C - (20 * (100 - self.CN2C)) / (100 - self.CN2C + math.exp(2.533 - 0.0636 * (100 - self.CN2C)))
            self.SMAX = 254 * (100 / self.CN1 - 1)
            self.S = self.SMAX * (1 - self.ATSW60 / (1.12 * self.TTSW60))
            if self.RAIN2 > (0.2 * self.S):
                self.RUNOF = ((self.RAIN2 - 0.2 * self.S)**2) / (self.RAIN2 + 0.8 * self.S)
            elif self.RAIN2 <= (0.2 * self.S):
                self.RUNOF = 0   
        # from saturated soil under both rainfed and 
        # irrigated except for RICE
        if (self.WAT60 - self.DRAIN60 - self.RUNOF) > self.WSAT60 and self.minWH == 0:
            self.RUNOF60 = (self.WAT60 - self.WSAT60 - self.DRAIN60 - self.RUNOF) * self.SDRAINF
            if self.RUNOF60 < 0:
                self.RUNOF60 = 0
        else:
            self.RUNOF60 = 0  
        self.RUNOF = self.RUNOF + self.RUNOF60
        self.CRAIN = self.CRAIN + self.RAIN
        self.CRUNOF = self.CRUNOF + self.RUNOF
        # Potential ET
        self.TD = 0.6 * self.TMAX + 0.4 * self.TMIN
        self.ALBEDO = self.CALB * (1 - math.exp(-self.KET * self.ETLAI)) + self.SALB * math.exp(-self.KET * self.ETLAI)
        self.EEQ = self.SRAD * (0.004876 - 0.004374 * self.ALBEDO) * (self.TD + 29)
        self.PET = self.EEQ * 1.1
        if self.TMAX > 34:
            self.PET = self.EEQ * ((self.TMAX - 34) * 0.05 + 1.1)
        if self.TMAX < 5:
            self.PET = self.EEQ * 0.01 * math.exp(0.18 * (self.TMAX + 20))
        # Soil evaporation
        self.EOS = self.PET * math.exp(-self.KET * self.ETLAI)
        if self.PET > self.EOSMIN and self.EOS < self.EOSMIN:
            self.EOS = self.EOSMIN
        self.SEVP = self.EOS
        if (self.RAIN + self.IRGW) > self.WETWAT:
            self.DYSE = 1
        if self.DYSE > 1 or self.FTSW < 0.5 or self.ATSW1 <= 1:
            self.SEVP = self.EOS * ((self.DYSE + 1) ** 0.5 - self.DYSE ** 0.5)
            self.DYSE = self.DYSE + 1
        self.CE = self.CE + self.SEVP
        # Plant transpiration
        self.VPTMIN = 0.6108 * math.exp(17.27 * self.TMIN / (self.TMIN + 237.3))
        self.VPTMAX = 0.6108 * math.exp(17.27 * self.TMAX / (self.TMAX + 237.3))
        self.VPD = self.VPDF * (self.VPTMAX - self.VPTMIN)
        self.TR = self.DDMP * self.VPD / self.TEC # VPD in kPa, TEC in Pa
        if self.TR < 0:
            self.TR = 0
        self.CTR = self.CTR + self.TR
        if self.DEPORT <= self.DEP1:
            self.TR1 = self.TR
        elif self.DEPORT > self.DEP1:
            if self.FTSW1 > self.WSSG:
                self.RT1 = 1
            else:
                self.RT1 = self.FTSW1 / self.WSSG
            self.TR1 = self.TR * self.RT1
        # Updating
        self.ATSW1 = self.ATSW1 + self.RAIN + self.IRGW - self.DRAIN1 - self.RUNOF - self.TR1 - self.SEVP
        if self.ATSW1 < 0:
            self.ATSW1 = 0
        self.FTSW1 = self.ATSW1 / self.TTSW1
        self.WAT1 = self.WLL1 + self.ATSW1
        self.ATSW = self.ATSW + self.RAIN + self.IRGW + self.EWAT - self.DRAIN - self.RUNOF - self.TR - self.SEVP
        if self.ATSW < 0:
            self.ATSW = 0
        self.TTSW = self.DEPORT * self.EXTR
        self.WATRL = self.DEPORT * self.CLL + self.ATSW
        self.WSATRL = self.DEPORT * self.SAT
        self.FTSW = self.ATSW / self.TTSW 
        self.ATSW60 = self.ATSW60 + self.RAIN + self.IRGW - self.DRAIN60 - self.RUNOF - self.TR - self.SEVP
        if self.ATSW60 < 0:
            self.ATSW60 = 0
        self.FTSW60 = self.ATSW60 / self.TTSW60
        self.WAT60 = self.WLL60 + self.ATSW60
        # Water-stress-factors
        if self.FTSW > self.WSSL:
            self.WSFL = 1
        else:
            self.WSFL = self.FTSW / self.WSSL
        if self.FTSW > self.WSSG:
            self.WSFG = 1
        else:
            self.WSFG = self.FTSW / self.WSSG
        self.WSFDS = (1 - self.WSFG) * self.WSSD + 1
        if self.WATRL > (0.99 * self.WSATRL) and self.minWH == 0:
            self.WSFN = 0
            self.WSFG = 0
            self.WSFL = 0
        return 0

    def update_Pyear(self):
        self.Pyear += 1
    
    def get_MAT(self):
        return int(self.MAT)
    
    def get_Pyear(self):
        return self.Pyear

    def ini_df_outputs(self):
        self.df_daily_outputs = pd.DataFrame(columns=["sName", "Location", "Manag",
                                                    "Soil", "Crop", "Pyear", "DOY",
                                                    "DAP", "TMP", "DTU", "NDS",
                                                    "LAI", "TCFRUE", "FINT",
                                                    "DDMP", "SGR", "WVEG", "WGRN",
                                                    "WTOP", "DEPORT", "RAIN", "IRGW",
                                                    "RUNOF", "PET", "SEVP", "TR",
                                                    "DRAIN", "ATSW", "FTSW", "CRAIN",
                                                    "CIRGW", "IRGNO", "CRUNOF", "CE",
                                                    "CTR", "WSTORG", "WatDep"])
        self.df_summary_outputs = pd.DataFrame(columns=["sName", "Location", "Manag", "Soil",
                                                        "Crop", "Pyear", "Pdoy", "dtBSG",
                                                        "dtTSG", "dtHAR", "WTOP", "WGRN",
                                                        "HI", "ISOLWAT", "CRAIN", "CIRGW",
                                                        "IRGNO", "FATSW", "CRUNOF", "CE",
                                                        "CTR", "CDRAIN", "ET", "E/ET",
                                                        "CumIPAR", "Fi", "RUE", "WI",
                                                        "Ft", "TE", "MXLAI", "Ysalt",
                                                        "Ywet", "RAINt", "TMINt", "TMAXt",
                                                        "SRADt", "SUMETt", "RAIN2", "TMIN2",
                                                        "TMAX2", "SRAD2", "SUMET2", "RAIN3",
                                                        "TMIN3", "TMAX3", "SRAD3", "SUMET3"])

    def update_daily_outputs(self, row):
        self.df_daily_outputs.loc[row, :] = [self.scenario_name, self.location_name, self.manage_name,
                                             self.soil_name, self.crop_name, self.Pyear, self.DOY,
                                             self.DAP, self.TMP, self.DTU, self.NDS, self.LAI,
                                             self.TCFRUE, self.FINT, self.DDMP, self.SGR, self.WVEG,
                                             self.WGRN, self.WTOP, self.DEPORT, self.RAIN, self.IRGW,
                                             self.RUNOF, self.PET, self.SEVP, self.TR, self.DRAIN,
                                             self.ATSW, self.FTSW, self.CRAIN, self.CIRGW, self.IRGNO,
                                             self.CRUNOF, self.CE, self.CTR, self.WSTORG, self.WatDep]

    def update_summary_outputs(self, row):
        # correction of yield for soil salinity
        self.EC = self.soil_df.EC.iloc[0]
        self.SaltTH = self.crop_df.SaltTH.iloc[0]
        self.SaltSlope = self.crop_df.SaltSlope.iloc[0]
        self.SaltSlope /= 100
        self.MC = self.crop_df["MC%"].iloc[0]
        if self.EC <= self.SaltTH:
            self.RYsalt = 1
        elif self.EC > self.SaltTH:
            self.RYsalt = 1 - self.SaltSlope * (self.EC - self.SaltTH)
        if self.WGRN == 0:
            self.Ysalt = 0
            self.Ywet = 0
            self.HI99 = 0
            self.ET99 = 0
            self.EET99 = 0
            self.RUE99 = 0
            self.WI99 = 0
            self.Ft99 = 0
            self.TE99 = 0
        else:
            self.Ysalt = self.WGRN * self.RYsalt
            self.Ywet = self.Ysalt / (1 - self.MC / 100) * 10
            self.HI99 = self.WGRN / (self.WTOP + 0.00001) # hi
            self.ET99 = self.CE + self.CTR
            self.EET99 = self.CE / (self.CE + self.CTR + 0.00001)
            self.RUE99 = self.WTOP / (self.SUMIPAR * self.AVGFINT + 0.0000001) # RUE
            self.WI99 = self.ISOLWAT + self.CRAIN + self.CIRGW - self.ATSW # WI
            self.Ft99 = self.CTR / (self.ISOLWAT + self.CRAIN + self.CIRGW - self.ATSW + 0.000001) # Ft
            self.TE99 = self.WTOP / (self.CTR + 0.000001) # TE
        self.df_summary_outputs.loc[row, :] = [self.scenario_name, self.location_name, self.manage_name,
                                               self.soil_name, self.crop_name, self.Pyear, self.Pdoy,
                                               self.dtBSG, self.dtTSG, self.dtHAR, self.WTOP, self.WGRN,
                                               self.HI99, self.ISOLWAT, self.CRAIN, self.CIRGW, self.IRGNO,
                                               self.ATSW, self.CRUNOF, self.CE, self.CTR, self.WSTORG,
                                               self.ET99, self.EET99, self.SUMIPAR, self.AVGFINT, self.RUE99,
                                               self.WI99, self.Ft99, self.TE99, self.MXXLAI, self.Ysalt,
                                               self.Ywet, self.SRAINT, self.MTMINT, self.MTMAXT, self.SSRADT,
                                               self.SUMETT, self.SRAIN2, self.MTMIN2, self.MTMAX2, self.SSRAD2,
                                               self.SUMET2, self.SRAIN3, self.MTMIN3, self.MTMAX3, self.SSRAD3,
                                               self.SUMET3]
    
    def write_summary_outputs(self, write_folder):
        if not os.path.exists(os.path.join(write_folder, "summary_csv")):
            os.mkdir(os.path.join(write_folder, "summary_csv"))
        summary_path = os.path.join(write_folder, "summary_csv",
                                    "{}_summary_outputs.csv".format(self.scenario_name))
        self.df_summary_outputs.to_csv(summary_path)
    
    def write_daily_outputs(self, write_folder, year=None):
        if not os.path.exists(os.path.join(write_folder, "daily_csv")):
            os.mkdir(os.path.join(write_folder, "daily_csv"))
        daily_path = os.path.join(write_folder, "daily_csv",
                                  "{}_{}_daily_outputs.csv".format(self.scenario_name, year))
        self.df_daily_outputs.to_csv(daily_path)
    
    def gen_daily_graphs(self, year=None):
        df = self.df_daily_outputs
        self.daily_graphs_output = []
        self.daily_graphs_ids = []
        x_graph = df['DAP'].values.tolist()
        name_dict = {"DTU": {"name": "Daily Temperature Unit", "unit": "oC"},
                     "NDS": {"name": "NDS", "unit": ""},
                     "LAI": {"name": "Leaf Area Index", "unit": "m2 m-2"},
                     "DDMP": {"name": "Daily Dry Matter Production", "unit": "g m-2 d-1"},
                     "SGR": {"name": "Daily Increase in Seed", "unit": "g m-2 d-1"},
                     "WVEG": {"name": "Accumulated Vegetative", "unit": "g m-2"},
                     "WGRN": {"name": "Accumulated Grain", "unit": "g m-2"},
                     "WTOP": {"name": "Accumulated Crop", "unit": "g m-2"}}
        graph_y_vars = ['DTU', 'NDS', 'LAI', ['DDMP', 'SGR'],
                        ['WVEG', 'WGRN', 'WTOP']]
        for y_var in graph_y_vars:
                xaxis_title = 'Days After Planting (DAP)'
                if isinstance(y_var, list):
                    yname = '_'.join(y_var)
                    title_name = ' and '.join([name_dict.get(x).get("name") for x in y_var])
                    title = '{}'.format(title_name)
                    yaxis_title = '{}'.format(title_name)
                    data = []
                    for y in y_var:
                        y_graph = df[y].values.tolist()
                        trace_temp = go.Scatter(x=x_graph, y=y_graph,
                                                mode='lines+markers',
                                                name='{}'.format(y))
                        data.append(trace_temp)
                else:
                    yname = str(y_var)
                    tname = name_dict.get(y_var).get("name")
                    title = '{}'.format(tname)
                    yaxis_title = '{}'.format(tname)
                    data = []
                    y_graph = df[y_var].values.tolist()
                    trace_temp = go.Scatter(x=x_graph, y=y_graph,
                                            mode='lines+markers',
                                            name='{}'.format(y_var))
                    data.append(trace_temp)
                layout = go.Layout(title=title, xaxis=dict(title=xaxis_title),
                                   yaxis=dict(title=yaxis_title),
                                   autosize=False, width=1500, height=1000)
                fig = go.Figure(data=data, layout=layout)
                self.daily_graphs_output.append(fig)
                self.daily_graphs_ids.append('{}_{}_{}_DAP'.format(self.scenario_name, year, yname))
    
    def gen_summary_graphs(self):
        df = self.df_summary_outputs
        self.summary_graphs_output = []
        self.summary_graphs_ids = []
        x_graph = df['Pyear'].values.tolist()
        name_dict = {"WGRN": {"name": "Accumulated Grain", "unit": "g m-2"},
                     "WTOP": {"name": "Accumulated Crop", "unit": "g m-2"}}
        graph_y_vars = [['WGRN', 'WTOP']]
        for y_var in graph_y_vars:
                xaxis_title = 'Simulation Year'
                if isinstance(y_var, list):
                    yname = '_'.join([x for x in y_var])
                    title_name = ' and '.join([name_dict.get('{}'.format(x)).get('name') for x in y_var])
                    title = '{}'.format(title_name)
                    yaxis_title = '{}'.format(title_name)
                    data = []
                    for y in y_var:
                        y_graph = df[y].values.tolist()
                        trace_temp = go.Scatter(x=x_graph, y=y_graph,
                                                mode='markers',
                                                name='{}'.format(y))
                        data.append(trace_temp)
                else:
                    yname = str(y_var)
                    tname = str(name_dict.get('{}'.format(y_var)).get('name'))
                    title = '{}'.format(tname)
                    yaxis_title = '{}'.format(tname)
                    data = []
                    y_graph = df[y_var].values.tolist()
                    trace_temp = go.Scatter(x=x_graph, y=y_graph,
                                            mode='markers',
                                            name='{}'.format(y_var))
                    data.append(trace_temp)
                layout = go.Layout(title=title, xaxis=dict(title=xaxis_title),
                                   yaxis=dict(title=yaxis_title),
                                   autosize=False, width=1500, height=1000)
                fig = go.Figure(data=data, layout=layout)
                self.summary_graphs_output.append(fig)
                self.summary_graphs_ids.append('{}_{}'.format(self.scenario_name, yname))

    def write_graph_image_daily(self, basic_path):
        if not os.path.exists(os.path.join(basic_path, 'graph_images')):
            os.mkdir(os.path.join(basic_path, 'graph_images'))
        if not os.path.exists(os.path.join(basic_path, 'graph_images', "daily")):
            os.mkdir(os.path.join(basic_path, 'graph_images', "daily"))
        for i, f in zip(self.daily_graphs_ids, self.daily_graphs_output):
            output_path = os.path.join(basic_path, 'graph_images', 'daily',
                                       '{}.png'.format(i))
            pio.write_image(f, output_path)

    def write_graph_html_daily(self, basic_path):
        if not os.path.exists(os.path.join(basic_path, 'graph_htmls')):
            os.mkdir(os.path.join(basic_path, 'graph_htmls'))
        if not os.path.exists(os.path.join(basic_path, "graph_htmls", "daily")):
            os.mkdir(os.path.join(basic_path, 'graph_htmls', "daily"))
        for i, f in zip(self.daily_graphs_ids, self.daily_graphs_output):
            output_path = os.path.join(basic_path, 'graph_htmls', 'daily',
                                       '{}.html'.format(i))
            plot(f, filename=output_path, auto_open=False, show_link=False,
                 config=dict(displaylogo=False))
    
    def write_graph_image_summary(self, basic_path):
        if not os.path.exists(os.path.join(basic_path, 'graph_images')):
            os.mkdir(os.path.join(basic_path, 'graph_images'))
        if not os.path.exists(os.path.join(basic_path, "graph_images", "summary")):
            os.mkdir(os.path.join(basic_path, "graph_images", "summary"))
        for i, f in zip(self.summary_graphs_ids, self.summary_graphs_output):
            output_path = os.path.join(basic_path, 'graph_images', "summary",
                                       '{}.png'.format(i))
            pio.write_image(f, output_path)

    def write_graph_html_summary(self, basic_path):
        if not os.path.exists(os.path.join(basic_path, 'graph_htmls')):
            os.mkdir(os.path.join(basic_path, 'graph_htmls'))
        if not os.path.exists(os.path.join(basic_path, "graph_htmls", "summary")):
            os.mkdir(os.path.join(basic_path, "graph_htmls", "summary"))
        for i, f in zip(self.summary_graphs_ids, self.summary_graphs_output):
            output_path = os.path.join(basic_path, "graph_htmls", "summary",
                                       '{}.html'.format(i))
            plot(f, filename=output_path, auto_open=False, show_link=False,
                 config=dict(displaylogo=False))



def ProcessMain(ini_dict, input_dict):
    """ Main()
    """
    scenario_df = input_dict.get("scenario").get("df")
    num_scenarios = len(scenario_df)
    logging.info("Detected {} number of crops to run as scenarios".format(num_scenarios))
    # loop each scenario (crop)
    for scnNo in range(0, num_scenarios-1):
        # Main Parameters Set
        LocRowNo = scenario_df.LocRowNo.iloc[scnNo]
        MangRowNo = scenario_df.MangRowNo.iloc[scnNo]
        SoilRowNo = scenario_df.SoilRowNo.iloc[scnNo]
        CropRowNo = scenario_df.CropRowNo.iloc[scnNo]
        scenario_name = scenario_df.Scenario.iloc[scnNo]
        location_name = input_dict.get("location").get("df").loc[input_dict.get("location").get("df")["#Loc"] == LocRowNo]["Location"].values[0]
        manage_name = input_dict.get("manage").get("df").loc[input_dict.get("manage").get("df")["#Manag"] == MangRowNo]["Manage"].values[0]
        soil_name = input_dict.get("soil").get("df").loc[input_dict.get("soil").get("df")["#Soil"] == SoilRowNo]["Soil"].values[0]
        crop_name = input_dict.get("crop").get("df").loc[input_dict.get("crop").get("df")["#Crop"] == CropRowNo]["Crop"].values[0]
        logging.info("Running scenario: {}".format(scenario_name))
        logging.info("Detected location row: {}".format(LocRowNo))
        logging.info("Detected manage row: {}".format(MangRowNo))
        logging.info("Detected soil row: {}".format(SoilRowNo))
        logging.info("Detected crop row: {}".format(CropRowNo))
        logging.info("Detected location name: {}".format(location_name))
        logging.info("Detected manage name: {}".format(manage_name))
        logging.info("Detected soil name: {}".format(soil_name))
        logging.info("Detected crop name: {}".format(crop_name))
        # Weather        
        weather_filename = input_dict.get("location").get("df").loc[input_dict.get("location").get("df")["#Loc"] == LocRowNo]["Weather"].values[0]
        weather_file = os.path.join(ini_dict.get("input_folder"), "Weather", "{}".format(weather_filename))
        logging.info("Weather filename: {}".format(weather_filename))
        logging.info("Weather pathname: {}".format(weather_file))
        # Other Parameters        
        Pyear = input_dict.get("manage").get("df").loc[input_dict.get("manage").get("df")["#Manag"] == MangRowNo]["Fyear"].values[0]
        yrno = input_dict.get("manage").get("df").loc[input_dict.get("manage").get("df")["#Manag"] == MangRowNo]["yrno"].values[0]
        weather_first_row = input_dict.get("location").get("df").loc[input_dict.get("location").get("df")["#Loc"] == LocRowNo]["WthFirstRow"].values[0]
        water = input_dict.get("manage").get("df").loc[input_dict.get("manage").get("df")["#Manag"] == MangRowNo]["water"].values[0]
        logging.info("Pyear: {}, yrno: {}, weather_first_row: {}, water: {}".format(Pyear, yrno, weather_first_row, water))
        # Setup main dataframe information
        # fill-in NaN or blank values as zero
        manage_df = pd.DataFrame(input_dict.get("manage").get("df").loc[input_dict.get("manage").get("df")["#Manag"] == MangRowNo])
        manage_df = manage_df.fillna(0)
        crop_df = pd.DataFrame(input_dict.get("crop").get("df").loc[input_dict.get("crop").get("df")["#Crop"] == CropRowNo])
        crop_df = crop_df.fillna(0)
        soil_df = pd.DataFrame(input_dict.get("soil").get("df").loc[input_dict.get("soil").get("df")["#Soil"] == SoilRowNo])
        soil_df = soil_df.fillna(0)
        location_df = pd.DataFrame(input_dict.get("location").get("df").loc[input_dict.get("location").get("df")["#Loc"] == LocRowNo])
        location_df = location_df.fillna(0)
        weather_df = pd.read_excel(weather_file, usecols=[0, 1, 2, 3, 4, 5], skiprows=[0,1,2,3,4,5,6,7,8], header=0, engine='openpyxl')
        logging.info(manage_df)
        logging.info(crop_df)
        logging.info(soil_df)
        logging.info(location_df)
        logging.info(weather_df.head())
        logging.info(weather_df.tail())
        # Initialize Crop Class
        N_Crop = Crop(manage_df, crop_df, soil_df, location_df, weather_df,
                    scenario_name=scenario_name, LocRowNo=LocRowNo, MangRowNo=MangRowNo, SoilRowNo=SoilRowNo, CropRowNo=CropRowNo,
                    location_name=location_name, manage_name=manage_name, soil_name=soil_name, crop_name=crop_name,
                    weather_file=weather_file, weather_first_row=weather_first_row,
                    Pyear=Pyear, yrno=yrno, water=water)
        # Initialize daily/summary reporting dataframes
        N_Crop.ini_df_outputs()
        # loops each simulation year        
        for yr in range(0, yrno):
            logging.info("Starting {} Simulation Year.".format(N_Crop.get_Pyear()))
            N_Crop.LocManagInputs()
            N_Crop.FindSimSowDate()
            daily_output_counter = 0
            while True:
                N_Crop.Weather()
                N_Crop.PhenologyBD()
                N_Crop.CropLAI()
                N_Crop.DMProduction()
                if water == 1 or water == 2:
                    N_Crop.SoilWater()
                N_Crop.update_daily_outputs(daily_output_counter)
                mat_trigger = N_Crop.get_MAT()
                if mat_trigger == 1:
                    break
                daily_output_counter += 1
            N_Crop.write_daily_outputs(ini_dict.get("write"), year=N_Crop.get_Pyear())
            N_Crop.gen_daily_graphs(year=N_Crop.get_Pyear())
            N_Crop.write_graph_image_daily(ini_dict.get("write"))
            N_Crop.write_graph_html_daily(ini_dict.get("write"))
            N_Crop.update_summary_outputs(yr)
            logging.info("Finished {} Simulation Year.".format(N_Crop.get_Pyear()))
            N_Crop.update_Pyear()
        N_Crop.write_summary_outputs(ini_dict.get("write"))
        N_Crop.gen_summary_graphs()
        N_Crop.write_graph_image_summary(ini_dict.get("write"))
        N_Crop.write_graph_html_summary(ini_dict.get("write"))
    return 0





if __name__ == "__main__":
    # begin runtime clock
    start = datetime.datetime.now()
    # determine the absolute file pathname of this *.py file
    abspath = os.path.abspath(__file__)
    # from the absolute file pathname determined above,
    # extract the directory path
    dir_name = os.path.dirname(abspath)
    # initiate logger
    log_file = os.path.join(dir_name, 'ssm_icrop2_{}.log'
                            .format(str(start.date())))
    CreateLogger(log_file)
    # create the command line parser object from argparse
    parser = argparse.ArgumentParser()
    # set the command line arguments available to user's
    parser.add_argument("--input_folder", "-if", type=str,
                        help="Provide the full pathname of runtime inputs \
                        folder containing all the input *.csv files for the model run")
    parser.add_argument("--write", "-w", type=str,
                        help="Provide the full folder pathname for the \
                        output data files to be written too")
    # create an object of the command line inputs
    args = parser.parse_args()
    # read the command line inputs into a Python dictionary
    # e.g. ini_dict.get("write") : 'C:\Users\zleady\Desktop\output.csv'
    ini_dict = vars(args)
    # log input variables
    for k in list(ini_dict.keys()):
        logging.info('Initialization Dict key: {} \n value: {}'
                     .format(k, ini_dict.get(k)))
    # read-in input *.csv information
    input_dict = ReadInputs(ini_dict)
    # log input absolute pathnames
    for i in list(input_dict.keys()):
        ipath = input_dict.get(i).get("path")
        logging.info("Read {} inputs from path:\n {}".format(i, ipath))
    # log input read-in data
    for i in list(input_dict.keys()):
        idf = input_dict.get(i).get("df")
        logging.info("Data from {}".format(i))
        logging.info(idf)
    # begin main processing function
    ProcessMain(ini_dict, input_dict)
    # complete runtime logging
    elapsed_time = datetime.datetime.now() - start
    logging.info('Runtime: {}'.format(str(elapsed_time)))