# standard libraries
import os
import sys
import datetime
import logging
import argparse
import math
import ast

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

class Crop:
    """ Main Crop Class for Simulation
    """
    def __init__(self, manage_df, crop_df, soil_df, location_df, weather_df, irrigation_df, nferti_df,
                 scenario_name=None, scnNo=None, LocRowNo=None, MangRowNo=None, SoilRowNo=None, CropRowNo=None,
                 location_name=None, manage_name=None, soil_name=None, crop_name=None,
                 weather_file=None, weather_first_row=None,
                 Pyear=None, yrno=None, water=None, nitrogen=None):
        # Dataframe Inputs Initialization
        self. manage_df = manage_df
        self.crop_df = crop_df
        self.soil_df = soil_df
        self.location_df = location_df
        self.weather_df = weather_df
        self.irrigation_df = irrigation_df
        self.nferti_df = nferti_df
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
        self.nitrogen = nitrogen
        self.scnNo = scnNo



    def LocManagInputs(self):
        self.LAT = self.location_df["Latitute"].iloc[0]
        self.VPDF = self.location_df["VPDF"].iloc[0]
        self.tchng = self.location_df["tchng"].iloc[0]
        self.pchng = self.location_df["pchng"].iloc[0]
        self.CO2 = self.location_df["CO2"].iloc[0]

        self.FixFind = self.manage_df["FixFind"].iloc[0]
        self.SimDoy = self.manage_df["SimDoy"].iloc[0]
        self.Pdoy = self.manage_df["Fpdoy"].iloc[0]
        if self.SimDoy == self.Pdoy:
            self.SimDoy = self.Pdoy - 1
        self.SearchDur = self.manage_df["SearchDur"].iloc[0]
        self.RfreeP = self.manage_df["RfreeP"].iloc[0]
        self.RfreeP = 5
        self.SowTmp = self.manage_df["SowTmp"].iloc[0]
        self.SowWat = self.manage_df["SowWat"].iloc[0]

        self.water = self.manage_df["water"].iloc[0]
        self.WatDep = 0
        self.NFERT = 0
        self.CNFERT = 0
        self.NVOL = 0
        self.CNVOL = 0
        self.NLEACH = 0
        self.CNLEACH = 0
        self.NMIN = 0
        self.CNMIN = 0
        self.NDNIT = 0
        self.CNDNIT = 0
        self.SNAVL = 0
        self. NSOL = 0
        self.NUP = 0
        self.NLF = 0
        self.NST = 0
        self.NVEG = 0
        self.NGRN = 0
        self.CNUP = 0
        self.CUMBNF = 0
        self.INSOL = 0
        self.dtBSG = 0
        self.MTMIN2 = 0
        self.MTMAX2 = 0
        self.BNF = 0
        self.DLAI = 0
        self.XNLF = 0
        self.NFC = 0
        self.IRGLVL = self.manage_df["IRGLVL"].iloc[0]
        self.StopDoy = self.manage_df["StopDoy"].iloc[0]
        self.ClipNo = self.manage_df["ClipNo"].iloc[0]
        self.minWH = self.manage_df["mnWH"].iloc[0]
        self.maxWH = self.manage_df["mxWH"].iloc[0]

        self.IrrigRowNo = self.manage_df["IrrigRowNo"].iloc[0]
        if self.water == 3:
            self.IRNUM = self.irrigation_df["IRNUM"].iloc[0] #Number of irrg. application
            self.WATiT = self.irrigation_df["DAP-NDS-DOY-based"].iloc[0]  #1=DAP-based, 2=CBD-based, 3=DOY-based

            self.DAPIR = ast.literal_eval(self.irrigation_df["when"].iloc[0])
            self.IRGWI = ast.literal_eval(self.irrigation_df["Amount(mm)"].iloc[0])
            self.WAT01 = 0
            if isinstance(self.DAPIR, list) or isinstance(self.IRGWI, list):
                self.WAT01 = [0]*self.IRNUM
                assert len(self.DAPIR) == len(self.IRGWI) == len(self.WAT01)
            else:
                self.DAPIR = [self.DAPIR]
                self.IRGWI = [self.IRGWI]
                self.WAT01 = [self.WAT01]
            # for n in range(0, self.IRNUM):
            #     self.DAPIR[n] = ThisWorkbook.Worksheets("Irrigation").Cells(self.IrrigRowNo, 4 + n * 2 - 1) #Time of irrig. application
            #     self.IRGWI[n] = ThisWorkbook.Worksheets("Irrigation").Cells(self.IrrigRowNo, 4 + n * 2)   #Irrig. water (mm)
            #     self.WAT01[n] = 0
        
        self.nitrogen = self.manage_df["nitrogen"].iloc[0]
        self.NfertRowNo = self.manage_df["NfertRowNo"].iloc[0]
        if self.nitrogen == 2:
            self.FN = self.nferti_df["N_Applications"].iloc[0] #Number of N application
            self.NATiT = self.nferti_df["DAP-NDS-DOY-based"].iloc[0] #1=DAP-based, 2=CBD-based,  3=DOY-based
            
            self.DAPNF = ast.literal_eval(self.nferti_df["when"].iloc[0])
            self.NFERTI = ast.literal_eval(self.nferti_df["Amount"].iloc[0])
            self.VOLFI = ast.literal_eval(self.nferti_df["Frac_Vol"].iloc[0])
            self.NFA01 = 0
            if isinstance(self.DAPNF, list) or isinstance(self.NFERTI, list) or isinstance(self.VOLFI, list): 
                self.NFA01 = [0]*self.FN
                assert len(self.DAPNF) == len(self.NFERTI) == len(self.VOLFI) == len(self.NFA01)
            else:
                self.DAPNF = [self.DAPNF]
                self.NFERTI = [self.NFERTI]
                self.VOLFI = [self.VOLFI]
                self.NFA01 = [self.NFA01]
            # for n in range(1, FN):
            #     self.DAPNF(N) = ThisWorkbook.Worksheets("Nferti").Cells(self.NfertRowNo, 4 + N * 3 - 2) #Time of N application as top-dressing
            #     self.NFERTI(N) = ThisWorkbook.Worksheets("Nferti").Cells(self.NfertRowNo, 4 + N * 3 - 1) #N fertilizer amount at the top-dressing (gN.m-2)
            #     self.VOLFI(N) = ThisWorkbook.Worksheets("Nferti").Cells(self.NfertRowNo, 4 + N * 3)  #Fraction volatilization
            #     self.NFA01(N) = 0
        self.NDS = 0
        self.DAS = 0
        self.DAP = 0
        self.SNOW = 0
        self.MAT = 0
        self.CUMBNF = 0
        self.WSFL = 1
        self.WSFG = 1
        self.WSFN = 1
        self.WSFDS = 1
        self.WSXF = 1
        self.iniPheno = 0
        self.iniLAI = 0
        self.iniDMP = 0
        self.iniSW = 0
        self.iniPNB = 0
        self.iniSNB = 0
    
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
            self.frBNF = self.crop_df.frBNF.iloc[0]
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
            self.MATYP = 1
        if self.DOY == self.StopDoy:
            self.MAT = 1
            self.MATYP = 4
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
        self.heatf = 1
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
            self.WSFG = 1 #?
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
            self.HYDDEP = self.soil_df.HYDDEP.iloc[0] #?                
            self.MAI1 = self.manage_df.MAI1.iloc[0]
            self.MAI = self.manage_df.MAI.iloc[0]
            # changed IPATSW to ISOLWAT 20210202
            # self.ISOLWAT = self.SOLDEP * self.EXTR * self.MAI
            self.IPATSW = self.SOLDEP * self.EXTR * self.MAI #?
            self.ATSW = self.DEPORT * self.EXTR * self.MAI
            self.TTSW = self.DEPORT * self.EXTR
            self.FTSW = self.ATSW / self.TTSW
            # changed IPATSW to ISOLWAT 20210202
            # self.WSTORG = self.ISOLWAT - self.ATSW
            self.WSTORG = self.IPATSW - self.ATSW #?
            self.ATSW1 = self.DEP1 * self.EXTR * self.MAI1
            self.TTSW1 = self.DEP1 * self.EXTR
            self.FTSW1 = self.ATSW1 / self.TTSW1
            self.WLL1 = self.DEP1 * self.CLL
            self.WAT1 = self.WLL1 + self.ATSW1
            self.WSAT1 = self.DEP1 * self.SAT
            # self.HYDDEP = 600 # see above
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
        # Irrigation #modified N
        if self.water == 1:
            if self.FTSW <= self.IRGLVL and self.NDS > 0 and self.NDS < (0.95 * self.frPM):
                self.IRGW = (self.TTSW - self.ATSW)
                self.IRGNO = self.IRGNO + 1
            else:
                self.IRGW = 0
        elif self.water == 2:
            # nothing, rainfed
            self.IRGW = 0
        elif self.water == 3:
            self.IRGW = 0
            if self.WATiT == 1: # irrigation applied based on DAP
                for i in range(0, self.IRNUM):
                    if self.DAP == self.DAPIR:
                        self.IRGW = self.IRGWI[i] # mm
                        self.IRGNO = self.IRGNO + 1
            elif self.WATiT == 2: # irrigation applied based on CBD with user-specified water
                for i in range(0, self.IRNUM):
                    if self.NDS >= self.DAPIR[i] and self.WAT01[i] == 0:
                        self.IRGW = self.IRGWI[i]
                        self.IRGNO = self.IRGNO + 1
                        self.WAT01[i] = 1
            elif self.WATiT == 3: # irrigation applied based on DOY
                for i in range(0, self.IRNUM):
                    if self.DOY == self.DAPIR[i]:
                        self.IRGW = self.IRGWI[i] # mm
                        self.IRGNO = self.IRGNO + 1
            elif self.WATiT == 4:
                for i in range(0, self.IRNUM):
                    if self.CBD >= self.DAPIR[i] and self.WAT01[i] == 0:
                        self.IRGW = (self.TTSWRZ - self.ATSWRZ) # mm
                        if self.IRGW < 0:
                            self.IRGW = 0
                        self.IRGNO = self.IRGNO + 1
                        self.WAT01[i] = 1
        self.CIRGW = self.CIRGW + self.IRGW
        # Rice water balance
        if self.minWH > 0: # identifies rice flooded fields
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
        self.WDULRL = self.DEPORT * self.DUL #?
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
        self.WSFN = self.WSFG #?
        self.WSFDS = (1 - self.WSFG) * self.WSSD + 1
        self.WSXF = 1 #?
        if self.WATRL > (0.99 * self.WSATRL) and self.minWH == 0:
            self.WSFN = 0
            self.WSFG = 0
            self.WSFL = 0
            self.WSXF = 0 #?
        return 0
    
    def CropLAIN(self):
        # nitrogen
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

            self.SLNG = self.crop_df.SLNG.iloc[0]
            self.SLNS = self.crop_df.SLNS.iloc[0]

            self.PART1 = np.log((1 / self.y1LAI - 1) / (1 / self.x1NDS))
            self.PART2 = np.log((1 / self.y2LAI - 1) / (1 / self.x2NDS))
            self.BL = (self.PART2 - self.PART1) / (self.x1NDS - self.x2NDS)
            self.AL = self.PART1 + self.BL * self.x1NDS

            self.GLAI = 0
            self.LAI1 = 0
            self.LAI2 = 0
            self.LAI = 0
            self.BLSLAI = 0
            self.MXXLAI = 0
            self.iniLAI = 1
        # yesterday LAI to intercept PAR today
        if self.GLAI != 0 and self.GLAI > (self.INLF / self.SLNG):
            self.GLAI = (self.INLF / self.SLNG)
        self.LAI = self.LAI + self.GLAI - self.DLAI
        if self.LAI < 0:
            self.LAI = 0
        if self.LAI > self.MXXLAI: # saving the value of actual max LAI
            self.MXXLAI = self.LAI
        if self.NDS > self.frBSG and self.NDS < self.frTSG and self.LAI < 0.05:
            self.NDS = self.frTSG
            self.MATYP = 2 # pre-mature due to low LAI
        if self.NDS <= self.frEMR:
            self.GLAI = 0
            self.DLAI = 0
        elif self.NDS >= self.frEMR and self.NDS < self.frBLS:
            self.LAI2 = self.NDS / (self.NDS + math.exp(self.AL - self.BL * self.NDS)) * self.LAIMX
            self.GLAI = (self.LAI2 - self.LAI1) * self.WSFL
            self.LAI1 = self.LAI2
            self.BLSLAI = self.LAI # saving the value of LAI at BLS
        elif self.NDS >= self.frBLS:
            self.GLAI = 0
        self.DLAI = self.XNLF / (self.SLNG - self.SLNS)
        # Frost and Heat
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
        self.heatf = 1
        if self.NDS > self.frEMR and self.TMAX > self.HeatTh:
            self.heatf = 1 + (self.TMAX - self.HeatTh) * self.HtLDR # Semenov-Sirius
            if self.heatf < 1:
                self.heatf = 1
            self.DLAIH = self.DLAI * self.heatf
        if self.DLAI < self.DLAIH:
            self.DLAI = self.DLAIH
    
    def PlantN(self):
        # Plant Nitrogen
        if self.iniPNB == 0:
            self.SLA = self.crop_df.SLA.iloc[0]
            self.SLNG = self.crop_df.SLNG.iloc[0]
            self.SLNS = self.crop_df.SLNS.iloc[0]
            self.SNCG = self.crop_df.SNCG.iloc[0]
            self.SNCS = self.crop_df.SNCS.iloc[0]
            self.GNC = self.crop_df.GNC.iloc[0]
            self.MXNUP = self.crop_df.MXNUP.iloc[0]
            self.WLF = 0.5
            self.WST = 0.5
            self.NST = self.WST * self.SNCG
            self.NLF = self.LAI * self.SLNG
            self.CNUP = self.NST + self.NLF
            self.NGRN = 0
            self.BNF = 0
            self.CUMBNF = 0
            self.iniPNB = 1
        # leaf & stem DM
        if self.NDS <= self.frEMR or self.NDS > self.frTSG:
            self.GLF = 0
            self.GST = 0
        elif self.NDS > self.frEMR and self.NDS < self.frTSG:
            self.DDMP2 = self.DDMP - self.SGR * self.GCC
            if self.DDMP2 < 0:
                self.DDMP2 = 0
            self.GLF = self.GLAI / self.SLA
            if self.GLF > self.DDMP2:
                # written as
                #self.GFL = self.DDMP2 #?
                self.GLF = self.DDMP2
            self.GST = self.DDMP2 - self.GLF
            if self.GST < 0:
                self.GST = 0
        self.WLF = self.WLF + self.GLF
        self.WST = self.WST + self.GST

        if self.NDS <= self.frEMR or self.NDS > self.frTSG:
            self.NUP = 0
            self.XNLF = 0
            self.XNST = 0
            self.INLF = 0
            self.INST = 0
            self.INGRN = 0
        elif self.NDS > self.frEMR and self.NDS < self.frBSG:
            self.INGRN = 0
            self.NSTDF = (self.WST * self.SNCG) - self.NST
            if self.NSTDF < 0:
                self.NSTDF = 0
            self.NUP = (self.GST * self.SNCG) + (self.GLAI * self.SLNG) + self.NSTDF
            if self.NUP > self.MXNUP:
                self.NUP = self.MXNUP
            self.NFC = self.NFC * 3 / 4 + self.NUP / self.WVEG * (1/4) # from Sinclair et al. 2003 for legumes
            if self.NDS > self.frBNF:
                self.NUP = self.NUP * self.WSFN # legume
            if self.NUP < 0:
                self.NUP = 0
            if self.FTSW > 1:
                self.NUP = self.NUP * self.WSXF
            if self.DDMP == 0:
                self.NUP = 0
            if self.frBNF >= self.frBSG and self.NUP > self.SNAVL:
                self.NUP = self.SNAVL # for non-legume
            if self.NDS < self.frBNF and self.NUP > self.SNAVL:
                self.NUP = self.SNAVL # legume
            if self.NUP > self.SNAVL:
                self.BNF = self.NUP - self.SNAVL # legume
            if self.BNF < 0:
                self.BNF = 0
            self.CUMBNF = self.CUMBNF + self.BNF

            if self.NST <= (self.WST * self.SNCS):
                self.INST = self.WST * self.SNCS - self.NST
                self.XNST = 0
                if self.INST >= self.NUP:
                    self.INLF = 0
                    self.XNLF = self.INST - self.NUP
                elif self.INST < self.NUP:
                    self.INLF = self.GLAI * self.SLNG
                    if self.INLF > (self.NUP - self.INST):
                        self.INLF = self.NUP - self.INST
                    self.INST = self.NUP - self.INLF
                    self.XNLF = 0
            elif self.NST > (self.WST * self.SNCS):
                self.INLF = self.GLAI * self.SLNG
                self.XNLF = 0
                if self.INLF >= self.NUP:
                    self.INST = 0
                    self.XNST = self.INLF - self.NUP
                    if self.XNST > (self.NST - self.WST * self.SNCS):
                        self.XNST = self.NST - self.WST * self.SNCS
                    self.INLF = self.NUP + self.XNST
                elif self.INLF < self.NUP:
                    self.INST = self.NUP - self.INLF
                    self.XNST = 0
        elif self.NDS >= self.frBSG and self.NDS <= self.frTSG:
            self.INGRN = self.SGR * self.GNC
            self.NUP = self.INGRN + (self.GST * self.SNCG) + (self.GLAI * self.SLNG)
            if self.NUP < 0:
                self.NUP = 0
            if self.NUP > self.MXNUP:
                self.NUP = self.MXNUP
            if self.NDS < self.frBNF:
                self.DNF = 0 # before BNF activation OR for non-legume crops
            elif self.NDS >= self.frBNF:
                self.PDNF = self.NFC * self.WVEG # legume
                if self.PDNF > self.NUP:
                    self.PDNF = self.NUP # legume
                self.DNF = self.PDNF * self.WSFN # legume
                if self.DDMP <= (self.SGR * self.GCC):
                    self.DNF = 0 # legume
                if self.DDMP == 0:
                    self.DNF = 0 # legume
            if self.FTSW > 1:
                self.NUP = self.NUP * self.WSXF
            if self.DDMP < (self.SGR / self.GCC):
                self.NUP = 0
            if self.DDMP == 0:
                self.NUP = 0
            if self.frBNF >= self.frBSG and self.NUP > self.SNAVL: # for non-legume
                self.NUP = self.SNAVL
            if self.NUP > (self.SNAVL + self.DNF):
                self.NUP = self.SNAVL + self.DNF 
            self.BNF = self.NUP - self.SNAVL
            if self.BNF < 0:
                self.BNF = 0
            self.CUMBNF = self.CUMBNF + self.BNF
            if self.NUP > self.INGRN:
                # N is excess of seed needs
                self.NUP2 = self.NUP - self.INGRN # <---8888888
                if self.NST <= (self.WST * self.SNCS):
                    self.INST = self.WST * self.SNCS - self.NST
                    self.XNST = 0
                    if self.INST >= self.NUP2:
                        self.INLF = 0
                        self.XNLF = self.INST - self.NUP2
                    elif self.INST < self.NUP2:
                        self.INLF = self.GLAI * self.SLNG
                        if self.INLF > (self.NUP2 - self.INST):
                            self.INLF = self.NUP2 - self.INST
                        self.INST = self.NUP2 - self.INLF
                        self.XNLF = 0
                elif self.NST > (self.WST * self.SNCS):
                    self.INLF = self.GLAI * self.SLNG
                    self.XNLF = 0
                    if self.INLF >= self.NUP2:
                        self.INST = 0
                        self.XNST = self.INLF - self.NUP2
                        if self.XNST > (self.NST - self.WST * self.SNCS):
                            self.XNST = self.NST - self.WST * self.SNCS
                        self.INLF = self.NUP2 + self.XNST
                    elif self.INLF < self.NUP2:
                        self.INST = self.NUP2 - self.INLF
                        self.XNST = 0
            elif self.NUP <= self.INGRN:
                # Need to transfer N from vegetative tissue
                self.INLF = 0
                self.INST = 0
                self.XNLF = (self.INGRN - self.NUP) * self.FXLF
                self.XNST = (self.INGRN - self.NUP) * (1 - self.FXLF)
        self.NST = self.NST + self.INST - self.XNST
        self.NLF = self.NLF + self.INLF - self.XNLF
        self.NVEG = self.NLF + self.NST
        self.NGRN = self.NGRN + self.INGRN
        self.CNUP = self.CNUP + self.NUP
        self.TRLN = self.LAI * (self.SLNG - self.SLNS) + (self.NST - self.WST * self.SNCS)
        self.FXLF = self.LAI * (self.SLNG - self.SLNS) / (self.TRLN + 1E-12)
        if self.FXLF > 1:
            self.FXLF = 1
        if self.FXLF < 0:
            self.FXLF = 0
        return 0

    def SoilN(self):
        # Parameters and Initials
        if self.iniSNB == 0:
            self.FG = self.soil_df.CF.iloc[0]      #Fraction soil > 2mm
            self.BD1 = self.soil_df["BD"].iloc[0]     #Soil bulk density (g.cm-3)
            self.NORGP = self.soil_df.NORG.iloc[0]   #Organic N (%)
            self.FMIN = self.soil_df.FMIN.iloc[0]    #Frac. Org N avail. for mineralization
            self.NO3 = self.soil_df["NO3"].iloc[0]     #gN.m-2
            self.NH4 = self.soil_df["NH4"].iloc[0]    #gN.m-2
                
            self.SOILM = self.HYDDEP * self.BD1 * (1 - self.FG) * 1000  #g.m-2
            self.NORG = self.NORGP * 0.01 * self.SOILM             #g.m-2
            self.MNORG = self.NORG * self.FMIN                     #gN.m-2 org. N avail. for miner.
            
            #NO3 = NO3 * (14 / 62) * 0.000001 * SOILM  #from ppm to gN.m-2
            #NH4 = NH4 * (14 / 18) * 0.000001 * SOILM  #from ppm to gN.m-2
                
            self.NSOL = (self.NO3 +self.NH4)             #gN.m-2
            self.NCON = self.NSOL / (self.WAT60 * 1000)   #gN.g-1 H2O
                
            self.INSOL = self.NSOL
            self.CNFERT = 0
            self.CNVOL = 0
            self.CNLEACH = 0
            self.CNMIN = 0
            self.CNDNIT = 0
            self.iniSNB = 1
        # Initialization at DAP=1 (if you want model to be re-initialized at DAP=1)
        if self.DAP == 1:
            self.NORGP = self.soil_df.NORG.iloc[0] # Organic N (%)
            self.NO3 = self.soil_df["NO3"].iloc[0] # gN.m-2
            self.NH4 = self.soil_df["NH4"].iloc[0] # gN.m-2
    
            self.NORG = self.NORGP * 0.01 * self.SOILM  #g.m-2
            self.MNORG = self.NORG * self.FMIN  #gN.m-2 org. N avail. for miner.
          
            self.NSOL = (self.NO3 + self.NH4)  #gN.m-2
            self.NCON = self.NSOL / (self.WAT60 * 1000) #gN.g-1 H2O
          
            self.INSOL = self.NSOL
            self.CNFERT = 0
            self.CNVOL = 0
            self.CNLEACH = 0
            self.CNMIN = 0
            self.CNDNIT = 0
        # N net mineralization
        self.TMPS = self.TMP
        if self.TMPS > 35:
            self.TMPS = 35
        self.KNMIN = 24 * math.exp(17.753 - 6350.5 / (self.TMPS + 273)) / 168
        self.KN = 1 - math.exp(-self.KNMIN)
        if self.FTSW60 < 0.9:
            self.RN = 1.111 * self.FTSW60
        if self.FTSW60 >= 0.9:
            self.RN = 10 - 10 * self.FTSW60
        if self.RN < 0:
            self.RN = 0
        self.NMIN = self.MNORG * self.RN * self.KN
        self.NMIN = self.NMIN * (0.0002 - self.NCON) / 0.0002  #threshold = 200 mgN.L-1
        if self.NMIN < 0:
            self.NMIN = 0
        self.MNORG = self.MNORG - self.NMIN
        self.CNMIN = self.CNMIN + self.NMIN
        # N application and voltailization
        self.NFERT = 0
        self.NVOL = 0
        if self.NATiT == 1:          #N appl. based on DAP
            for n in range(0, self.FN):
                if self.DAP == self.DAPNF[n]:
                    self.NFERT = self.NFERTI[n]        #gN.m-2
                    self.VOLF = self.VOLFI[n] / 100
                    self.NVOL = self.VOLF * self.NFERT  #gN.m-2
        elif self.NATiT == 2:      #N appl. based on NDS
            for n in range(0, self.FN):
                if self.NDS >= self.DAPNF[n] and self.NFA01[n] == 0:
                    self.NFERT = self.NFERTI[n]         #gN.m-2
                    self.VOLF = self.VOLFI[n] / 100
                    self.NVOL = self.VOLF * self.NFERT #gN.m-2
                    self.NFA01[n] = 1
        elif self.NATiT == 3:     #N appl. based on DOY
            for n in range(0, self.FN):
                if self.DOY == self.DAPNF[n]:
                    self.NFERT =self. NFERTI[n]       #gN.m-2
                    self.VOLF = self.VOLFI[n] / 100
                    self.NVOL = self.VOLF * self.NFERT    #gN.m-2
        self.CNFERT = self.CNFERT + self.NFERT
        self.CNVOL = self.CNVOL + self.NVOL
        # N downward movement
        self.NLEACH = self.NSOL * (self.DRAIN60 / (self.WAT60 + self.DRAIN60)) #gN.m-2                        ':::
        if self.NCON <= 1E-06:
            self.NLEACH = 0     #threshold = 1 mgN.L-1
        self.CNLEACH = self.CNLEACH + self.NLEACH
        # N denitification
        self.NDNIT = 0
        if self.FTSW60 > 1:
            self.XNCON = self.NCON
            if self.XNCON > 0.0004:
                self.XNCON = 0.0004   #threshold = 400 mgN.L-1
            self.KDNIT = 6 * math.exp(0.07735 * self.TMPS - 6.593)
            self.NDNIT = self.XNCON * (1 - math.exp(-self.KDNIT))   #gN.g-1 H2O
            self.NDNIT = self.NDNIT * self.WAT60 * 1000        #gN.m-2
            #WFNDNIT = (WAT60 - WDUL60) / (WSAT60 - WDUL60)
            #If WFNDNIT > 1 Then WFNDNIT = 1
            #NDNIT = NDNIT * WFNDNIT
            self.depfac = 300 / self.HYDDEP #NDNIT only in top 30cm
            if self.depfac > 1:
                self.depfac = 1
            self.NDNIT = self.NDNIT * self.depfac
        if self.minWH > 0:
            self.NDNIT = 0     #Assuming no NDNIT in rice flooded fields
        self.CNDNIT = self.CNDNIT + self.NDNIT
        # Frac. top layer with roots
        self.FROOT60 = self.DEPORT / self.HYDDEP
        if self.FROOT60 > 1:
            self.FROOT60 = 1
        # Updating
        self.NSOL = self.NSOL + self.NMIN + self.NFERT - self.NVOL - self.NLEACH - self.NDNIT - (self.NUP - self.BNF)
        if self.NSOL < 0:
            self.NSOL = 0
        self.NCON = self.NSOL / (self.WAT60 * 1000)
        self.SNAVL = (self.NCON - 1E-06) * self.ATSW60 * 1000 * self.FROOT60  #threshold = 1 mgN.L-1
        if self.SNAVL < 0:
            self.SNAVL = 0
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
            self.NDS = 0
            self.DTU = 0
            self.DAP = 0 # added Soltani 20210127
            if self.water == 1 or self.water == 2 or self.water == 3:
                self.SoilWater()
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
                if self.nitrogen == 2:
                    self.SoilN()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 5 #7?
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
                if self.nitrogen == 2:
                    self.SoilN()                    
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 5 #7?
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
                if self.nitrogen == 2:
                    self.SoilN()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 5 #7?
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
                if self.nitrogen == 2:
                    self.SoilN()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 5 #7?
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
                if self.nitrogen == 2:
                    self.SoilN()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 5 #7?
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
                if self.nitrogen == 2:
                    self.SoilN()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 5 #7?
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
                if self.nitrogen == 2:
                    self.SoilN()
                self.CumFind += 1
                if self.CumFind > self.SearchDur:
                    self.MAT = 1
                    self.MATYP = 5 #7?
                if self.SUMRAIN >= self.SowWat and self.MVMTMP < self.SowTmp and self.Nfixfind >= self.RfreeP:
                    break
                if self.MAT == 1:
                    break
            self.Pdoy = self.DOY
        elif self.FixFind == 91:
        # Finding bud burst based on TU accumulation from 1st Jan.
            self.SForc = 0
            self.ForcTB = self.crop_df.TBD.iloc[0]
            self.ForcReq = self.crop_df.ForcReq.iloc[0]
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
                if self.nitrogen == 2:
                    self.SoilN()
                if self.SForc >= self.ForcReq:
                    break
            self.Pdoy = self.DOY
        if self.MAT == 1:
            return 1
        return 0

    def update_Pyear(self):
        self.Pyear += 1
    
    def get_MAT(self):
        return int(self.MAT)
    
    def get_Pyear(self):
        return self.Pyear


    def ini_df_headers(self):
        self.df_daily_outputs = pd.DataFrame(columns=["sName", "Location", "Manag",
                                                    "Soil", "Crop", "Pyear", "DOY",
                                                    "DAP", "TMP", "DTU", "NDS",
                                                    "LAI", "TCFRUE", "FINT",
                                                    "DDMP", "SGR", "WVEG", "WGRN",
                                                    "WTOP", "DEPORT", "RAIN", "IRGW",
                                                    "RUNOF", "PET", "SEVP", "TR",
                                                    "DRAIN", "ATSW", "FTSW", "CRAIN",
                                                    "CIRGW", "IRGNO", "CRUNOF", "CE",
                                                    "CTR", "WSTORG", "WatDep", "NFERT",
                                                    "CNFERT", "NVOL", "CNVOL", "NLEACH",
                                                    "CNLEACH", "NMIN", "CNMIN", "NDNIT",
                                                    "CNDNIT", "SNAVL", "NSOL", "NUP", "NLF",
                                                    "NST", "NVEG", "NGRN", "CNUP", "CUMBNF"])


        self.df_summary_outputs = pd.DataFrame(columns=["sName", "Location", "Manag", "Soil",
                                                        "Crop", "Pyear", "Pdoy", "dtBSG",
                                                        "dtTSG", "dtHAR", "WTOP", "WGRN",
                                                        "HI99", "ISOLWAT", "CRAIN", "CIRGW",
                                                        "IRGNO", "ATSW", "CRUNOF", "CE",
                                                        "CTR", "WSTORG", "ET99", "EET99",
                                                        "SUMIPAR", "AVGFINT", "RUE99",
                                                        "WI99", "Ft99", "TE99",
                                                        "MXXLAI", "Ysalt", "Ywet", "NLF",
                                                        "NST", "NVEG", "NGRN", "CNUP",
                                                        "CUMBNF", "INSOL", "CNFERT", "CNMIN",
                                                        "NSOL", "CNVOL", "CNLEACH", "CNDNIT",
                                                        "MATYP", "SRAINT", "MTMINT", "MTMAXT",
                                                        "SSRADT", "SUMETT", "SRAIN2", "MTMIN2",
                                                        "MTMAX2", "SSRAD2", "SUMET2", "SRAIN3",
                                                        "MTMIN3", "MTMAX3", "SSRAD3", "SUMET3"])
    def update_daily_outputs(self, row):
        self.df_daily_outputs.loc[row, :] = [self.scenario_name, self.location_name, self.manage_name,
                                             self.soil_name, self.crop_name, self.Pyear, self.DOY,
                                             self.DAP, self.TMP, self.DTU, self.NDS, self.LAI,
                                             self.TCFRUE, self.FINT, self.DDMP, self.SGR, self.WVEG,
                                             self.WGRN, self.WTOP, self.DEPORT, self.RAIN, self.IRGW,
                                             self.RUNOF, self.PET, self.SEVP, self.TR, self.DRAIN,
                                             self.ATSW, self.FTSW, self.CRAIN, self.CIRGW, self.IRGNO,
                                             self.CRUNOF, self.CE, self.CTR, self.WSTORG, self.WatDep,
                                             self.NFERT, self.CNFERT, self.NVOL, self.CNVOL, self.NLEACH,
                                             self.CNLEACH, self.NMIN, self.CNMIN, self.NDNIT, self.CNDNIT,
                                             self.SNAVL, self.NSOL, self.NUP, self.NLF, self.NST, self.NVEG,
                                             self.NGRN, self.CNUP, self.CUMBNF]

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
                                               self.Ywet, self.NLF, self.NST, self.NVEG, self.NGRN,
                                               self.CNUP, self.CUMBNF, self.INSOL, self.CNFERT, self.CNMIN,
                                               self.NSOL, self.CNVOL, self.CNLEACH, self.CNDNIT, self.MATYP,
                                               self.SRAINT, self.MTMINT, self.MTMAXT, self.SSRADT,
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
                     "WTOP": {"name": "Accumulated Crop", "unit": "g m-2"},
                     "TR": {"name": "Transpiration", "unit": "mm"},
                     "SEVP": {"name": "Soil Evaporation", "unit": "mm"},
                     "PET": {"name": "Potential Evapotranspiration", "unit": "mm"}}
        graph_y_vars = ['DTU', 'NDS', 'LAI', ['DDMP', 'SGR'], ['TR', 'SEVP', 'PET'],
                        ['WVEG', 'WGRN', 'WTOP']]
        for y_var in graph_y_vars:
                xaxis_title = 'Days After Planting (DAP)'
                if isinstance(y_var, list):
                    yname = '_'.join(y_var)
                    title_name = ' and<br>'.join(["{} ({})".format(name_dict.get(x).get("name"),
                                                                name_dict.get(x).get("unit")) for x in y_var])
                    
                    title = '{}<br>{}'.format(self.scenario_name, title_name)
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
                    tunit = name_dict.get(y_var).get("unit")
                    title = '{}<br>{} ({})'.format(self.scenario_name, tname, tunit)
                    yaxis_title = title
                    data = []
                    y_graph = df[y_var].values.tolist()
                    trace_temp = go.Scatter(x=x_graph, y=y_graph,
                                            mode='lines+markers',
                                            name='{}'.format(y_var))
                    data.append(trace_temp)
                layout = go.Layout(title=title, xaxis=dict(title=xaxis_title),
                                   yaxis=dict(title=yaxis_title),
                                   autosize=True,
                                   legend=dict(yanchor="top",
                                               y=0.99,
                                               xanchor="left",
                                               x=0.01),
                                    title_x=0.5)
                fig = go.Figure(data=data, layout=layout)
                self.daily_graphs_output.append(fig)
                self.daily_graphs_ids.append('{}_{}_{}_DAP'.format(self.scenario_name, year, yname))
    
    def gen_summary_graphs(self):
        df = self.df_summary_outputs
        df_daily_sum = self.df_daily_outputs
        self.summary_graphs_output = []
        self.summary_graphs_ids = []
        x_graph = df['Pyear'].values.tolist()
        name_dict = {"WGRN": {"name": "Accumulated Grain", "unit": "g m-2"},
                     "WTOP": {"name": "Accumulated Crop", "unit": "g m-2"},
                     "SEVP": {"name": "Soil Evaporation", "unit": "mm"},
                     "TR": {"name": "Accumulated Transpiration", "unit": "mm"},
                     "PET": {"name": "Potential Evapotranspiration", "unit": "mm"},
                     "TE99": {"name": "Transpiration", "unit": "mm"},
                     "ET99": {"name": "Evapotranspiration", "unit": "mm"},
                     "EET99": {"name": "E/ET Ratio", "unit":"Ratio"}}
        graph_y_vars = [['WGRN', 'WTOP'], ['TE99', 'ET99'], ['TE99', 'EET99'], ["TR", "SEVP", "ET99", "PET"]]
        for y_var in graph_y_vars:
                xaxis_title = 'Simulation Year'
                if isinstance(y_var, list):
                    yname = '_'.join([x for x in y_var])
                    title_name = ' and<br>'.join(["{} ({})".format(name_dict.get(x).get('name'),
                                                                name_dict.get(x).get("unit")) for x in y_var])
                    title = '{}'.format(title_name)
                    yaxis_title = '{}'.format(title_name)
                    data = []
                    for y in y_var:
                        if not y == "TR" and not y == "PET" and not y == "SEVP":
                            y_graph = df[y].values.tolist()
                        else: 
                            y_graph = [float(df_daily_sum[y].sum())]
                        trace_temp = go.Bar(x=x_graph, y=y_graph,
                                            name='{}'.format(y))
                        data.append(trace_temp)
                else:
                    yname = str(y_var)
                    tname = str(name_dict.get(yvar).get("name"))
                    tunit = str(name_dict.get(y_var).get("unit"))
                    title = '{} ({})'.format(tname, tunit)
                    yaxis_title = title
                    data = []
                    if not y_var == "TR" and not y_var == "PET":
                        y_graph = df[y_var].values.tolist()
                    else:
                        y_graph = [float(df_daily_sum[y_var].sum())]
                    trace_temp = go.Bar(x=x_graph, y=y_graph,
                                        name='{}'.format(y_var))
                    data.append(trace_temp)
                layout = go.Layout(title=title, xaxis=dict(title=xaxis_title),
                                   yaxis=dict(title=yaxis_title),
                                   autosize=True,
                                   legend=dict(yanchor="top",
                                               y=0.99,
                                               xanchor="left",
                                               x=0.01),
                                    title_x=0.5)
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

def SimMain(ini_dict):
    scenario_path = os.path.join(ini_dict.get("input_folder"), "scenario_inputs.csv")
    logging.info("Scenario DataFrame Read-in Path: {}".format(scenario_path))
    scenario_df = pd.read_csv(scenario_path, header=0, index_col=None)
    logging.info(scenario_df)
    num_scenarios = len(scenario_df)
    logging.info("Detected {} number of scenarios".format(num_scenarios))
    for scnNo in range(0, num_scenarios-1):
        scnName = scenario_df.Scenario.iloc[scnNo]
        logging.info("Scenario Name: {}".format(scnName))
        LocRowNo = scenario_df.LocRowNo.iloc[scnNo]
        MangRowNo = scenario_df.MangRowNo.iloc[scnNo]
        SoilRowNo = scenario_df.SoilRowNo.iloc[scnNo]
        CropRowNo = scenario_df.CropRowNo.iloc[scnNo]
        logging.info("LocRowNo={} MangRowNo={} SoilRowNo={} CropRowNo={}".format(LocRowNo, MangRowNo, SoilRowNo, CropRowNo))
        location_path = os.path.join(ini_dict.get("input_folder"), "location_inputs.csv")
        manage_path = os.path.join(ini_dict.get("input_folder"), "manage_inputs.csv")
        soil_path = os.path.join(ini_dict.get("input_folder"), "soil_inputs.csv")
        crop_path = os.path.join(ini_dict.get("input_folder"), "crop_inputs.csv")
        irrigation_path = os.path.join(ini_dict.get("input_folder"), "irrigation_inputs.csv")
        nferti_path = os.path.join(ini_dict.get("input_folder"), "nferti_inputs.csv")
        logging.info("{}".format(location_path))
        logging.info("{}".format(manage_path))
        logging.info("{}".format(soil_path))
        logging.info("{}".format(crop_path))
        logging.info("{}".format(irrigation_path))
        logging.info("{}".format(nferti_path))        
        location_df = pd.read_csv(location_path, header=0, index_col=None)
        manage_df = pd.read_csv(manage_path, header=0, index_col=None)
        soil_df = pd.read_csv(soil_path, header=0, index_col=None)
        crop_df = pd.read_csv(crop_path, header=0, index_col=None)
        irrigation_df = pd.read_csv(irrigation_path, header=0, index_col=None)
        nferti_df = pd.read_csv(nferti_path, header=0, index_col=None)

        locName = location_df.loc[location_df["#Loc"]==LocRowNo]["Location"].values[0]
        wthFile = location_df.loc[location_df["#Loc"]==LocRowNo]["Weather"].values[0]
        mngName = manage_df.loc[manage_df["#Manag"]==MangRowNo]["Manag"].values[0]
        solName = soil_df.loc[soil_df["#Soil"]==SoilRowNo]["Soil"].values[0]
        crpName = crop_df.loc[crop_df["#Crop"]==CropRowNo]["Crop"].values[0]
        logging.info("LocName={} MngName={} SolName={} CrpName={}".format(locName, mngName, solName, crpName))
        logging.info("Weather File: {}".format(wthFile))
        weather_path = os.path.join(ini_dict.get("input_folder"), "Weather", "{}.csv".format(wthFile))
        logging.info("Weather Pathname: {}".format(weather_path))
        weather_df = pd.read_csv(weather_path, header=0, index_col=None, na_values='.')
        logging.info("Weather DataFrame \n{}".format(weather_df))
    
        # select df data based on RowNo id
        location_df = pd.DataFrame(location_df.loc[location_df["#Loc"] == LocRowNo])
        manage_df = pd.DataFrame(manage_df.loc[manage_df["#Manag"] == MangRowNo])
        soil_df = pd.DataFrame(soil_df.loc[soil_df["#Soil"] == SoilRowNo])
        crop_df = pd.DataFrame(crop_df.loc[crop_df["#Crop"] == CropRowNo])
        # fill in NaN to 0
        location_df = location_df.fillna(0)
        manage_df = manage_df.fillna(0)
        soil_df = soil_df.fillna(0)
        crop_df = crop_df.fillna(0)
        weather_df = weather_df.fillna(0)

        # select irrigation and nitrogen data
        IrrigRowNo = manage_df.loc[manage_df["#Manag"]==MangRowNo]["IrrigRowNo"].values[0]
        NfertRowNo = manage_df.loc[manage_df["#Manag"]==MangRowNo]["NfertRowNo"].values[0]
        irrigation_df = pd.DataFrame(irrigation_df.loc[irrigation_df["IrrigRowNo"] == IrrigRowNo])
        nferti_df = pd.DataFrame(nferti_df.loc[nferti_df["NfertRowNo"] == NfertRowNo])
        # fill in NaN to 0 on irrigation and nitrogen data
        irrigation_df = irrigation_df.fillna(0)
        nferti_df = nferti_df.fillna(0)


        #ReDim DAPIR(10), IRGWI(10), WAT01(10)
        #ReDim DAPNF(10), NFERTI(10), VOLFI(10), NFA01(10)
        # DAPIR = np.zeros(10)
        # IRGWI = np.zeros(10)
        # WAT01 = np.zeros(10)
        # DAPNF = np.zeros(10)
        # NFERTI = np.zeros(10)
        # VOLFI = np.zeros(10)
        # NFA01 = np.zeros(10)

        Pyear = manage_df.loc[manage_df["#Manag"]==MangRowNo]["Fyear"].values[0]
        yrno = manage_df.loc[manage_df["#Manag"]==MangRowNo]["yrno"].values[0]
        wthRow = location_df.loc[location_df["#Loc"]==LocRowNo]["WthFirstRow"].values[0]
        water =  manage_df.loc[manage_df["#Manag"]==MangRowNo]["water"].values[0]
        nitrogen =  manage_df.loc[manage_df["#Manag"]==MangRowNo]["nitrogen"].values[0]
        logging.info("Pyear={} yrno={} wthRow={} water={} nitrogen={}".format(Pyear, yrno, wthRow, water, nitrogen))
        
        
        # Main Sim Begin
        N_Crop = Crop(manage_df, crop_df, soil_df, location_df,
                      weather_df, irrigation_df, nferti_df,
                      scenario_name=scnName, scnNo=scnNo, LocRowNo=LocRowNo,
                      MangRowNo=MangRowNo, SoilRowNo=SoilRowNo, CropRowNo=CropRowNo,
                      location_name=locName, manage_name=mngName,
                      soil_name=solName, crop_name=crpName,
                      weather_file=wthFile, weather_first_row=wthRow,
                      Pyear=Pyear, yrno=yrno, water=water, nitrogen=nitrogen)
        N_Crop.ini_df_headers()
        for yr in range(0, yrno):
            N_Crop.LocManagInputs()
            N_Crop.FindSimSowDate()
            daily_output_counter = 0
            while True:
                N_Crop.Weather()
                N_Crop.PhenologyBD()
                if nitrogen == 0:
                    N_Crop.CropLAI()
                else:
                    N_Crop.CropLAIN()
                N_Crop.DMProduction()
                if nitrogen == 2:
                    N_Crop.PlantN()
                if water == 1 or water == 2 or water == 3:
                    N_Crop.SoilWater()
                if nitrogen == 2:
                    N_Crop.SoilN()
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
                


if __name__ == "__main__":
    # begin runtime clock
    start = datetime.datetime.now()
    # determine the absolute file pathname of this *.py file
    abspath = os.path.abspath(__file__)
    # from the absolute file pathname determined above,
    # extract the directory path
    dir_name = os.path.dirname(abspath)
    # initiate logger
    log_file = os.path.join(dir_name, 'N_ssm_icrop2_{}.log'
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
    # begin main processing function
    SimMain(ini_dict)
    # complete runtime logging
    elapsed_time = datetime.datetime.now() - start
    logging.info('Runtime: {}'.format(str(elapsed_time)))