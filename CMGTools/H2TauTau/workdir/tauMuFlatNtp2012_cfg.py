#from PhysicsTools.PatAlgos.patTemplate_cfg import *
import FWCore.ParameterSet.Config as cms
import os

process = cms.Process("FLATNTP")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.maxLuminosityBlocks = cms.untracked.PSet(input = cms.untracked.int32(-1))
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )
evReportFreq = 100

#####################Define the sample to process
sampleName = os.environ['SAMPLENAME']
sampleJobIdx = int(os.environ['SAMPLEJOBIDX'])
print "sampleName: "
print sampleName
print "sampleJobIdx: "
print sampleJobIdx

process.load('CMGTools.H2TauTau.tools.joseFlatNtpSample_cfi')
from CMGTools.H2TauTau.tools.joseFlatNtpSample_cff import *
configureFlatNtpSample(process.flatNtp,sampleName,year='2012')

dataset_user = 'benitezj'
sampleTag = "/PATCMG_TEST52/H2TAUTAU_TEST52"
inputfiles = "tauMu_fullsel_tree_CMG_.*root"



#########################
dataset_name = process.flatNtp.path.value() + sampleTag
firstfile = sampleJobIdx * 5
lastfile = (sampleJobIdx + 1 )*5

print dataset_user
print dataset_name
print inputfiles
print firstfile
print lastfile

#get input files
from CMGTools.Production.datasetToSource import *
process.source = datasetToSource( dataset_user, dataset_name, inputfiles)
process.source.fileNames = process.source.fileNames[firstfile:lastfile]
print process.source.fileNames

##
process.analysis = cms.Path(process.flatNtp) 
process.schedule = cms.Schedule(process.analysis)
process.TFileService = cms.Service("TFileService", fileName = cms.string("flatNtp.root"))


#####################################################
process.MessageLogger = cms.Service("MessageLogger",
    cerr = cms.untracked.PSet(
    FwkReport = cms.untracked.PSet(
    
    reportEvery = cms.untracked.int32(evReportFreq),

    optionalPSet = cms.untracked.bool(True),
    limit = cms.untracked.int32(10000000)
    ),
    optionalPSet = cms.untracked.bool(True),
    FwkJob = cms.untracked.PSet(
    optionalPSet = cms.untracked.bool(True),
    limit = cms.untracked.int32(0)
    ),    
    )
)

#process.source.duplicateCheckMode = cms.untracked.string("noDuplicateCheck")
#print process.dumpPython()
