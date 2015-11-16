/* \class SVfitInterface
**
** This class provides an interface to the SVfit standalone algorithm
** for the computation of the SVfit mass of the lepton pair candidates.
** 
** The decay mode (e, mu, tauh) of each lepton is the pair is asserted
** from the pdgId associated and is used in the algorithm.
**
** input type is reco::CompositeCandidate for each lepton
** that is coverted to TLorentzVector to be passed to the algorithm
**
** output type is pat::CompositeCandidate, i.e. the original pairs
** plus some userfloats containing the SVfit mass and MET px, px, pt, phi. 
**  
** \date:    18 November 2014
** \author:  L. Cadamuro (LLR)
*/

#include <FWCore/Framework/interface/Frameworkfwd.h>
#include <FWCore/Framework/interface/EDProducer.h>
#include <FWCore/Framework/interface/Event.h>
#include <FWCore/Framework/interface/ESHandle.h>
#include <FWCore/MessageLogger/interface/MessageLogger.h>
#include <FWCore/ParameterSet/interface/ParameterSet.h>
#include <FWCore/Utilities/interface/InputTag.h>
#include <LLRHiggsTauTau/NtupleProducer/interface/CutSet.h>
#include <LLRHiggsTauTau/NtupleProducer/interface/LeptonIsoHelper.h>
#include <DataFormats/Candidate/interface/ShallowCloneCandidate.h>
#include <DataFormats/PatCandidates/interface/CompositeCandidate.h>
#include <DataFormats/PatCandidates/interface/MET.h>
#include <DataFormats/METReco/interface/PFMET.h>
#include <DataFormats/METReco/interface/PFMETCollection.h>
#include <DataFormats/METReco/interface/CommonMETData.h>
#include <TauAnalysis/SVfitStandalone/interface/SVfitStandaloneAlgorithm.h>
 #include <LLRHiggsTauTau/NtupleProducer/interface/DaughterDataHelpers.h>

#include <vector>
#include <string>

using namespace edm;
using namespace std;
using namespace reco;

// ------------------------------------------------------------------

class SVfitInterface : public edm::EDProducer {
 public:
  /// Constructor
  explicit SVfitInterface(const edm::ParameterSet&);
    
  /// Destructor
  ~SVfitInterface();  

 private:
  virtual void beginJob(){};  
  virtual void produce(edm::Event&, const edm::EventSetup&);
  virtual void endJob(){};

  svFitStandalone::kDecayType GetDecayTypeFlag (int pdgId);
  bool Switch (svFitStandalone::kDecayType type1, double pt1, svFitStandalone::kDecayType type2, double pt2);
  double GetMass (svFitStandalone::kDecayType type, double candMass);

  edm::InputTag theCandidateTag;
  std::vector<edm::InputTag> vtheMETTag;
  //int sampleType;
  bool _usePairMET;
  //bool _useMVAMET;
  TFile* inputFile_visPtResolution_;
  
};

// ------------------------------------------------------------------


SVfitInterface::SVfitInterface(const edm::ParameterSet& iConfig)
{
  theCandidateTag = iConfig.getParameter<InputTag>("srcPairs");
  _usePairMET = iConfig.getParameter<bool>("usePairMET");
  //if (_usePairMET) _useMVAMET = true;
  //else _useMVAMET = false; // TO FIX! NO need for it
  //_useMVAMET = iConfig.getUntrackedParameter<bool>("useMVAMET");

  vtheMETTag = iConfig.getParameter<std::vector<edm::InputTag>>("srcMET");

  edm::FileInPath inputFileName_visPtResolution("TauAnalysis/SVfitStandalone/data/svFitVisMassAndPtResolutionPDF.root");
  TH1::AddDirectory(false);  
  inputFile_visPtResolution_ = new TFile(inputFileName_visPtResolution.fullPath().data());

  produces<pat::CompositeCandidateCollection>();
  
}  

SVfitInterface::~SVfitInterface()
{
    delete inputFile_visPtResolution_;
}

void SVfitInterface::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{  

  // Get lepton pairs
  Handle<View<reco::CompositeCandidate> > pairHandle;
  iEvent.getByLabel(theCandidateTag, pairHandle);
  
  unsigned int elNumber = pairHandle->size();
  unsigned int metNumber = 0;

  /*
  cout << "SVFit DEBUG: input pair collection contains: " << elNumber << " pairs" << endl;
  cout << "SVFit DEBUG: input MEt vector has :" << vtheMETTag.size() << " entries; now printing number of METs in each entry" << endl;
  for (unsigned int i = 0; i < vtheMETTag.size(); i++)
  {
     Handle<View<reco::PFMET> > METHandle_PfMET_DEBUG;
     iEvent.getByLabel(vtheMETTag.at(i), METHandle_PfMET_DEBUG);
     const reco::PFMET& pfMET_DEBUG = (*METHandle_PfMET_DEBUG)[0];
     cout << "  " << i << " | MET num: " << METHandle_PfMET_DEBUG->size() << " | MEt (px, py): " << pfMET_DEBUG.px() <<  " , " << pfMET_DEBUG.py() << endl;
  }
  cout << "FINISHED DEBUG" << endl;
  */

  // MET class type changes if using MVA MEt or 'ordinary' MEt
  
  // create two handles for two types
  Handle<View<reco::PFMET> > METHandle_PfMET;
  Handle<View<pat::MET> >    METHandle_PatMET;
  
  // intialize MET
  double METx = 0.;
  double METy = 0.; 
  TMatrixD covMET(2, 2);
  float significance = -999.;
      
  // initialize MET once if not using PairMET
  if (!_usePairMET)
  {   
     iEvent.getByLabel(vtheMETTag.at(0), METHandle_PatMET);
     metNumber = METHandle_PatMET->size();
     if (metNumber != 1)     
        edm::LogWarning("pfMetHasNotSizeOne") << "(SVfitInterface) Warning! Using single pf MEt, but input MEt collection size is different from 1"
                                                           << "   --> using MET entry num. 0";
     const pat::MET& patMET = (*METHandle_PatMET)[0];
     METx = patMET.px();
     METy = patMET.py();
     
     Handle<double> significanceHandle;
     Handle<math::Error<2>::type> covHandle;
     
     iEvent.getByLabel ("METSignificance", "METSignificance", significanceHandle);
     iEvent.getByLabel ("METSignificance", "METCovariance", covHandle);
     
     //cout << *significanceHandle << " " << *sig00Handle << " " << *sig01Handle << " " << *sig10Handle << " " << *sig11Handle << endl;
     covMET[0][0] = (*covHandle)(0,0);
     covMET[1][0] = (*covHandle)(1,0);
     covMET[0][1] = covMET[1][0]; // (1,0) is the only one saved
     covMET[1][1] = (*covHandle)(1,1);

     significance = (float) (*significanceHandle);
     
     // protection against singular matrices
     if (covMET[0][0] == 0 && covMET[1][0] == 0 && covMET[0][1] == 0 && covMET[1][1] == 0)
        edm::LogWarning("SingularCovarianceMatrix") << "(SVfitInterface) Warning! Input covariance matrix is singular" 
                                                    << "   --> SVfit algorithm will probably crash...";
  }
  
  // Output collection
  auto_ptr<pat::CompositeCandidateCollection> result( new pat::CompositeCandidateCollection );

  // loop on all the pairs
  for (unsigned int i = 0; i < elNumber; ++i)
  {
    //cout << "Cand: " << i << endl; 
    
    // Get the pair and the two leptons composing it
    const CompositeCandidate& pairBuf = (*pairHandle)[i];
    pat::CompositeCandidate pair(pairBuf);
    
    const Candidate *l1 = pair.daughter(0);
    const Candidate *l2 = pair.daughter(1);

    svFitStandalone::kDecayType l1Type = GetDecayTypeFlag (l1->pdgId());
    svFitStandalone::kDecayType l2Type = GetDecayTypeFlag (l2->pdgId());
    double mass1 = GetMass (l1Type, l1->mass());
    double mass2 = GetMass (l2Type, l2->mass());
   
    int decay1 = -1;
    int decay2 = -1;
    if (l1Type == svFitStandalone::kTauToHadDecay) decay1 = (int)(userdatahelpers::getUserFloat(l1,"decayMode"));
    if (l2Type == svFitStandalone::kTauToHadDecay) decay2 = (int)(userdatahelpers::getUserFloat(l2,"decayMode"));
   
    //cout << l1Type << " " << decay1 << endl;
    //cout << l2Type << " " << decay2 << endl;
   
    // compute SVfit only if tau(s) pass the OldDM discriminator (avoids crashes...)
    bool passOldDM = true;
    if (l1Type == svFitStandalone::kTauToHadDecay && userdatahelpers::getUserInt(l1,"decayModeFindingOldDMs") != 1) passOldDM = false;
    if (l2Type == svFitStandalone::kTauToHadDecay && userdatahelpers::getUserInt(l2,"decayModeFindingOldDMs") != 1) passOldDM = false;

    // do not compute SVfit on ee or mumu pairs
    bool isGoodPairType = true;
    if (l1Type == svFitStandalone::kTauToElecDecay && l2Type == svFitStandalone::kTauToElecDecay) isGoodPairType = false;
    if (l1Type == svFitStandalone::kTauToMuDecay && l2Type == svFitStandalone::kTauToMuDecay) isGoodPairType = false;

    // do not compute SVfit if the two pairs are too close one to the other
    bool isGoodDR = true;
    if (deltaR(l1->p4(), l2->p4()) < 0.25) isGoodDR = false;
    
    bool swi = Switch (l1Type, l1->pt(), l2Type, l2->pt());
  
    if (_usePairMET)
    {
      iEvent.getByLabel(vtheMETTag.at(i), METHandle_PfMET);
      metNumber = METHandle_PfMET->size();
             
      const PFMET& pfMET = (*METHandle_PfMET)[0];
      const reco::METCovMatrix& covMETbuf = pfMET.getSignificanceMatrix();
      significance = (float) pfMET.significance();

      METx = pfMET.px();
      METy = pfMET.py();

      covMET[0][0] = covMETbuf(0,0);
      covMET[1][0] = covMETbuf(1,0);
      covMET[0][1] = covMETbuf(0,1);
      covMET[1][1] = covMETbuf(1,1);

      // protection against singular matrices
      if (covMET[0][0] == 0 && covMET[1][0] == 0 && covMET[0][1] == 0 && covMET[1][1] == 0)
      {
          edm::LogWarning("SingularCovarianceMatrix") << "(SVfitInterface) Warning! Input covariance matrix is singular" 
                                                    << "   --> SVfit algorithm will probably crash...";
      }
    } 
     
    //cout << "l1, l2 pdgId: " << l1->pdgId() << " " << l2->pdgId() << endl;
    
    std::vector<svFitStandalone::MeasuredTauLepton> measuredTauLeptons;
    
    if (swi) // 2 first, 1 second (switch)
    {
        measuredTauLeptons.push_back(svFitStandalone::MeasuredTauLepton(l2Type, l2->pt(), l2->eta(), l2->phi(), mass2, decay2 ));  
        measuredTauLeptons.push_back(svFitStandalone::MeasuredTauLepton(l1Type, l1->pt(), l1->eta(), l1->phi(), mass1, decay1 ));
    }
    else // 1 first, 2 second
    {
        measuredTauLeptons.push_back(svFitStandalone::MeasuredTauLepton(l1Type, l1->pt(), l1->eta(), l1->phi(), mass1, decay1 ));
        measuredTauLeptons.push_back(svFitStandalone::MeasuredTauLepton(l2Type, l2->pt(), l2->eta(), l2->phi(), mass2, decay2 ));  
    }
         
    // define algorithm (set the debug level to 3 for testing)
    unsigned int verbosity = 0;
    double SVfitMass = -999.;
    double SVpt = -999.;
    double SVeta = -999.;
    double SVphi = -999.;
    double SVptUnc = -999.;
    double SVetaUnc = -999.;
    double SVphiUnc = -999.;
    double SVMETRho = -999.; // fitted MET
    double SVMETPhi = -999.;

    Bool_t GoodPairFlag = kTRUE;
    
    //lepton 1
    //electron
    if(l1Type == svFitStandalone::kTauToElecDecay && l1->pt() < 17.) GoodPairFlag = kFALSE;
    //muon
    if(l1Type == svFitStandalone::kTauToMuDecay   && l1->pt() < 17.) GoodPairFlag = kFALSE;
    //tau
    if(l1Type == svFitStandalone::kTauToHadDecay  && l1->pt() < 30.) GoodPairFlag = kFALSE;
    if(l1Type == svFitStandalone::kTauToHadDecay  && userdatahelpers::getUserFloat(l1,"byCombinedIsolationDeltaBetaCorrRaw3Hits")>10.)  GoodPairFlag = kFALSE;
    if(l1Type == svFitStandalone::kTauToHadDecay  && userdatahelpers::getUserInt(l1,"decayModeFinding")<0.5)  GoodPairFlag = kFALSE;
    // if(l1Type == svFitStandalone::kTauToHadDecay  && userdatahelpers::getUserInt(l1,"againstMuonLoose3")<0.5)  GoodPairFlag = kFALSE;
    // if(l1Type == svFitStandalone::kTauToHadDecay  && userdatahelpers::getUserInt(l1,"againstElectronMediumMVA5")<0.5)  GoodPairFlag = kFALSE;
    
    //lepton 2
    //electron
    if(l2Type == svFitStandalone::kTauToElecDecay && l2->pt() < 17.) GoodPairFlag = kFALSE;
    //muon
    if(l2Type == svFitStandalone::kTauToMuDecay   && l2->pt() < 17.) GoodPairFlag = kFALSE;
    //tau
    if(l2Type == svFitStandalone::kTauToHadDecay  && l2->pt() < 30.) GoodPairFlag = kFALSE;
    if(l2Type == svFitStandalone::kTauToHadDecay  && userdatahelpers::getUserFloat(l2,"byCombinedIsolationDeltaBetaCorrRaw3Hits")>10.)  GoodPairFlag = kFALSE;
    if(l2Type == svFitStandalone::kTauToHadDecay  && userdatahelpers::getUserInt(l2,"decayModeFinding")<0.5)  GoodPairFlag = kFALSE;
    // if(l2Type == svFitStandalone::kTauToHadDecay  && userdatahelpers::getUserInt(l2,"againstMuonLoose3")<0.5)  GoodPairFlag = kFALSE;
    // if(l2Type == svFitStandalone::kTauToHadDecay  && userdatahelpers::getUserInt(l2,"againstElectronMediumMVA5")<0.5)  GoodPairFlag = kFALSE;
    

    SVfitStandaloneAlgorithm algo(measuredTauLeptons, METx, METy, covMET, verbosity);
    algo.addLogM(false); // in general, keep it false when using VEGAS integration
    
    // only run SVfit if taus are passing OldDM discriminator, skip mumu and ee pairs
    if (passOldDM && isGoodPairType && isGoodDR && GoodPairFlag)
    // if (passOldDM && isGoodPairType && isGoodDR)
    {
      //algo.integrateVEGAS();
      algo.shiftVisPt(true, inputFile_visPtResolution_);
      algo.integrateMarkovChain();
      
      if ( algo.isValidSolution() )
      {    
        SVfitMass = algo.getMass(); // return value is in units of GeV
        SVpt = algo.pt();
        SVeta = algo.eta();
        SVphi = algo.phi();
        SVptUnc = algo.ptUncert();
        SVetaUnc = algo.etaUncert();
        SVphiUnc = algo.phiUncert();
        SVMETRho = algo.fittedMET().Rho();
        SVMETPhi = algo.fittedMET().Phi(); // this is NOT a vector in the transverse plane! It has eta != 0.
        
      } // otherwise mass will be -1
    }
    
    // add user floats: SVfit mass, met properties, etc..  
    pair.addUserFloat("SVfitMass", (float) SVfitMass);
    pair.addUserFloat("SVfit_pt", (float) SVpt);
    pair.addUserFloat("SVfit_eta", (float) SVeta);
    pair.addUserFloat("SVfit_phi", (float) SVphi);
    pair.addUserFloat("SVfit_ptUnc", (float) SVptUnc);
    pair.addUserFloat("SVfit_etaUnc", (float) SVetaUnc);
    pair.addUserFloat("SVfit_phiUnc", (float) SVphiUnc);
    pair.addUserFloat("SVfit_METRho", (float) SVMETRho);
    pair.addUserFloat("SVfit_METPhi", (float) SVMETPhi);
    pair.addUserFloat("MEt_px", (float) METx);
    pair.addUserFloat("MEt_py", (float) METy);
    pair.addUserFloat("MEt_cov00", (float) covMET[0][0]);
    pair.addUserFloat("MEt_cov01", (float) covMET[0][1]);
    pair.addUserFloat("MEt_cov10", (float) covMET[1][0]);
    pair.addUserFloat("MEt_cov11", (float) covMET[1][1]);
    pair.addUserFloat("MEt_significance", significance);
    
    result->push_back(pair);     
  }
  
  iEvent.put(result);
}


svFitStandalone::kDecayType SVfitInterface::GetDecayTypeFlag (int pdgId)
{
    if (abs(pdgId) == 11) return svFitStandalone::kTauToElecDecay;
    if (abs(pdgId) == 13) return svFitStandalone::kTauToMuDecay;
    if (abs(pdgId) == 15) return svFitStandalone::kTauToHadDecay;
    
    edm::LogWarning("WrongDecayModePdgID")
       << "(SVfitInterface): unable to identify decay type from pdgId"
       << "     ---> Decay will be treated as an hadronic decay";
    return svFitStandalone::kTauToHadDecay;
}

// decide if leptons 1 and 2 must be switched to respect SVfit conventions
bool SVfitInterface::Switch (svFitStandalone::kDecayType type1, double pt1, svFitStandalone::kDecayType type2, double pt2)
{
    // e e, mu mu, tau tau
    if (type1 == type2) {return (pt1 < pt2);}
    
    // e tau, mu tau
    if ( (type1 == svFitStandalone::kTauToElecDecay || type1 == svFitStandalone::kTauToMuDecay) &&
         type2 == svFitStandalone::kTauToHadDecay ) {return false;}
    if ( (type2 == svFitStandalone::kTauToElecDecay || type2 == svFitStandalone::kTauToMuDecay) &&
         type1 == svFitStandalone::kTauToHadDecay ) {return true;}

    // e mu
    if (type1 == svFitStandalone::kTauToElecDecay && type2 == svFitStandalone::kTauToMuDecay) {return false;}
    if (type2 == svFitStandalone::kTauToElecDecay && type1 == svFitStandalone::kTauToMuDecay) {return true;}
    
    cout << "SVfit Standalone: ordering not done (should never happen)" << endl;
    return false;
}

// set mass (pdg ele/mu or leave cand mass for tauh
double SVfitInterface::GetMass (svFitStandalone::kDecayType type, double candMass)
{
    if (type == svFitStandalone::kTauToElecDecay) return 0.51100e-3;
    if (type == svFitStandalone::kTauToMuDecay) return 0.10566;

    return candMass; // for tauh and all exceptions return cand mass
}



#include <FWCore/Framework/interface/MakerMacros.h>
DEFINE_FWK_MODULE(SVfitInterface);
