#-----------------------------------------
#
#Producer controller
#
#-----------------------------------------
import os, re
PyFilePath = os.environ['CMSSW_BASE']+"/src/LLRHiggsTauTau/NtupleProducer/"

#samples list (it could be moved to a cfg file for better reading
#samples = [
#]
#apply corrections?
APPLYMUCORR=False
APPLYELECORR=True
APPLYFSR=False #this is by far the slowest module (not counting SVFit so far)
#Cuts on the Objects (add more cuts with &&)
#MUCUT="(isGlobalMuon || (isTrackerMuon && numberOfMatches>0)) && abs(eta)<2.4 && pt>8"
#ELECUT="abs(eta)<2.5 && gsfTrack.trackerExpectedHitsInner.numberOfHits<=1 && pt>10"
#TAUCUT="pt>15"
#JETCUT="pt>15"

USEPAIRMET=False # input to SVfit: true: MVA pair MET; false: PFmet (HF inclusion set using USE_NOHFMET)
APPLYMETCORR=False # flag to enable (True) and disable (False) Z-recoil corrections for MVA MET response and resolution
USE_NOHFMET = False # True to exclude HF and run on silver json


SVFITBYPASS=False # use SVFitBypass module, no SVfit computation, adds dummy userfloats for MET and SVfit mass
USECLASSICSVFIT=True # if True use the ClassicSVfit package, if False use the SVFitStandAlone package

BUILDONLYOS=False #If true don't create the collection of SS candidates (and thus don't run SV fit on them)
APPLYTESCORRECTION=True # shift the central value of the tau energy scale before computing up/down variations
COMPUTEUPDOWNSVFIT=True # compute SVfit for up/down TES variation
COMPUTEMETUPDOWNSVFIT=True # compute SVfit for up/down MET JES variation
doCPVariables=False # compute CP variables and PV refit
COMPUTEQGVAR = False # compute QG Tagger for jets
IsMC=True
Is25ns=True
HLTProcessName='HLT' #Different names possible, check e.g. at https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMiniAOD.
if not IsMC:
    HLTProcessName='HLT' #It always 'HLT' for real data
print "HLTProcessName: ",HLTProcessName

#relaxed sets for testing purposes
TAUDISCRIMINATOR="byIsolationMVA3oldDMwoLTraw"
PVERTEXCUT="!isFake && ndof > 4 && abs(z) <= 24 && position.Rho <= 2" #cut on good primary vertexes
MUCUT="isLooseMuon && pt>10"#"isLooseMuon && pt>5"
ELECUT="pt>10"#"pt>7"#"gsfTracsk.hitPattern().numberOfHits(HitPattern::MISSING_INNER_HITS)<=1 && pt>10"
TAUCUT="pt>20"#"tauID('byCombinedIsolationDeltaBetaCorrRaw3Hits') < 1000.0 && pt>18" #miniAOD tau from hpsPFTauProducer have pt>18 and decaymodefinding ID
JETCUT="pt>0" # was 10, is now 0 to save all the jets and be able to copute JEC MET in KLUB
LLCUT="mass>-99999"
BCUT="pt>5"

# ------------------------
DO_ENRICHED=False # do True by default, both ntuples and enriched outputs are saved!
STORE_ENRICHEMENT_ONLY=True # When True and DO_ENRICHED=True only collection additional to MiniAOD standard are stored. They can be used to reproduce ntuples when used together with oryginal MiniAOD with two-file-solution
# ------------------------

is92X = True if 'CMSSW_9' in os.environ['CMSSW_VERSION'] else False# True to run in 92X (2017), False to run in 80X (2016) or 76X (2015)
print "is92X: " , is92X
is80X = True if 'CMSSW_8' in os.environ['CMSSW_VERSION'] else False# True to run in 80X (2016), False to run in 76X (2015)
print "is80X: " , is80X

##
## Standard sequence
##

if is92X:
    #execfile(PyFilePath+"python/HiggsTauTauProducer_92X.py")
    execfile(PyFilePath+"python/HiggsTauTauProducer_94X.py")
elif is80X:
    execfile(PyFilePath+"python/HiggsTauTauProducer_80X.py")
else :
    execfile(PyFilePath+"python/HiggsTauTauProducer.py")

### ----------------------------------------------------------------------
### Source, better to use sample to run on batch
### ----------------------------------------------------------------------
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
    # '/store/mc/RunIISpring16MiniAODv2/SMS-TChiHH_HToBB_HToTauTau_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/PUSpring16Fast_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/00000/B8A61C30-5E12-E711-87BB-FA163E939724.root',
    #'/store/mc/RunIISpring16MiniAODv2/SMS-TChiHH_HToBB_HToTauTau_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/PUSpring16Fast_80X_mcRun2_asymptotic_2016_miniAODv2_v0-v1/00000/0264645E-5E12-E711-889B-E41D2D08DD10.root',
    # '/store/mc/RunIISummer16MiniAODv2/DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v2/60000/4CBBCFDF-F8C6-E611-A5C2-6CC2173BBD40.root',
    # '/store/mc/RunIISummer16MiniAODv2/TT_TuneCUETP8M2T4_13TeV-powheg-pythia8/MINIAODSIM/PUMoriond17_backup_80X_mcRun2_asymptotic_2016_TrancheIV_v6-v1/00000/AC8AA010-88BB-E611-9974-FA163E1B885B.root',
    #'/store/mc/RunIISummer16MiniAODv2/ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1/MINIAODSIM/PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v6_ext1-v1/80000/80EA9B8A-A1C1-E611-A107-20CF3027A61A.root',
    #'/store/data/Run2016B/SingleMuon/MINIAOD/23Sep2016-v3/120000/E6D5D5EB-8299-E611-83D1-FA163EB4F61D.root',
    ####'/store/data/Run2016C/SingleMuon/MINIAOD/23Sep2016-v1/80000/F8F49A79-BE89-E611-A029-008CFA1974E4.root'
    #'/store/data/Run2016B/SingleMuon/MINIAOD/PromptReco-v2/000/273/150/00000/34A57FB8-D819-E611-B0A4-02163E0144EE.root', #80X data
    # '/store/mc/RunIISpring16MiniAODv1/GluGluToBulkGravitonToHHTo2B2Tau_M-400_narrow_13TeV-madgraph/MINIAODSIM/PUSpring16RAWAODSIM_80X_mcRun2_asymptotic_2016_v3_ext1-v1/30000/06E22BEA-9F10-E611-9862-1CB72C0A3A5D.root', #80X MC
    # '/store/mc/RunIIFall15MiniAODv2/SUSYGluGluToHToTauTau_M-160_TuneCUETP8M1_13TeV-pythia8/MINIAODSIM/PU25nsData2015v1_76X_mcRun2_asymptotic_v12-v1/50000/12184969-3DB8-E511-879B-001E67504A65.root', #76X MC
    
    
    # 2017 Data
    # B_v1
    #'/store/data/Run2017B/SingleMuon/MINIAOD/PromptReco-v1/000/297/046/00000/32AC3177-7A56-E711-BE34-02163E019D73.root',
    #'/store/data/Run2017B/SingleElectron/MINIAOD/PromptReco-v1/000/297/046/00000/02CBE6D1-4456-E711-82F5-02163E019D97.root', # 5000   evts
    #'/store/data/Run2017B/SingleElectron/MINIAOD/PromptReco-v1/000/297/050/00000/166F7BB0-3C56-E711-BD8B-02163E0145C5.root',  # 147000 evts
    #'/store/data/Run2017B/Tau/MINIAOD/PromptReco-v1/000/297/046/00000/B600F102-4856-E711-839A-02163E01411B.root',
    # C_v3
    #'/store/data/Run2017C/SingleMuon/MINIAOD/PromptReco-v3/000/300/742/00000/0AC61DCE-457E-E711-9CAE-02163E014217.root',
    # root://cms-xrd-global.cern.ch//store/data/Run2017C/SingleMuon/MINIAOD/PromptReco-v3/000/300/742/00000/240BA088-597E-E711-ADE4-02163E019C30.root
    #'/store/data/Run2017C/SingleMuon/MINIAOD/PromptReco-v3/000/300/742/00000/240BA088-597E-E711-ADE4-02163E019C30.root',
    #'/store/data/Run2017C/SingleMuon/MINIAOD/PromptReco-v3/000/300/742/00000/425DFEF6-5D7E-E711-8F2F-02163E01A1DD.root',
    
    # MC 2017 - GT:92X_upgrade2017_realistic_v10
    #'/store/mc/RunIISummer17MiniAOD/VBFHToTauTau_M125_13TeV_powheg_pythia8/MINIAODSIM/NZSFlatPU28to62_HIG07_92X_upgrade2017_realistic_v10-v1/70000/0080A67C-FBA4-E711-A8FE-00259029E84C.root',
    #'/store/mc/RunIISummer17MiniAOD/VBFHToTauTau_M125_13TeV_powheg_pythia8/MINIAODSIM/NZSFlatPU28to62_HIG07_92X_upgrade2017_realistic_v10-v1/70000/0678C84B-F49E-E711-B561-A0369FC51AD4.root',
    #'/store/mc/RunIISummer17MiniAOD/VBFHToTauTau_M125_13TeV_powheg_pythia8/MINIAODSIM/NZSFlatPU28to62_HIG07_92X_upgrade2017_realistic_v10-v1/70000/088CC59F-F39C-E711-8124-549F35AF44E3.root',
    
    # 2017 embedded samples - GT: 92X_dataRun2_Prompt_v4
    #'/store/user/pahrens/gc_storage/MuTau_data_2017_CMSSW923p2_freiburg_v7/TauEmbedding_MuTau_data_2017_CMSSW923p2_Run2017B/merged/1/merged_0.root',    # 688 evts
    #'/store/user/pahrens/gc_storage/MuTau_data_2017_CMSSW923p2_freiburg_v7/TauEmbedding_MuTau_data_2017_CMSSW923p2_Run2017B/merged/1/merged_100.root',  # 715 evts
    #'/store/user/pahrens/gc_storage/MuTau_data_2017_CMSSW923p2_freiburg_v7/TauEmbedding_MuTau_data_2017_CMSSW923p2_Run2017B/merged/1/merged_1000.root', # 657 evts
    
    #'/store/mc/RunIISummer17MiniAOD/VBFHToTauTau_M125_13TeV_powheg_pythia8/MINIAODSIM/92X_upgrade2017_realistic_v10-v2/50000/02098EBB-029C-E711-8FED-441EA1714E4C.root'
    #'/store/mc/RunIISummer17MiniAOD/VBFHToTauTau_M125_13TeV_powheg_pythia8/MINIAODSIM/92X_upgrade2017_realistic_v10-v2/50000/2A50557C-829D-E711-9331-10983627C3CE.root',
    
    # Samples for SyncFeb2018
    # Signal
    #'/store/mc/RunIIFall17MiniAOD/GluGluToBulkGravitonToHHTo2B2Tau_M-450_narrow_13TeV-madgraph/MINIAODSIM/94X_mc2017_realistic_v10-v1/40000/128F2EAF-6905-E811-810E-44A842BECCD8.root',
    #'/store/mc/RunIIFall17MiniAOD/GluGluToBulkGravitonToHHTo2B2Tau_M-450_narrow_13TeV-madgraph/MINIAODSIM/94X_mc2017_realistic_v10-v1/40000/F89C5A80-6905-E811-9A3F-FA163ED3ED08.root',
    #'/store/mc/RunIIFall17MiniAOD/GluGluToBulkGravitonToHHTo2B2Tau_M-450_narrow_13TeV-madgraph/MINIAODSIM/94X_mc2017_realistic_v10-v1/40000/34715D6D-6905-E811-9843-44A842CFD5BE.root',
    # miniAOD_v2
    #'/store/mc/RunIIFall17MiniAODv2/GluGluToBulkGravitonToHHTo2B2Tau_M-450_narrow_13TeV-madgraph/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/90000/1CA54262-F442-E811-8262-0CC47A4D7694.root',
    #'/store/mc/RunIIFall17MiniAODv2/GluGluToBulkGravitonToHHTo2B2Tau_M-450_narrow_13TeV-madgraph/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/90000/5ED78A31-7243-E811-8053-484D7E8DF09F.root',
    #'/store/mc/RunIIFall17MiniAODv2/GluGluToBulkGravitonToHHTo2B2Tau_M-450_narrow_13TeV-madgraph/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/90000/8CDFDFC6-C542-E811-9360-848F69FBC12A.root',
    #'/store/mc/RunIIFall17MiniAODv2/GluGluToBulkGravitonToHHTo2B2Tau_M-450_narrow_13TeV-madgraph/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/90000/A4C07038-AC42-E811-8A74-1418776375C9.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/production/CMSSW_9_4_6_patch1/src/LLRHiggsTauTau/NtupleProducer/inputFiles/Graviton450_1.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/production/CMSSW_9_4_6_patch1/src/LLRHiggsTauTau/NtupleProducer/inputFiles/Graviton450_2.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/production/CMSSW_9_4_6_patch1/src/LLRHiggsTauTau/NtupleProducer/inputFiles/Graviton450_3.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/production/CMSSW_9_4_6_patch1/src/LLRHiggsTauTau/NtupleProducer/inputFiles/Graviton450_4.root',

    # Data
    #'/store/data/Run2017B/Tau/MINIAOD/17Nov2017-v1/40000/02D49C45-F8DD-E711-9ACC-001E675043AD.root',
    #'/store/data/Run2017B/SingleMuon/MINIAOD/31Mar2018-v1/100000/001642F1-6638-E811-B4FA-0025905B857A.root',
    # miniAOD_v2
    #'/store/data/Run2017B/Tau/MINIAOD/31Mar2018-v1/00000/040B1CD3-9437-E811-8D93-A4BF01158FE0.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/production/CMSSW_9_4_6_patch1/src/LLRHiggsTauTau/NtupleProducer/inputFiles/TauB.root'
    #'/store/data/Run2017F/Tau/MINIAOD/31Mar2018-v1/00000/0089E8C0-1A37-E811-9E5C-008CFAC93D18.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/production/CMSSW_9_4_6_patch1/src/LLRHiggsTauTau/NtupleProducer/inputFiles/TauF.root'

    # TT Fully Hadronic
    #'/store/mc/RunIIFall17MiniAOD/TTToHadronic_TuneCP5_13TeV-powheg-pythia8/MINIAODSIM/94X_mc2017_realistic_v10-v1/00000/047A883D-9618-E811-B3FB-7CD30AD09FDC.root',
    #'/store/mc/RunIIFall17MiniAODv2/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/20000/CA2359BE-6442-E811-A7C5-9CB654AEAE02.root'
    # miniAOD_v2
    #'/store/mc/RunIIFall17MiniAODv2/TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/00000/0031EAB0-8442-E811-84DF-0025901AFB36.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/production/CMSSW_9_4_6_patch1/src/LLRHiggsTauTau/NtupleProducer/inputFiles/TT.root',

    # DY 2 Jets
    #'/store/mc/RunIIFall17MiniAODv2/DY2JetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/810000/BAE0A78F-7366-E811-B871-A0369FD20D18.root'
    
    #'/store/mc/RunIIFall17MiniAODv2/ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8/MINIAODSIM/PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/10000/6435B3B7-8342-E811-B249-0CC47A5FA3BD.root'
    
    
    # VBF private production test
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/TEST_PRODUCTION/CMSSW_9_4_6_patch1/src/nevts_1000/HIG-RunIIFall17MiniAODv2-01157.root'
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/TEST_PRODUCTION/CMSSW_9_4_6_patch1/src/nevts_1000_2/HIG-RunIIFall17MiniAODv2-01157.root'
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/TEST_PRODUCTION/CMSSW_9_4_6_patch1/src/HIG-RunIIFall17MiniAODv2-01157_1.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/TEST_PRODUCTION/CMSSW_9_4_6_patch1/src/HIG-RunIIFall17MiniAODv2-01157_2.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/TEST_PRODUCTION/CMSSW_9_4_6_patch1/src/HIG-RunIIFall17MiniAODv2-01157_3.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/TEST_PRODUCTION/CMSSW_9_4_6_patch1/src/HIG-RunIIFall17MiniAODv2-01157_4.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/TEST_PRODUCTION/CMSSW_9_4_6_patch1/src/HIG-RunIIFall17MiniAODv2-01157_5.root',
    #'file:/afs/cern.ch/work/f/fbrivio/Hhh_1718/TEST_PRODUCTION/CMSSW_9_4_6_patch1/src/HIG-RunIIFall17MiniAODv2-01157_6.root',
    
    )
)

# process.source.skipEvents = cms.untracked.uint32(968)
#process.source.eventsToProcess = cms.untracked.VEventRange("1:2347130-1:2347130") # run only on event=2347130 (syntax= from run:evt - to run:evt)
#process.source.eventsToProcess = cms.untracked.VEventRange("1:26669:46950527-1:26669:46950527")
#process.source.eventsToProcess = cms.untracked.VEventRange("1:7:5757-1:7:5757")
#process.source.eventsToProcess = cms.untracked.VEventRange("305902:212:301932757-305902:212:301932757")
#process.source.eventsToProcess = cms.untracked.VEventRange("1:493:476100-1:493:476100")

#Limited nEv for testing purposes. -1 to run all events
process.maxEvents.input = -1

# JSON mask for data --> defined in the lumiMask file
# from JSON file
if not IsMC:
  execfile(PyFilePath+"python/lumiMask.py")
  process.source.lumisToProcess = LUMIMASK

##
## Output file
##
process.TFileService=cms.Service('TFileService',fileName=cms.string('HTauTauAnalysis.root'))
#process.TFileService=cms.Service('TFileService',fileName=cms.string('HTauTauAnalysis_VBF_6.root'))
#process.TFileService=cms.Service('TFileService',fileName=cms.string('HTauTauAnalysis_TauDataF_eighteen.root'))

# L1 trigger objects (as suggested on: https://twiki.cern.ch/twiki/bin/view/CMS/HiggsToTauTauWorking2017#Trigger_Information )
#  ----> TO BE FIXED <----
#process.out.outputCommands.append('keep *_caloStage2Digis_*_*') #FRA
#process.out.outputCommands.append('keep *_gmtStage2Digis_*_*')  #FRA 


if DO_ENRICHED:
    process.out = cms.OutputModule("PoolOutputModule",
        fileName = cms.untracked.string('Enriched_miniAOD.root'),
        outputCommands = cms.untracked.vstring('keep *'),
        fastCloning     = cms.untracked.bool(False),
        #Compression settings from MiniAOD allowing to save about 10% of disc space compared to defults ->
        compressionAlgorithm = cms.untracked.string('LZMA'),
        compressionLevel = cms.untracked.int32(4),
        dropMetaData = cms.untracked.string('ALL'),
        eventAutoFlushCompressedSize = cms.untracked.int32(15728640),
        overrideInputFileSplitLevels = cms.untracked.bool(True)
        # <-
    )
    if STORE_ENRICHEMENT_ONLY:
        # Store only additional collections compared to MiniAOD necessary to reproduce ntuples (basically MVAMET, lepton pairs with SVFit and corrected jets)
        # Size of about 10% of full EnrichedMiniAOD
        process.out.outputCommands.append('drop *')
        process.out.outputCommands.append('keep *_SVllCand_*_*')
        process.out.outputCommands.append('keep *_SVbypass_*_*')
        process.out.outputCommands.append('keep *_barellCand_*_*')
        process.out.outputCommands.append('keep *_corrMVAMET_*_*')
        process.out.outputCommands.append('keep *_MVAMET_*_*')
        process.out.outputCommands.append('keep *_jets_*_*')
        process.out.outputCommands.append('keep *_patJetsReapplyJEC_*_*')
        process.out.outputCommands.append('keep *_softLeptons_*_*')
        process.out.outputCommands.append('keep *_genInfo_*_*')
        #process.out.fileName = 'EnrichementForMiniAOD.root' #FIXME: change name of output file?
    process.end = cms.EndPath(process.out)

#process.options = cms.PSet(skipEvent =  cms.untracked.vstring('ProductNotFound'))
#process.p = cms.EndPath(process.HTauTauTree)
process.p = cms.Path(process.Candidates)

# Silence output
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 5000
#process.MessageLogger.categories.append('onlyError')
#process.MessageLogger.cerr.onlyError=cms.untracked.PSet(threshold  = cms.untracked.string('ERROR'))
#process.MessageLogger.cerr.threshold='ERROR'
#process.MessageLogger = cms.Service("MessageLogger",
#	destinations = cms.untracked.vstring('log.txt')
#)
#process.MessageLogger.threshold = cms.untracked.string('ERROR')

#processDumpFile = open('process.dump' , 'w')
#print >> processDumpFile, process.dumpPython()
