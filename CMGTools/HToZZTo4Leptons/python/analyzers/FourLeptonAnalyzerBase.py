import operator 
import itertools
import copy

from ROOT import TLorentzVector

from CMGTools.RootTools.fwlite.Analyzer import Analyzer
from CMGTools.RootTools.fwlite.Event import Event
from CMGTools.RootTools.statistics.Counter import Counter, Counters
from CMGTools.RootTools.fwlite.AutoHandle import AutoHandle
from CMGTools.RootTools.physicsobjects.PhysicsObjects import Lepton,Photon,Electron

from CMGTools.HToZZTo4Leptons.analyzers.DiObject import DiObject
from CMGTools.HToZZTo4Leptons.analyzers.DiObjectPair import DiObjectPair
from CMGTools.HToZZTo4Leptons.tools.FSRRecovery import FSRRecovery
from CMGTools.HToZZTo4Leptons.tools.FakeRateCalculator import FakeRateCalculator



        
class FourLeptonAnalyzerBase( Analyzer ):

    LeptonClass1 = Lepton 
    LeptonClass2 = Lepton

    def __init__(self, cfg_ana, cfg_comp, looperName ):
        super(FourLeptonAnalyzerBase,self).__init__(cfg_ana,cfg_comp,looperName)

        if hasattr(cfg_ana,'fakeRates'):
            self.fakeRates=[]
            for fr in cfg_ana.fakeRates:
                self.fakeRates.append(FakeRateCalculator(fr))


    def declareHandles(self):
        super(FourLeptonAnalyzerBase, self).declareHandles()

        self.handles['rho'] = AutoHandle( ('kt6PFJetsForIso', 'rho'),
                                          'double')
        self.handles['met'] = AutoHandle( ('cmgPFMET',''),'std::vector<cmg::BaseMET>')

        self.handles['photons'] = AutoHandle( ('cmgPhotonSel',''),'std::vector<cmg::Photon>')
        self.handles['electrons'] = AutoHandle( ('cmgElectronSel',''),'std::vector<cmg::Electron>')


    def beginLoop(self):
        super(FourLeptonAnalyzerBase,self).beginLoop()
        self.counters.addCounter('FourLepton')
        count = self.counters.counter('FourLepton')
        count.register('all events')
        
    def buildPhotonList(self, event):

        event.photons = map( Photon,self.handles['photons'].product() )
#        event.photons.extend(map( Photon,self.handles['electrons'].product()))


    def buildLeptonList(self, event):
        event.leptons1 = map( self.__class__.LeptonClass1,
                              self.handles['leptons1'].product() )
        if self.__class__.LeptonClass1 != self.__class__.LeptonClass2: 
            event.leptons2 = map( self.__class__.LeptonClass2,
                                  self.handles['leptons2'].product() )
        else:
            event.leptons2 = event.leptons1




       
    def process(self, iEvent, event):
        return True
    
    def findPairs(self, leptons):
        out = []
        for l1, l2 in itertools.combinations(leptons, 2):
            out.append( DiObject(l1, l2) )
        return out


    def findPairsWithFSR(self, leptons,photons):
        out = []
        for l1, l2 in itertools.combinations(leptons, 2):
            z = DiObject(l1, l2)
            if not hasattr(self.cfg_ana,"FSR"):
                out.append(z)
            else:    

                fsrAlgo=FSRRecovery(self.cfg_ana.FSR)

                fsrAlgo.setPhotons(photons)

                fsrAlgo.setZ(z)

                fsrAlgo.recoverZ()

                out.append(z)
        return out


    #this function is different for the ee/mumu
    def findQuads(self, leptons):
        out = []
        for l1, l2,l3,l4 in itertools.permutations(leptons, 4):
            if l1.pt()>l2.pt() and l3.pt()>l4.pt():
                if hasattr(self,'fakeRates'):
                    for fr in self.fakeRates:
                        fr.attachToObject(l3)
                        fr.attachToObject(l4)
                quadObject =DiObjectPair(l1, l2,l3,l4)
                out.append(quadObject)
                


        return out

    def findQuadsWithFSR(self, leptons,photons):
        out = []
        for l1, l2,l3,l4 in itertools.permutations(leptons, 4):
            if l1.pt()>l2.pt() and l3.pt()>l4.pt():
                quadObject =DiObjectPair(l1, l2,l3,l4)
                if not hasattr(self.cfg_ana,"FSR"):
                    if hasattr(self,'fakeRates'):
                        for fr in self.fakeRates:
                            fr.attachToObject(quadObject.leg2.leg1)
                            fr.attachToObject(quadObject.leg2.leg2)
                    out.append(quadObject)
                else:    
                    fsrAlgo=FSRRecovery(self.cfg_ana.FSR)
                    fsrAlgo.setPhotons(photons)
                    fsrAlgo.setZZ(quadObject)
                    #recover FSR photons
                    fsrAlgo.recoverZZ()
                    #Now Z 2
                    quadObject.updateP4()
                    if hasattr(self,'fakeRates'):

                        for fr in self.fakeRates:
                            fr.attachToObject(quadObject.leg2.leg1)
                            fr.attachToObject(quadObject.leg2.leg2)
                    out.append(quadObject)
        return out



    #Common Lepton Selection
    def testLepton(self, lepton, pt, eta,sel=None):
        if sel is not None and  not lepton.getSelection(sel):
          return False
        if lepton.pt() > pt and abs(lepton.eta()) < eta: 
            return True
        else:
            return False

        
        
    def testLeptonLoose1(self, lepton,sel=None):
        return abs(lepton.dxy())<0.5 and abs(lepton.dz())<1. and abs(lepton.sip3D())<4.

    def testLeptonLoose2(self, lepton,sel=None):
        return abs(lepton.dxy())<0.5 and abs(lepton.dz())<1. and abs(lepton.sip3D())<4.

    def testLeptonTight1(self, lepton,sel=None):
        return abs(lepton.dxy())<0.5 and abs(lepton.dz())<1. and abs(lepton.sip3D())<4.

    def testLeptonTight2(self, lepton,sel=None):
        return abs(lepton.dxy())<0.5 and abs(lepton.dz())<1. and abs(lepton.sip3D())<4.


#    Skimming of leptons 1-2 corresponds to the flavour here 
    def testLeptonSkim1(self, lepton,sel=None):
        if hasattr(self.cfg_ana,"minPt1") and hasattr(self.cfg_ana,"maxEta1"):
            return self.testLepton(lepton,self.cfg_ana.minPt1,self.cfg_ana.maxEta1,sel)  and \
                   abs(lepton.dxy())<0.5 and abs(lepton.dz())<1.
        else:
            return abs(lepton.dxy())<0.5 and abs(lepton.dz())<1.

    def testLeptonSkim2(self, lepton,sel=None):
        if hasattr(self.cfg_ana,"minPt2") and hasattr(self.cfg_ana,"maxEta2"):
            return self.testLepton(lepton,self.cfg_ana.minPt2,self.cfg_ana.maxEta2,sel)  and \
                   abs(lepton.dxy())<0.5 and abs(lepton.dz())<1.
        else:
            return abs(lepton.dxy())<0.5 and abs(lepton.dz())<1.

#####################################################




    #loose muon  requirements  
    def testMuonLoose(self, muon):
        '''Returns True if a muon passes a set of cuts.
        Can be used in testLepton1 and testLepton2, in child classes.'''
        looseID = (muon.isGlobal() or muon.isTracker())
        return looseID

    def testElectronLoose(self, electron):
        looseID = electron.numberOfHits()<=1
        return looseID


    def testMuonPF(self, muon):
        '''Returns True if a muon passes a set of cuts.
        Can be used in testLepton1 and testLepton2, in child classes.'''

        pfID = muon.sourcePtr().userFloat("isPFMuon")>0.5
        return pfID


    #tight muonn  requirements 
    def testMuonTight(self, muon):
        '''Returns True if a muon passes a set of cuts.
        Can be used in testLepton1 and testLepton2, in child classes.'''

        iso  = muon.absEffAreaIso(self.rho,self.cfg_ana.effectiveAreas)/muon.pt()<0.4 #warning:you need to set the self.rho !!!
        return self.testMuonLoose(muon) and self.testMuonPF(muon) and iso

    def testElectronTight(self, electron):
        '''Returns True if a electron passes a set of cuts.
        Can be used in testLepton1 and testLepton2, in child classes.'''
        id = electron.mvaIDZZ()
        iso  = electron.absEffAreaIso(self.rho,self.cfg_ana.effectiveAreas)/electron.pt()<0.4 #warning:you need to set the self.rho !!!
        return iso and id 


        


    def testZSkim(self, zCand):
        '''Applies  OS SF and M requirements on a Z'''
        return zCand.M() > self.cfg_ana.z1_m[0] and \
               self.testZSF(zCand) and \
               self.testZOS(zCand)

     
    def testZSF(self, zCand):
        return  (abs(zCand.leg1.pdgId()) == abs(zCand.leg2.pdgId()) )

    def testZOS(self, zCand):
        return  (zCand.charge() == 0) 

    def testZ1PtThresholds(self, zCand):
        return zCand.leg1.pt() > self.cfg_ana.z1_pt1 and \
               zCand.leg2.pt() > self.cfg_ana.z1_pt2 

    def testZ1Mass(self, zCand):
        return zCand.M() > self.cfg_ana.z1_m[0] and \
               zCand.M() < self.cfg_ana.z1_m[1] 

    def testZ2Mass(self, zCand):
        return zCand.M() > self.cfg_ana.z2_m[0] and \
               zCand.M() < self.cfg_ana.z2_m[1] 


    def testZ1LooseID(self,zCand):
        return self.testLeptonLoose1(zCand.leg1) and \
               self.testLeptonLoose1(zCand.leg2)

    def testZ1TightID(self,zCand):
        return self.testLeptonTight1(zCand.leg1) and \
               self.testLeptonTight1(zCand.leg2)

    def testZ2LooseID(self,zCand):
        return self.testLeptonLoose2(zCand.leg1) and \
               self.testLeptonLoose2(zCand.leg2)

    def testZ2TightID(self,zCand):
        return self.testLeptonTight2(zCand.leg1) and \
               self.testLeptonTight2(zCand.leg2)


    def testFourLeptonLooseID(self, fourLepton):
        return self.testZ1LooseID(fourLepton.leg1) and self.testZ2LooseID(fourLepton.leg2)

    def testFourLeptonTightID(self, fourLepton):
        return self.testZ1TightID(fourLepton.leg1) and self.testZ2TightID(fourLepton.leg2)

    def testFourLeptonTightIDZ1(self, fourLepton):
        return self.testZ1TightID(fourLepton.leg1) 

    def testFourLeptonTightIDZ2(self, fourLepton):
        return self.testZ2TightID(fourLepton.leg2) 



    def testFourLeptonSF(self, fourLepton):
        return self.testZSF(fourLepton.leg1) and self.testZSF(fourLepton.leg2)

    def testFourLeptonOS(self, fourLepton):
        return self.testZOS(fourLepton.leg1) and self.testZOS(fourLepton.leg2)

    def testFourLeptonPtThr(self, fourLepton):
        leading_pt = fourLepton.sortedPtLeg(0) 
        subleading_pt = fourLepton.sortedPtLeg(1) 
        return leading_pt>self.cfg_ana.z1_pt1  and subleading_pt>self.cfg_ana.z1_pt2

    def testFourLeptonZ1(self, fourLepton):
        return self.testZ1Mass(fourLepton.leg1) and self.testZSF(fourLepton.leg1) and \
               self.testZOS(fourLepton.leg1)


    def testFourLeptonMassZ1Z2(self, fourLepton):
        return self.testZ1Mass(fourLepton.leg1) and self.testZ2Mass(fourLepton.leg2)

    def testFourLeptonMassZ1(self, fourLepton):
        return self.testZ1Mass(fourLepton.leg1)

        
    def testFourLeptonMinMass(self, fourLepton):
        return fourLepton.minPairMass()>self.cfg_ana.minMass

    def testFourLeptonMassZ(self, fourLepton):
        return fourLepton.mass()>=70

    def testFourLeptonMass(self, fourLepton):
        return fourLepton.mass()>=self.cfg_ana.minHMass and fourLepton.leg2.mass()>self.cfg_ana.minHMassZ2


        
    def bestZBosonByMass(self, zBosons):
        if len( zBosons ) == 0:
            return None
        elif len( zBosons ) == 1:
            return zBosons[0]
        else:
            # taking the closest from the Z mass
            zMass = 91.2
            return min(zBosons, key = lambda x: abs( x.mass() - zMass) )

    def bestZBosonBySumPt(self, zBosons):
        if len( zBosons ) == 0:
            return None
        elif len( zBosons ) == 1:
            return zBosons[0]
        else:
            return max(zBosons, key = lambda x: x.leg1.pt()+x.leg2.pt())


    def testZBosonSumPt(self, zBoson):
        sum=0
        if zBoson.hasFSR():
            sum = zBoson.leg1.pt()+zBoson.leg2.pt()+zBoson.fsrPhoton.pt()
        else:    
            sum = zBoson.leg1.pt()+zBoson.leg2.pt()
        return sum    



    def sortFourLeptons(self, fourLeptons):
        #sort the first one by Z mass and if there
        #are more than one take the two highest pt ones
        if len(fourLeptons)>1 :
            
            fourLeptons=sorted(fourLeptons,key=lambda x: self.testZBosonSumPt,reverse=True)
            fourLeptons=sorted(fourLeptons,key=lambda x: abs(x.leg1.mass()-91.2))
            
        





       

                                                                                                           



                                                                                                       
