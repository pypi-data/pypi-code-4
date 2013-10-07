from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import String, Integer

Base = declarative_base()

class Target(Base):
    __tablename__ = 'targets'
    id = Column(Integer, primary_key=True)
    objective = Column(Integer, ForeignKey('objectives.id'))
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)

class Action(Base):
    __tablename__ = 'actions'
    id = Column(Integer, primary_key=True)
    target = Column(Integer, ForeignKey('targets.id'))
    name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    community_action = Column(String)

class CommunityReport(Base):
    __tablename__ = 'community_report'
    action = Column(Integer, ForeignKey('actions.id'), primary_key=True)
    year = Column(Integer, primary_key=True)
    progress = Column(String)

class Header(Base):
    __tablename__ = '01Header'
    CountryCode = Column(String, primary_key=True)
    Country = Column(String)
    PrefilledName = Column(String)
    PrefilledVerifiedCOName = Column(String)
    PrefilledVerifiedCODate = Column(String)
    PrefilledVerifiedECName = Column(String)
    PrefilledVerifiedECDate = Column(String)
    DataEntryMSName = Column(String)
    DataEntryCOName = Column(String)
    VerifiedMSName = Column(String)
    VerifiedMSDate = Column(String)
    VerifiedCOName = Column(String)
    VerifiedCODate = Column(String)
    VerifiedECName = Column(String)
    VerifiedECDate = Column(String)

class CountryReport(Base):
    __tablename__ = 'country_report'
    Country = Column(String, primary_key=True)
    Objective = Column(Integer, primary_key=True)
    Ident = Column(String, primary_key=True)
    MOP = Column(String, primary_key=True)
    Narative = Column(String)
    MSComments = Column(String)
    Clarifcations = Column(String)
    DataSource = Column(String)
    MSVerrified = Column(String)
    EC1Verrified = Column(String)
    EC2Verrified = Column(String)
    CO1Verrified = Column(String)
    CO2Verrified = Column(String)

class ProgressMeasures(Base):
    __tablename__ = 'progress_measures'
    id = Column(String, primary_key=True)
    mop = Column(String)
    text = Column(String)

class Objective(Base):
    __tablename__ = 'objectives'
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String)
    headline = Column(String)
    order = Column(Integer)

class A1_1_1_Natura2000Compleat(Base):
  __tablename__ = 'A1_1_1_Natura2000Compleat'
  CountryCode = Column(String, primary_key=True)
  HabitatSites = Column(String)
  HabitatArea = Column(String)
  HabitatTerraArea = Column(String)
  HabitatMarineSites = Column(String)
  HabitatMarineArea = Column(String)
  BirdSites = Column(String)
  BirdArea = Column(String)
  BirdTerraArea = Column(String)
  BirdMarineSites = Column(String)
  BirdMarineArea = Column(String)

class A1_1_1_Natura2000Plan(Base):
    __tablename__ = 'A1_1_1_Natura2000Plan'
    CountryCode = Column(String, primary_key=True)
    Compleat = Column(String)
    Preperation = Column(String)
    None_ = Column('None', String)

class A1_1_3(Base):
    __tablename__ = 'A1_1_3'
    CountryCode = Column(String, primary_key=True)
    Y2004 = Column(String)
    Y2005 = Column(String)
    Y2006 = Column(String)
    Y2007 = Column(String)
    Y2008 = Column(String)
    Y2009 = Column(String)

class A1_3(Base):
    __tablename__ = 'A1_3'
    CountryCode = Column(String, primary_key=True)
    BirdRed = Column(String)
    BirdAmd = Column(String)
    BirdGrn = Column(String)

class A1_2_3(Base):
    __tablename__ = 'A1_2_3'
    CountryCode = Column(String, primary_key=True)
    ToolInPlace = Column(String)
    ToolInDev = Column(String)

class A1_3_1_ActionPlan(Base):
    __tablename__ = 'A1_3_1_ActionPlan'
    CountryCode = Column(String, primary_key=True)
    BirdComp = Column(String)
    MammalComp = Column(String)
    AmphibComp = Column(String)
    FishComp = Column(String)
    InvertComp = Column(String)
    PlantsComp = Column(String)
    BirdPlan = Column(String)
    MammalPlan = Column(String)
    AmphibPlan = Column(String)
    FishPlan = Column(String)
    InvertPlan = Column(String)
    PlantsPlan = Column(String)
    PlanDataSource = Column(String)

class A1_3_1_BirdIndicator(Base):
    __tablename__ = 'A1_3_1_BirdIndicator'
    CountryCode = Column(String, primary_key=True)
    IndicatorDev = Column(String)
    IndicatorDesc = Column(String)
    DataSource = Column(String)

class A1_3_1_BirdMonitoring(Base):
    __tablename__ = 'A1_3_1_BirdMonitoring'
    CountryCode = Column(String, primary_key=True)
    active = Column(String)

class A1_3_1_RedList(Base):
    __tablename__ = 'A1_3_1_RedList'
    CountryCode = Column(String, primary_key=True)
    Bird = Column(String)
    Mammal = Column(String)
    Amphib = Column(String)
    Fish = Column(String)
    Invert = Column(String)
    Plants = Column(String)

class A2_1_1(Base):
    __tablename__ = 'A2_1_1'
    CountryCode = Column(String, primary_key=True)
    EAFRDTotal = Column(String)
    EAFRDAxis2 = Column(String)
    EAFRDAxis2Percent = Column(String)
    PublicTotal = Column(String)
    PublicAxis2 = Column(String)
    PublicAxis2Percent = Column(String)
    AgriEAFRD = Column(String)
    AgriEAFRDPercent = Column(String)
    AgriPublic = Column(String)
    AgriPublicPercent = Column(String)
    NaturaAgriEAFRD = Column(String)
    NaturaAgriEAFRDPercent = Column(String)
    NaturaAgriPublic = Column(String)
    NaturaAgriPublicPercent = Column(String)
    NaturaForestEAFRD = Column(String)
    NaturaForestEAFRDPercent = Column(String)
    NaturaForestPublic = Column(String)
    NaturaForestPublicPercent = Column(String)
    ForestEAFRD = Column(String)
    ForestEAFRDPercent = Column(String)
    ForestPublic = Column(String)
    ForestPublicPercent = Column(String)

class A2_1_3_ForestCert(Base):
    __tablename__ = 'A2_1_3_ForestCert'
    CountryCode = Column(String, primary_key=True)
    FSCArea = Column(String)
    FSCPercent = Column(String)
    PECFArea = Column(String)
    PECFPercent = Column(String)
    OtherCert = Column(String)
    OtherCertArea = Column(String)
    OtherCertPercent = Column(String)

class A2_1_3_HNV(Base):
    __tablename__ = 'A2_1_3_HNV'
    CountryCode = Column(String, primary_key=True)
    Area = Column(String)
    Share = Column(String)
    NoMapped = Column(String)
    Mapped = Column(String)

class A2_1_4(Base):
    __tablename__ = 'A2_1_4'
    CountryCode = Column(String, primary_key=True)
    Livestock = Column(String)
    Pasture = Column(String)
    Landscape = Column(String)
    Habitat = Column(String)
    GAEC = Column(String)
    GAECDetails = Column(String)

class A2_1_6(Base):
    __tablename__ = 'A2_1_6'
    CountryCode = Column(String, primary_key=True)
    Training = Column(String)
    TrainingAmount = Column(String)
    TrainingPercent = Column(String)

class A2_1_8(Base):
    __tablename__ = 'A2_1_8'
    CountryCode = Column(String, primary_key=True)
    RegBirds = Column(String)
    RegFarming = Column(String)
    RegForestry = Column(String)
    RegTree = Column(String)
    NatBirds = Column(String)
    NatFarming = Column(String)
    NatForestry = Column(String)
    NatTree = Column(String)
    BioIndicators = Column(String)
    BioIndicatorsDetails = Column(String)

class A2_1_9(Base):
    __tablename__ = 'A2_1_9'
    CountryCode = Column(String, primary_key=True)
    Amount = Column(String)
    Percentage = Column(String)

class A2_1_11_NatStrats(Base):
    __tablename__ = 'A2_1_11_NatStrats'
    CountryCode = Column(String, primary_key=True)
    NatStratNo = Column(String)
    NatStratDev = Column(String)
    NatStratImp = Column(String)
    NatStratDontKnow = Column(String)
    ActionNo = Column(String)
    ActionDev = Column(String)
    ActionImp = Column(String)
    ActionDontKnow = Column(String)
    OtherDesc = Column(String)
    OtherNo = Column(String)
    OtherDev = Column(String)
    OtherImp = Column(String)
    OtherDontKnow = Column(String)
    NatStratCrop = Column(String)
    NatStratLivestock = Column(String)
    NatStratTree = Column(String)
    ActionCrop = Column(String)
    ActionLivestock = Column(String)
    ActionTree = Column(String)
    OtherDescIn = Column(String)
    OtherCropIn = Column(String)
    OtherLivestockIn = Column(String)
    OtherTreeIn = Column(String)
    CropNum = Column(String)
    CropValue = Column(String)
    LivestockNum = Column(String)
    LivestockValue = Column(String)
    TreeNum = Column(String)
    TreeValue = Column(String)
    KeyAims = Column(String)

class A2_1_11_RDPPayments(Base):
    __tablename__ = 'A2_1_11_RDPPayments'
    CountryCode = Column(String, primary_key=True)
    EAFRD = Column(String)
    EAFRDPercent = Column(String)
    Public = Column(String)
    PublicPercent = Column(String)

class A2_1_12(Base):
    __tablename__ = 'A2_1_12'
    CountryCode = Column(String, primary_key=True)
    EAFRDTotal = Column(String)
    EAFRDAxis2 = Column(String)
    EAFRDAxis2Percent = Column(String)
    PublicTotal = Column(String)
    PublicAxis2 = Column(String)
    PublicAxis2Percent = Column(String)
    AgriEAFRD = Column(String)
    AgriEAFRDPercent = Column(String)
    AgriPublic = Column(String)
    AgriPublicPercent = Column(String)
    NaturaAgriEAFRD = Column(String)
    NaturaAgriEAFRDPercent = Column(String)
    NaturaAgriPublic = Column(String)
    NaturaAgriPublicPercent = Column(String)
    NaturaForestEAFRD = Column(String)
    NaturaForestEAFRDPercent = Column(String)
    NaturaForestPublic = Column(String)
    NaturaForestPublicPercent = Column(String)
    ForestPublic = Column(String)
    ForestPublicPercent = Column(String)

class A2_1_15(Base):
    __tablename__ = 'A2_1_15'
    CountryCode = Column(String, primary_key=True)
    Afforest = Column(String)
    Deforest = Column(String)
    AfforestDetails = Column(String)
    DeforestDetails = Column(String)
    EIAAfforest = Column(String)
    EIAAfforestLimits = Column(String)
    EIADeforest = Column(String)
    EIADeforestLimits = Column(String)
    SEAAfforest = Column(String)
    SEAAfforestLimits = Column(String)
    SEADeforest = Column(String)
    SEADeforestLimits = Column(String)
    BioAfforest = Column(String)
    BioAfforestLimits = Column(String)
    BioDeforest = Column(String)
    BioDeforestLimits = Column(String)
    OtherAfforest = Column(String)
    OtherAfforestLimits = Column(String)
    OtherDeforest = Column(String)
    OtherDeforestLimits = Column(String)

class A2_2_1(Base):
    __tablename__ = 'A2_2_1'
    CountryCode = Column(String, primary_key=True)
    NatMonitor = Column(String)
    NatMonitorDetails = Column(String)
    MandatoryParam = Column(String)
    Projects = Column(String)

class A2_3_FWHabitatStatus(Base):
    __tablename__ = 'A2_3_FWHabitatStatus'
    CountryCode = Column(String, primary_key=True)
    FVNum = Column(String)
    FVPercent = Column(String)
    UNum = Column(String)
    UPercent = Column(String)
    XXNum = Column(String)
    XXPercent = Column(String)
    NANum = Column(String)
    NAPercent = Column(String)

class A2_3_FWQuality(Base):
    __tablename__ = 'A2_3_FWQuality'
    CountryCode = Column(String, primary_key=True)
    BOD2002 = Column(String)
    BOD2003 = Column(String)
    BOD2004 = Column(String)
    BOD2005 = Column(String)
    Ammonium2002 = Column(String)
    Ammonium2003 = Column(String)
    Ammonium2004 = Column(String)
    Ammonium2005 = Column(String)
    NO3River2002 = Column(String)
    NO3River2003 = Column(String)
    NO3River2004 = Column(String)
    NO3River2005 = Column(String)
    NO3Lake2002 = Column(String)
    NO3Lake2003 = Column(String)
    NO3Lake2004 = Column(String)
    NO3Lake2005 = Column(String)
    NO3Ground2002 = Column(String)
    NO3Ground2003 = Column(String)
    NO3Ground2004 = Column(String)
    NO3Ground2005 = Column(String)
    OPRiver2002 = Column(String)
    OPRiver2003 = Column(String)
    OPRiver2004 = Column(String)
    OPRiver2005 = Column(String)
    TPLake2002 = Column(String)
    TPLake2003 = Column(String)
    TPLake2004 = Column(String)
    TPLake2005 = Column(String)
    Y1992To2005 = Column(String)


class A2_3_InlandBathing(Base):
    __tablename__ = 'A2_3_InlandBathing'
    CountryCode = Column(String, primary_key=True)
    Total2005 = Column(String)
    Total2006 = Column(String)
    Total2007 = Column(String)
    Total2008 = Column(String)
    Comply2005 = Column(String)
    Comply2006 = Column(String)
    Comply2007 = Column(String)
    Comply2008 = Column(String)
    Percent2005 = Column(String)
    Percent2006 = Column(String)
    Percent2007 = Column(String)
    Percent2008 = Column(String)

class A2_3_1_Stations(Base):
    __tablename__ = 'A2_3_1_Stations'
    CountryCode = Column(String, primary_key=True)
    num = Column(String)

class A2_3_1_BioAsses(Base):
    __tablename__ = 'A2_3_1_BioAsses'
    CountryCode = Column(String, primary_key=True)
    GrnRiverPP = Column(String)
    GrnRiverMP = Column(String)
    GrnRiverBI = Column(String)
    GrnRiverFI = Column(String)
    GrnLakePP = Column(String)
    GrnLakeMP = Column(String)
    GrnLakeBI = Column(String)
    GrnLakeFI = Column(String)
    GrnTransPP = Column(String)
    GrnTransMA = Column(String)
    GrnTransBI = Column(String)
    GrnTransFI = Column(String)
    GrnCostalPP = Column(String)
    GrnCostalMA = Column(String)
    GrnCostalBI = Column(String)
    YelRiverPP = Column(String)
    YelRiverMP = Column(String)
    YelRiverBI = Column(String)
    YelRiverFI = Column(String)
    YelLakePP = Column(String)
    YelLakeMP = Column(String)
    YelLakeBI = Column(String)
    YelLakeFI = Column(String)
    YelTransPP = Column(String)
    YelTransMA = Column(String)
    YelTransBI = Column(String)
    YelTransFI = Column(String)
    YelCostalPP = Column(String)
    YelCostalMA = Column(String)
    YelCostalBI = Column(String)
    RedRiverPP = Column(String)
    RedRiverMP = Column(String)
    RedRiverBI = Column(String)
    RedRiverFI = Column(String)
    RedLakePP = Column(String)
    RedLakeMP = Column(String)
    RedLakeBI = Column(String)
    RedLakeFI = Column(String)
    RedTransPP = Column(String)
    RedTransMA = Column(String)
    RedTransBI = Column(String)
    RedTransFI = Column(String)
    RedCostalPP = Column(String)
    RedCostalMA = Column(String)
    RedCostalBI = Column(String)

class A2_4_1(Base):
    __tablename__ = 'A2_4_1'
    CountryCode = Column(String, primary_key=True)
    NumInstalls = Column(String)
    NumPermits = Column(String)
    NumPermitsNotUpdated = Column(String)
    NumPermitsUpdated = Column(String)
    OutstandingPermits = Column(String)

class A2_4_2_EcoAtRisk(Base):
    __tablename__ = 'A2_4_2_EcoAtRisk'
    CountryCode = Column(String, primary_key=True)
    Acid2000 = Column(String)
    Acid2010 = Column(String)
    Acid2020 = Column(String)
    AcidMFR2010 = Column(String)
    Eutro2000 = Column(String)
    Eutro2010 = Column(String)
    Eutro2020 = Column(String)
    EutroMFR2010 = Column(String)

class A2_4_2_Emission(Base):
    __tablename__ = 'A2_4_2_Emission'
    CountryCode = Column(String, primary_key=True)
    NO2006 = Column(String)
    NO2007 = Column(String)
    NO2008 = Column(String)
    NONECD = Column(String)
    NO2010 = Column(String)
    SO2006 = Column(String)
    SO2007 = Column(String)
    SO2008 = Column(String)
    SONECD = Column(String)
    SO2010 = Column(String)
    NH2006 = Column(String)
    NH2007 = Column(String)
    NH2008 = Column(String)
    NHNECD = Column(String)
    NH2010 = Column(String)
    Volatile2006 = Column(String)
    Volatile2007 = Column(String)
    Volatile2008 = Column(String)
    VolatileNECD = Column(String)
    Volatile2010 = Column(String)

class A2_4_3(Base):
    __tablename__ = 'A2_4_3'
    CountryCode = Column(String, primary_key=True)
    Y1990_1992 = Column(String)
    Y2002_2004 = Column(String)
    Change = Column(String)

class A3(Base):
    __tablename__ = 'A3'
    CountryCode = Column(String, primary_key=True)
    MeanTrophic = Column(String)
    Change1999_2004 = Column(String)
    Change1984_2004 = Column(String)

class A3_1(Base):
    __tablename__ = 'A3_1'
    CountryCode = Column(String, primary_key=True)
    MarineFVNum = Column(String)
    MarineFVPercent = Column(String)
    MarineUNum = Column(String)
    MarineUPercent = Column(String)
    MarineXXNum = Column(String)
    MarineXXPercent = Column(String)
    MarineNANum = Column(String)
    MarineNAPercent = Column(String)
    CostalFVNum = Column(String)
    CostalFVPercent = Column(String)
    CostalUNum = Column(String)
    CostalUPercent = Column(String)
    CostalXXNum = Column(String)
    CostalXXPercent = Column(String)
    CostalNANum = Column(String)
    CostalNAPercent = Column(String)
    SpeciesFVNum = Column(String)
    SpeciesFVPercent = Column(String)
    SpeciesUNum = Column(String)
    SpeciesUPercent = Column(String)
    SpeciesXXNum = Column(String)
    SpeciesXXPercent = Column(String)
    SpeciesNANum = Column(String)
    SpeciesNAPercent = Column(String)
    NotFishFVNum = Column(String)
    NotFishFVPercent = Column(String)
    NotFishUNum = Column(String)
    NotFishUPercent = Column(String)
    NotFishXXNum = Column(String)
    NotFishXXPercent = Column(String)
    NotFishNANum = Column(String)
    NotFishNAPercent = Column(String)

class A3_1_4(Base):
    __tablename__ = 'A3_1_4'
    CountryCode = Column(String, primary_key=True)
    MeasureNo = Column(String)
    MeasureDev = Column(String)
    MeasureImp = Column(String)
    MeasureDontKnow = Column(String)
    MontitorNo = Column(String)
    MontitorDev = Column(String)
    MontitorImp = Column(String)
    MontitorDontKnow = Column(String)
    Average = Column(String)

class A3_1_5(Base):
    __tablename__ = 'A3_1_5'
    CountryCode = Column(String, primary_key=True)
    NoPlan = Column(String)
    InDev = Column(String)
    Adopted = Column(String)
    DontKnow = Column(String)
    Link = Column(String)

class A3_2_Phospate(Base):
    __tablename__ = 'A3_2_Phospate'
    CountryCode = Column(String, primary_key=True)
    Region = Column(String)
    Decrease = Column(String)
    NoTrend = Column(String)
    Increase = Column(String)
    Total = Column(String)
    DataLink = Column(String)
    CountryRegion = Column(String)

class A3_2_Nitrogen(Base):
    __tablename__ = 'A3_2_Nitrogen'
    CountryCode = Column(String, primary_key=True)
    Region = Column(String)
    Decrease = Column(String)
    NoTrend = Column(String)
    Increase = Column(String)
    Total = Column(String)
    DataLink = Column(String)
    CountryRegion = Column(String)

class A3_2_BathingWater(Base):
    __tablename__ = 'A3_2_BathingWater'
    CountryCode = Column(String, primary_key=True)
    Guide2006 = Column(String)
    Guide2007 = Column(String)
    Guide2008 = Column(String)
    Mandatory2006 = Column(String)
    Mandtory2007 = Column(String)
    Mandtory2008 = Column(String)
    DataLink = Column(String)

class A3_4(Base):
    __tablename__ = 'A3_4'
    CountryCode = Column(String, primary_key=True)
    Ax12007MS = Column(String)
    Ax12007EC = Column(String)
    Ax12007MSTotal = Column(String)
    Ax22007MS = Column(String)
    Ax22007EC = Column(String)
    Ax22007MSTotal = Column(String)
    Ax32007MS = Column(String)
    Ax32007EC = Column(String)
    Ax32007MSTotal = Column(String)
    Ax42007MS = Column(String)
    Ax42007EC = Column(String)
    Ax42007MSTotal = Column(String)
    Total2007MS = Column(String)
    Total2007EC = Column(String)
    Total2007MSTotal = Column(String)
    Axis1 = Column(String)
    Axis2 = Column(String)
    Axis3 = Column(String)
    Axis4 = Column(String)

class A3_5(Base):
    __tablename__ = 'A3_5'
    CountryCode = Column(String, primary_key=True)
    WithinLimit = Column(String)
    OutsideLimit = Column(String)

class A3_5_1(Base):
    __tablename__ = 'A3_5_1'
    CountryCode = Column(String, primary_key=True)
    vessels2006 = Column(String)
    Infringe2006 = Column(String)
    InfringePercent2006 = Column(String)
    Penalties2006 = Column(String)
    AveFine2006 = Column(String)
    MaxFine2006 = Column(String)
    vessels2007 = Column(String)
    Infringe2007 = Column(String)
    InfringePercent2007 = Column(String)
    Penalties2007 = Column(String)
    AveFine2007 = Column(String)
    MaxFine2007 = Column(String)

class A3_5_2(Base):
    __tablename__ = 'A3_5_2'
    CountryCode = Column(String, primary_key=True)
    SalmonPlan = Column(String)
    SalmonLink = Column(String)
    TroutPlan = Column(String)
    TroutLink = Column(String)
    SturgeonPlan = Column(String)
    SturgeonLink = Column(String)
    EelPlan = Column(String)
    EelLink = Column(String)
    OtherDesc = Column(String)
    OtherPlan = Column(String)
    OtherLink = Column(String)
    Habitat = Column(String)
    HabitatDetail = Column(String)
    Barriers = Column(String)
    BarriersDetail = Column(String)
    Stock = Column(String)
    StockDetail = Column(String)
    DiaOtherDesc = Column(String)
    DiaOther = Column(String)
    DiaOtherDetail = Column(String)

class A3_5_3(Base):
    __tablename__ = 'A3_5_3'
    CountryCode = Column(String, primary_key=True)
    Vessel1999 = Column(String)
    Vessel2004 = Column(String)
    Vessel2006 = Column(String)
    Vessel2007 = Column(String)
    Tonnage1999 = Column(String)
    Tonnage2004 = Column(String)
    Tonnage2006 = Column(String)
    Tonnage2007 = Column(String)
    Power1999 = Column(String)
    Power2004 = Column(String)
    Power2006 = Column(String)
    Power2007 = Column(String)

class A3_6_1(Base):
    __tablename__ = 'A3_6_1'
    CountryCode = Column(String, primary_key=True)
    vessel2006 = Column(String)
    Breaches2006 = Column(String)
    Penalties2006 = Column(String)
    AveFine2006 = Column(String)
    vessel2007 = Column(String)
    Breaches2007 = Column(String)
    Penalties2007 = Column(String)
    AveFine2007 = Column(String)
    MSActions = Column(String)

class A3_6_2(Base):
    __tablename__ = 'A3_6_2'
    CountryCode = Column(String, primary_key=True)
    SharkMonitor = Column(String)
    SharkYear1 = Column(String)
    SharkNumYears = Column(String)
    SeabirdsMonitor = Column(String)
    SeabirdsYear1 = Column(String)
    SeabirdsNumYears = Column(String)
    Links = Column(String)

class A3_6_3_Inshore(Base):
    __tablename__ = 'A3_6_3_Inshore'
    CountryCode = Column(String, primary_key=True)
    Measures = Column(String)
    Number = Column(String)

class A3_6_3_Offshore(Base):
    __tablename__ = 'A3_6_3_Offshore'
    CountryCode = Column(String, primary_key=True)
    AllSites = Column(String)
    Requests = Column(String)
    Number = Column(String)

class A3_7_1(Base):
    __tablename__ = 'A3_7_1'
    CountryCode = Column(String, primary_key=True)
    DCF = Column(String)

class A4(Base):
    __tablename__ = 'A4'
    CountryCode = Column(String, primary_key=True)
    spending = Column(String)

class A4_3(Base):
    __tablename__ = 'A4_3'
    CountryCode = Column(String, primary_key=True)
    Planing = Column(String)
    LawPost2006 = Column(String)
    Monitor = Column(String)
    MonitorReports = Column(String)
    Coordination = Column(String)
    EcoNetwork = Column(String)

class A4_4_1(Base):
    __tablename__ = 'A4_4_1'
    CountryCode = Column(String, primary_key=True)
    TourismGuide = Column(String)
    Plan = Column(String)
    Legal = Column(String)
    Reporting = Column(String)

class A4_5_1(Base):
    __tablename__ = 'A4_5_1'
    CountryCode = Column(String, primary_key=True)
    OutermostRegion = Column(String)
    Minimised = Column(String)
    Compensated = Column(String)
    Measures = Column(String)

class A5_1_AlienLegal(Base):
    __tablename__ = 'A5_1_AlienLegal'
    CountryCode = Column(String, primary_key=True)
    General = Column(String)
    GenralDetail = Column(String)
    Specific = Column(String)
    SpecificDetail = Column(String)
    Import = Column(String)
    Trade = Column(String)
    Intro = Column(String)
    Control = Column(String)

class A5_1_AlienSpecies(Base):
    __tablename__ = 'A5_1_AlienSpecies'
    CountryCode = Column(String, primary_key=True)
    TotalAlien = Column(String)
    Num1000km = Column(String)

class A5_1_2(Base):
    __tablename__ = 'A5_1_2'
    CountryCode = Column(String, primary_key=True)
    StrategyNo = Column(String)
    StrategyDev = Column(String)
    StrategyImp = Column(String)
    StrategyDontKnow = Column(String)
    ActionNo = Column(String)
    ActionDev = Column(String)
    ActionImp = Column(String)
    ActionDontKnow = Column(String)
    OtherDesc = Column(String)
    OtherNo = Column(String)
    OtherDev = Column(String)
    OtherImp = Column(String)
    OtherDontKnow = Column(String)
    IASStrategy = Column(String)
    IASStrategyDetails = Column(String)
    IASAction = Column(String)
    IASActionDetails = Column(String)

class A5_1_3(Base):
    __tablename__ = 'A5_1_3'
    CountryCode = Column(String, primary_key=True)
    Ballast = Column(String)

class A5_1_4(Base):
    __tablename__ = 'A5_1_4'
    CountryCode = Column(String, primary_key=True)
    DatabaseNo = Column(String)
    DatabaseDev = Column(String)
    DatabaseImp = Column(String)
    DatabaseDontKnow = Column(String)
    EarlyWarnNo = Column(String)
    EarlyWarnDev = Column(String)
    EarlyWarnImp = Column(String)
    EarlyWarnDontKnow = Column(String)
    Rapid = Column(String)
    Incident = Column(String)
    Focal = Column(String)
    Coordination = Column(String)

class A5_2_2(Base):
    __tablename__ = 'A5_2_2'
    CountryCode = Column(String, primary_key=True)
    GMlegalNo = Column(String)
    GMlegalDev = Column(String)
    GMlegalImp = Column(String)

class A6_1_1(Base):
    __tablename__ = 'A6_1_1'
    CountryCode = Column(String, primary_key=True)
    NationalReport4 = Column(String)
    NBSAP = Column(String)
    NBSAPData = Column(String)
    CBDYear = Column(String)
    CBDAmount = Column(String)
    CMSYear = Column(String)
    CMSAmount = Column(String)
    AEWAYear = Column(String)
    AEWAAmount = Column(String)
    RamsarYear = Column(String)
    RamsarAmount = Column(String)
    WHCYear = Column(String)
    WHCAmount = Column(String)
    ConventionData = Column(String)

class A7_1(Base):
    __tablename__ = 'A7_1'
    CountryCode = Column(String, primary_key=True)
    Aid2006 = Column(String)
    Aid2007 = Column(String)
    Aid2008 = Column(String)
    Percent2006 = Column(String)
    Percent2007 = Column(String)
    Percent2008 = Column(String)


class A7_1_3(Base):
    __tablename__ = 'A7_1_3'
    CountryCode = Column(String, primary_key=True)
    BiAid2006 = Column(String)
    BiAid2007 = Column(String)
    BiAid2008 = Column(String)
    BiPercent2006 = Column(String)
    BiPercent2007 = Column(String)
    BiPercent2008 = Column(String)


class A7_1_4(Base):
    __tablename__ = 'A7_1_4'
    CountryCode = Column(String, primary_key=True)
    Total3rd = Column(String)
    Total4th = Column(String)
    Total5th = Column(String)
    Percent3rd = Column(String)
    Percent4th = Column(String)
    Percent5th = Column(String)

class A7_1_6(Base):
    __tablename__ = 'A7_1_6'
    CountryCode = Column(String, primary_key=True)
    Aid2006 = Column(String)
    Aid2007 = Column(String)
    Aid2008 = Column(String)
    Percent2006 = Column(String)
    Percent2007 = Column(String)
    Percent2008 = Column(String)
    OCT = Column(String)
    Value = Column(String)
    Objectives = Column(String)

class A7_2_2(Base):
    __tablename__ = 'A7_2_2'
    CountryCode = Column(String, primary_key=True)
    MandatorySEA_EIA = Column(String)

class A7_2_5(Base):
    __tablename__ = 'A7_2_5'
    CountryCode = Column(String, primary_key=True)
    OCTMandatorySEA_EIA = Column(String)

class A8_1(Base):
    __tablename__ = 'A8_1'
    CountryCode = Column(String, primary_key=True)
    A8_1_3Imp = Column(String)
    A8_1_3Partial = Column(String)
    A8_1_3Not = Column(String)
    A8_1_4Imp = Column(String)
    A8_1_4Partial = Column(String)
    A8_1_4Not = Column(String)
    A8_1_8Imp = Column(String)
    A8_1_8Partial = Column(String)
    A8_1_8Not = Column(String)

class A8_1_3_BenefitShare(Base):
    __tablename__ = 'A8_1_3_BenefitShare'
    CountryCode = Column(String, primary_key=True)
    Legal = Column(String)
    Aware = Column(String)

class A8_1_3_CBD(Base):
    __tablename__ = 'A8_1_3_CBD'
    CountryCode = Column(String, primary_key=True)
    Y2006 = Column(String)
    Y2007 = Column(String)
    Y2008 = Column(String)
    Y2009 = Column(String)

class A8_1_3_GeneticResource(Base):
    __tablename__ = 'A8_1_3_GeneticResource'
    CountryCode = Column(String, primary_key=True)
    Legal = Column(String)
    Aware = Column(String)

class A8_1_4(Base):
    __tablename__ = 'A8_1_4'
    CountryCode = Column(String, primary_key=True)
    Y2006 = Column(String)
    Y2007 = Column(String)
    Y2008 = Column(String)
    Y2009 = Column(String)

class A8_1_8(Base):
    __tablename__ = 'A8_1_8'
    CountryCode = Column(String, primary_key=True)
    ImportApps = Column(String)
    ImportAppsDenied = Column(String)
    ImportPercent = Column(String)
    ExportApps = Column(String)
    ExportAppsDenied = Column(String)
    ExportPercent = Column(String)
    ReExportApps = Column(String)
    ReExportAppsDenied = Column(String)
    ReExportPercent = Column(String)
    SeizeP1Year = Column(String)
    SeizeP1Num = Column(String)
    SeizeP2Year = Column(String)
    SeizeP2Num = Column(String)
    NetChange = Column(String)
    Capacity = Column(String)
    Finance = Column(String)
    CITESDataLink = Column(String)
    Contributions = Column(String)
    Amount = Column(String)
    CITES_COPDataLink = Column(String)

class A9_1_1(Base):
    __tablename__ = 'A9_1_1'
    CountryCode = Column(String, primary_key=True)
    GHG2006 = Column(String)
    GHG2007 = Column(String)
    GHG2008 = Column(String)
    Change2006 = Column(String)
    Change2007 = Column(String)
    Change2008 = Column(String)

class A9_3_2(Base):
    __tablename__ = 'A9_3_2'
    CountryCode = Column(String, primary_key=True)
    PlanNo = Column(String)
    PlanDev = Column(String)
    PlanImp = Column(String)
    PlanDontKnow = Column(String)
    NREAPNo = Column(String)
    NREAPDev = Column(String)
    NREAPImp = Column(String)
    NREAPDontKnow = Column(String)
    Round = Column(String)
    NatCert = Column(String)
    OtherDesc = Column(String)
    OtherNat = Column(String)
    Require = Column(String)
    RequireDetail = Column(String)

class A9_4_1(Base):
    __tablename__ = 'A9_4_1'
    CountryCode = Column(String, primary_key=True)
    StratNo = Column(String)
    StratDev = Column(String)
    StratImp = Column(String)
    StratDontKnow = Column(String)
    PlanNo = Column(String)
    PlanDev = Column(String)
    PlanImp = Column(String)
    PlanDontKnow = Column(String)
    OtherDesc = Column(String)
    OtherNo = Column(String)
    OtherDev = Column(String)
    OtherImp = Column(String)
    OtherDontKnow = Column(String)
    AdaptStratYN = Column(String)
    AdaptStratDetail = Column(String)
    AdaptPlanYN = Column(String)
    AdaptPlanDetail = Column(String)
    BioStratYN = Column(String)
    BioStratDetail = Column(String)
    BioPlanYN = Column(String)
    BioPlanDetail = Column(String)
    ProjectsYN = Column(String)
    ProjectsDetail = Column(String)

class A9_4_3(Base):
    __tablename__ = 'A9_4_3'
    CountryCode = Column(String, primary_key=True)
    StudiesYN = Column(String)
    StudiesDetail = Column(String)
    HabitatYN = Column(String)
    HabitatDetail = Column(String)
    SpeciesYN = Column(String)
    SpeciesDetail = Column(String)

class A10_1(Base):
    __tablename__ = 'A10_1'
    CountryCode = Column(String, primary_key=True)
    Programme = Column(String)
    ProgrammeDetail = Column(String)
    Research = Column(String)
    ResearchDetail = Column(String)

class A10_1_2(Base):
    __tablename__ = 'A10_1_2'
    CountryCode = Column(String, primary_key=True)
    NatFollow = Column(String)
    WideFollow = Column(String)
    FollowDetails = Column(String)
    Local = Column(String)
    SubNat = Column(String)
    Nat = Column(String)
    Stakeholder = Column(String)
    Valuation = Column(String)
    CaseStudies = Column(String)
    Access = Column(String)
    Standards = Column(String)
    MAInPlans = Column(String)
    ValuationUsed = Column(String)

class A10_1_8(Base):
    __tablename__ = 'A10_1_8'
    CountryCode = Column(String, primary_key=True)
    Platform = Column(String)
    PlatfromUpdated = Column(String)
    PlatfromDevPlans = Column(String)
    PlatfromLink = Column(String)

class A10_1_9(Base):
    __tablename__ = 'A10_1_9'
    CountryCode = Column(String, primary_key=True)
    MoU = Column(String)
    Associate = Column(String)
    NonMember = Column(String)
    GBIFDetails = Column(String)
    GBIFLink = Column(String)
    Gov = Column(String)
    Public = Column(String)
    NotMember = Column(String)
    ENBIDetails = Column(String)

class B1_1_1(Base):
    __tablename__ = 'B1_1_1'
    CountryCode = Column(String, primary_key=True)
    NatProg = Column(String)
    NatProgDetails = Column(String)
    NatProgData = Column(String)
    Mange2004 = Column(String)
    Restore2004 = Column(String)
    Other2004 = Column(String)
    Mange2005 = Column(String)
    Restore2005 = Column(String)
    Other2005 = Column(String)
    Mange2006 = Column(String)
    Restore2006 = Column(String)
    Other2006 = Column(String)
    Mange2007 = Column(String)
    Restore2007 = Column(String)
    Other2007 = Column(String)
    Mange2008 = Column(String)
    Restore2008 = Column(String)
    Other2008 = Column(String)

class B1_1_4(Base):
    __tablename__ = 'B1_1_4'
    CountryCode = Column(String, primary_key=True)
    Cat51_2006 = Column(String)
    Cat51_2007 = Column(String)
    Cat51_2008 = Column(String)
    Cat51_2009 = Column(String)
    Cat55_2006 = Column(String)
    Cat55_2007 = Column(String)
    Cat55_2008 = Column(String)
    Cat55_2009 = Column(String)
    Cat56_2006 = Column(String)
    Cat56_2007 = Column(String)
    Cat56_2008 = Column(String)
    Cat56_2009 = Column(String)

class B1_1_8(Base):
    __tablename__ = 'B1_1_8'
    CountryCode = Column(String, primary_key=True)
    Y2006 = Column(String)
    Y2007 = Column(String)
    Y2008 = Column(String)
    Y2009 = Column(String)

class B2_4(Base):
    __tablename__ = 'B2_4'
    CountryCode = Column(String, primary_key=True)
    New = Column(String)
    Existing = Column(String)
    Develope = Column(String)
    NoNew = Column(String)
    Details = Column(String)

class B3_1_2(Base):
    __tablename__ = 'B3_1_2'
    CountryCode = Column(String, primary_key=True)
    Local = Column(String)
    Regional = Column(String)
    National = Column(String)

class B3_1_5(Base):
    __tablename__ = 'B3_1_5'
    CountryCode = Column(String, primary_key=True)
    Local = Column(String)
    Regional = Column(String)
    National = Column(String)

class B3_1_6(Base):
    __tablename__ = 'B3_1_6'
    CountryCode = Column(String, primary_key=True)
    Y2006 = Column(String)
    Y2007 = Column(String)
    Y2008 = Column(String)
    Y2009 = Column(String)

class B3_1_7(Base):
    __tablename__ = 'B3_1_7'
    CountryCode = Column(String, primary_key=True)
    Y2006 = Column(String)
    Y2007 = Column(String)
    Y2008 = Column(String)
    Y2009 = Column(String)

class B3_1_8(Base):
    __tablename__ = 'B3_1_8'
    CountryCode = Column(String, primary_key=True)
    EU = Column(String)
    NonEU = Column(String)

class B4_1_1(Base):
    __tablename__ = 'B4_1_1'
    CountryCode = Column(String, primary_key=True)
    Yes = Column(String)
    No = Column(String)
    Dev = Column(String)
    NotYet = Column(String)
    Partially = Column(String)
    Fully = Column(String)

class B4_1_2(Base):
    __tablename__ = 'B4_1_2'
    CountryCode = Column(String, primary_key=True)
    Y2006 = Column(String)
    Y2007 = Column(String)
    Y2008 = Column(String)
    Declaration = Column(String)

class C1_2(Base):
    __tablename__ = 'C1_2'
    CountryCode = Column(String, primary_key=True)
    SEBI = Column(String)

class C1_2_1(Base):
    __tablename__ = 'C1_2_1'
    CountryCode = Column(String, primary_key=True)
    Abundance = Column(String)
    RedList = Column(String)
    Species = Column(String)
    Ecosystem = Column(String)
    Habitat = Column(String)
    Livestock = Column(String)
    Areas = Column(String)
    BirdSites = Column(String)
    Nitrogen = Column(String)
    Aliens = Column(String)
    BirdClimate = Column(String)
    MarineTrophic = Column(String)
    FragArea = Column(String)
    FragRicer = Column(String)
    NutrientCostal = Column(String)
    FWQuality = Column(String)
    ForestGrow = Column(String)
    ForestDead = Column(String)
    AgriNitro = Column(String)
    AgriAreas = Column(String)
    Fisheries = Column(String)
    Aquaculture = Column(String)
    Footprint = Column(String)
    Patent = Column(String)
    Finance = Column(String)
    Public = Column(String)
    Additional = Column(String)

class C1_3_1(Base):
    __tablename__ = 'C1_3_1'
    CountryCode = Column(String, primary_key=True)
    Costal = Column(String)
    Dunes = Column(String)
    FWHabitats = Column(String)
    Heath = Column(String)
    Scrub = Column(String)
    Grass = Column(String)
    Bogs = Column(String)
    Rocky = Column(String)
    Forest = Column(String)
    HabitatOther = Column(String)
    Birds = Column(String)
    Mammals = Column(String)
    Amphibians = Column(String)
    Fish = Column(String)
    Inverts = Column(String)
    Plants = Column(String)
    SpeciesOther = Column(String)
    CostalDetail = Column(String)
    DunesDetail = Column(String)
    FWHabitatsDetail = Column(String)
    HeathDetail = Column(String)
    ScrubDetail = Column(String)
    GrassDetail = Column(String)
    BogsDetail = Column(String)
    RockyDetail = Column(String)
    ForestDetail = Column(String)
    HabitatOtherDetail = Column(String)
    BirdsDetail = Column(String)
    MammalsDetail = Column(String)
    AmphibiansDetail = Column(String)
    FishDetail = Column(String)
    InvertsDetail = Column(String)
    PlantsDetail = Column(String)
    SpeciesOtherDetail = Column(String)


