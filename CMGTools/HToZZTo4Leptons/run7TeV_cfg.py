import copy
import os 
import CMGTools.RootTools.fwlite.Config as cfg


from CMGTools.HToZZTo4Leptons.setup.EffectiveAreas import effectiveAreas2011 as effectiveAreas
from CMGTools.HToZZTo4Leptons.setup.FSR import FSRConfig as fsr
from CMGTools.HToZZTo4Leptons.setup.FakeRates import *



period = 'Period_2011AB'
channel = 'mu_mu'



mc_vertexWeight = None
if period == 'Period_2011A':
    mc_vertexWeight = 'vertexWeightFall112invfb'
elif period == 'Period_2011B':
    mc_vertexWeight = 'vertexWeightFall112011B'
elif period == 'Period_2011AB':
    mc_vertexWeight = 'vertexWeightFall112011AB'

###GEN LEVEL SELECTORS
muMuGenSel = cfg.Analyzer(
    'HZZGenSelector_MuMu',
    col_label = 'genParticlesPruned',
    channel = 'mu-mu'
    )
muEleGenSel = cfg.Analyzer(
    'HZZGenSelector_EMu',
    col_label = 'genParticlesPruned',
    channel = 'mu-ele'
    )

eleEleGenSel = cfg.Analyzer(
    'HZZGenSelector_EE',
    col_label = 'genParticlesPruned',
    channel = 'ele-ele'
    )


#Trigger Information
triggerAna = cfg.Analyzer(
    'TriggerAnalyzer'
    )

#Vertex information
vertexAna = cfg.Analyzer(
    'VertexAnalyzer',
    vertexWeight = mc_vertexWeight,
    skimGoodVertex=True,
    verbose = False
    )


#Analyzers
muMuAna = cfg.Analyzer(
    'MuMuFourLeptonAnalyzer',
    minPt1=5,
    maxEta1=2.4,
    minPt2=5,
    maxEta2=2.4,
    z1_m = (40.,120.),
    z2_m = (4.,120.),
    z1_pt1 = 20,
    z1_pt2 = 10,
    minHMass=100.,
    minHMassZ2=12.,
    minMass=4.,
    PF=True,
    keep=False,
    effectiveAreas=effectiveAreas,
    fakeRates=fakeRates2011,
#    FSR=fsr
    )


muEleAna = copy.deepcopy( muMuAna)
muEleAna.name = 'MuEleFourLeptonAnalyzer'
muEleAna.minPt1 = 5
muEleAna.maxEta1 = 2.4
muEleAna.minPt2 = 7
muEleAna.maxEta2 = 2.5


eleEleAna = copy.deepcopy( muEleAna )
eleEleAna.name = 'EleEleFourLeptonAnalyzer'
eleEleAna.minPt1 = 7
eleEleAna.maxEta1 = 2.5
eleEleAna.minPt2 = 7
eleEleAna.maxEta2 = 2.5


#GenLevelAnalyzers
muMuGenAna = copy.deepcopy(muMuAna)
muMuGenAna.name = 'GenGenFourLeptonAnalyzer_MuMu'
muMuGenAna.pdgId1 = 13
muMuGenAna.pdgId2 = 13

muEleGenAna = copy.deepcopy(muEleAna)
muEleGenAna.name = 'GenGenFourLeptonAnalyzer_MuEle'
muEleGenAna.pdgId1 = 13
muEleGenAna.pdgId2 = 11

eleEleGenAna = copy.deepcopy(eleEleAna)
eleEleGenAna.name = 'GenGenFourLeptonAnalyzer_EleEle'
eleEleGenAna.pdgId1 = 11
eleEleGenAna.pdgId2 = 11




def createTreeProducer( ana ):
    tp = cfg.Analyzer( '_'.join( ['FourLeptonTreeProducer',ana.name] ),
                       anaName = ana.name,
                       effectiveAreas=effectiveAreas
                       )
    return tp


####################################################################################

from CMGTools.HToZZTo4Leptons.samples.samples_7TeV import * 

####################################################################################


jsonFilter = cfg.Analyzer(
    'JSONAnalyzer'
    )

selectedSamples=[]

for comp in mcSamples:
    comp.isMC = True
    comp.splitFactor = 10
#DYJets.splitFactor = 300
#DYJetsLowMass.splitFactor = 100




for comp in dataSamplesMu:
    comp.splitFactor = 100
    
for comp in dataSamplesE:
    comp.splitFactor = 100
    
theAna = None
if channel == 'mu_mu':
    theGenSel = muMuGenSel
    theAna = muMuAna
    theGenAna = muMuGenAna
    for data in dataSamplesMu:
        data.triggers = triggers_mumu
    for mc in mcSamples:
        mc.triggers = triggers_mumu
    selectedComponents=mcSamples+dataSamplesMu
    
elif channel == 'mu_ele':
    theGenSel = muEleGenSel
    theAna = muEleAna
    theGenAna = muEleGenAna

    for data in dataSamplesMu:
        data.triggers = triggers_mumu
    for data in dataSamplesE:
        data.triggers = triggers_ee
        data.vetoTriggers = triggers_mumu
    for mc in mcSamples:
        mc.triggers = triggers_mue
    selectedComponents=mcSamples+dataSamplesMu+dataSamplesE



elif channel == 'ele_ele':
    theGenSel = eleEleGenSel
    theAna = eleEleAna
    theGenAna = eleEleGenAna
    for data in dataSamplesE:
        data.triggers = triggers_ee
    for mc in mcSamples:
        mc.triggers = triggers_ee
    selectedComponents=mcSamples+dataSamplesE

#Define Sequences for data and MC

mcSequence = [
   theGenSel,    #uncomment to preselect events in gen level 
    triggerAna,
    vertexAna,
    theGenAna,
    theAna,
    createTreeProducer( theAna ),
    createTreeProducer( theGenAna )
    ]

dataSequence=[
    jsonFilter,
    triggerAna,
    vertexAna,
    theAna,
    createTreeProducer( theAna )
    ]



#for full production use data sequence
sequence = cfg.Sequence(dataSequence)





test = 1
if test==1:
    dataset = GGH130
    selectedComponents = [dataset]
    dataset.splitFactor = 1
    dataset.files = dataset.files[:10]

   
if test ==2:
    selectedComponents=selectedComponents[:1]
    print selectedComponents
    for comp in selectedComponents:
        comp.splitFactor = 1
        comp.files = comp.files[:10]

if test ==3:
    selectedComponents=selectedComponents[-1:]
    print selectedComponents
    for comp in selectedComponents:
        comp.splitFactor = 1
        comp.files = comp.files[:10]



    
config = cfg.Config( components = selectedComponents,
                     sequence = sequence )
