TString gPrefix = "";
int neta = 2;

#if 0
TH2 *FR_tight_ttl_el = (TH2*) TFile::Open("../../data/fakerate/FR_ttl2lss_e.root")->Get("FR_e");
TH2 *FR_tight_ttl_mu = (TH2*) TFile::Open("../../data/fakerate/FR_ttl2lss_m.root")->Get("FR_m");
TH2 *FR_ttl_el = (TH2*) TFile::Open("../../data/fakerate/FR_ttl_e.root")->Get("FR_e");
TH2 *FR_ttl_mu = (TH2*) TFile::Open("../../data/fakerate/FR_ttl_m.root")->Get("FR_m");
TH2 *FR_zl_el = (TH2*) TFile::Open("../../data/fakerate/FR_zl_e.root")->Get("FR_e");
TH2 *FR_zl_mu = (TH2*) TFile::Open("../../data/fakerate/FR_zl_m.root")->Get("FR_m");
TH2 *FR_zlw_el = (TH2*) TFile::Open("../../data/fakerate/FR_zlw_e.root")->Get("FR_e");
TH2 *FR_zlw_mu = (TH2*) TFile::Open("../../data/fakerate/FR_zlw_m.root")->Get("FR_m");
#else
TH2 *FR_tight_ttl_el = 0;
TH2 *FR_tight_ttl_mu = 0;
TH2 *FR_ttl_el = 0;
TH2 *FR_ttl_mu = 0;
TH2 *FR_zl_el = 0;
TH2 *FR_zl_mu = 0;
TH2 *FR_zlw_el = 0;
TH2 *FR_zlw_mu = 0;
#endif

TH2 *FR_tight_qcd_el = 0;
TH2 *FR_tight_qcd_mu = 0;
TH2 *FR_qcd_el = 0;
TH2 *FR_qcd_mu = 0;
TH2 *FR_tight_qcdj_mu = 0;
TH2 *FR_qcdj_mu = 0;
TH2 *d_FR_tight_qcd_el = 0;
TH2 *d_FR_tight_qcd_mu = 0;
TH2 *d_FR_qcd_el = 0;
TH2 *d_FR_qcd_mu = 0;

const int ntrig1mu = 5;
const int trig1mu[ntrig1mu] = { 8, 12, 17, 24, 40 };
TH2 *FR_qcd1mu_mu[ntrig1mu], *FR_qcd1mu_el[ntrig1mu];


void loadData(TString iPrefix, int trig) {
    TFile *fMC = TFile::Open(trig == 1 ? "fakeRates_TTJets_MC.root" : "fakeRates_TTJets_MC_NonTrig.root" );
    FR_tight_ttl_el = (TH2*) fMC->Get(iPrefix+"_tight_el");
    FR_tight_ttl_mu = (TH2*) fMC->Get(iPrefix+"_tight_mu");
    FR_ttl_el = (TH2*) fMC->Get(iPrefix+"_el");
    FR_ttl_mu = (TH2*) fMC->Get(iPrefix+"_mu");

    TFile *fQCD = TFile::Open(trig == 1 ? "fakeRates_QCDMu_MC.root" : "fakeRates_QCDMu_MC_NonTrig.root");
    FR_tight_qcd_el = (TH2*) fQCD->Get(iPrefix+"_tight_el");
    FR_tight_qcd_mu = (TH2*) fQCD->Get(iPrefix+"_tight_mu");
    FR_qcd_el = (TH2*) fQCD->Get(iPrefix+"_el");
    FR_qcd_mu = (TH2*) fQCD->Get(iPrefix+"_mu");
    FR_tight_qcdj_mu = (TH2*) fQCD->Get(iPrefix+"j_tight_mu");
    FR_qcdj_mu = (TH2*) fQCD->Get(iPrefix+"j_mu");

    TFile *fQCD1Mu = TFile::Open("fakeRates_QCDMu_MC_SingleMu.root");
    for (int it = 0; it < ntrig1mu; ++it) {
        FR_qcd1mu_mu[it] = (TH2*) fQCD1Mu->Get(Form("%s_TagMu%d_mu", iPrefix.Data(), trig1mu[it]));
        FR_qcd1mu_el[it] = (TH2*) fQCD1Mu->Get(Form("%s_TagMu%d_el", iPrefix.Data(), trig1mu[it]));
    }

    TFile *fDQCD = 0;
    if (iPrefix == "FR")  fDQCD = TFile::Open(trig == 1 ? "frFitsSimple.root"         : "frFitsSimple_TagMu.root");
    if (iPrefix == "FRC") fDQCD = TFile::Open(trig == 1 ? "frFitsSimpleCutBased.root" : "frFitsSimpleCutBased_TagMu.root");
    d_FR_tight_qcd_el = (TH2*) fDQCD->Get("FR_tight_el");
    d_FR_tight_qcd_mu = (TH2*) fDQCD->Get("FR_tight_mu");
    d_FR_qcd_el = (TH2*) fDQCD->Get("FR_el");
    d_FR_qcd_mu = (TH2*) fDQCD->Get("FR_mu");

    TFile *fZMC = TFile::Open("fakeRates_DYJets_MC.root");
    if (fZMC) {
        FR_zl_el = (TH2*) fZMC->Get(iPrefix+"_el");
        FR_zl_mu = (TH2*) fZMC->Get(iPrefix+"_mu");
    }

}

TGraph* drawSlice(TH2 *h2d, int ieta, int color, bool ist=false) {
    if (h2d == 0) return 0;
    TGraphAsymmErrors *ret = new TGraphAsymmErrors(h2d->GetNbinsX());
    TAxis *ax = h2d->GetXaxis();
    for (int i = 0, n = ret->GetN(); i < n; ++i) {
        ret->SetPoint(i, ax->GetBinCenter(i+1), h2d->GetBinContent(i+1,ieta+1));
        ret->SetPointError(i, 0.5*ax->GetBinWidth(i+1), 0.5*ax->GetBinWidth(i+1),
                              h2d->GetBinError(i+1,ieta+1), h2d->GetBinError(i+1,ieta+1));
    }
    ret->SetLineWidth(2);
    ret->SetLineColor(color);
    ret->SetMarkerColor(color);
    if (ist) {
        ret->SetFillColor(color);
        ret->SetFillStyle(3004);
        ret->Draw("E5 SAME");
        ret->Draw("E2 SAME");
    } else {
        ret->Draw("P SAME");
    }
    return ret;
}


TCanvas *c1 = 0;
TH1 *frame = 0;
TLegend *newLeg(double x1, double y1, double x2, double y2, double textSize=0.035) {
    TLegend *ret = new TLegend(x1,y1,x2,y2);
    ret->SetTextFont(42);
    ret->SetFillColor(0);
    ret->SetShadowColor(0);
    ret->SetTextSize(textSize);
    return ret;
}

const char *ETALBL4[4] = { "b1", "b2", "e1", "e2" };
const char *ETALBL2[2] = { "b", "e" };
const char *ietalbl(int ieta) {
    if (neta == 4) return ETALBL4[ieta];
    else return ETALBL2[ieta];
}

void stackFRsMu(int ieta, int idata=0) {
    frame->Draw();
    TLegend *leg = newLeg(.2,.7,.42,.9);
    leg->AddEntry(drawSlice(FR_ttl_mu, ieta, 4, true), "MC tt+l", "LF");
    if (FR_zl_mu) leg->AddEntry(drawSlice(FR_zl_mu, ieta, 7), "MC z+l", "LP");
    //leg->AddEntry(drawSlice(FR_zlw_mu, ieta, 6), "z+l w", "LP");
    leg->AddEntry(drawSlice(FR_qcd_mu, ieta, 206), "MC qcd #mu", "LP");
    //leg->AddEntry(drawSlice(FR_qcdj_mu, ieta, 209), "MC qcd j", "LP");
    leg->Draw();
    if (idata) {
        TLegend *leg = newLeg(.45,.8,.87,.9);
        leg->AddEntry(drawSlice(d_FR_qcd_mu, ieta, 1), "Data qcd #mu", "LP");
        leg->Draw();
    }
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/mu_%s.png", gPrefix.Data(), ietalbl(ieta)));
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/mu_%s.pdf", gPrefix.Data(), ietalbl(ieta)));
}

void stackFRsEl(int ieta, int idata=0) {
    frame->Draw();
    TLegend *leg = newLeg(.2,.7,.42,.9);
    leg->AddEntry(drawSlice(FR_ttl_el, ieta, 4, true), "MC tt+l", "LF");
    if (FR_zl_el) leg->AddEntry(drawSlice(FR_zl_el, ieta, 7), "MC z+l", "LP");
    //leg->AddEntry(drawSlice(FR_zlw_el, ieta, 6), "z+l w", "LP");
    leg->AddEntry(drawSlice(FR_qcd_el, ieta, 206), "MC qcd #mu", "LP");
    leg->Draw();
    if (idata) {
        TLegend *leg = newLeg(.45,.8,.87,.9);
        leg->AddEntry(drawSlice(d_FR_qcd_el, ieta, 1), "Data qcd #mu", "LP");
        leg->Draw();
    }
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/el_%s.png", gPrefix.Data(), ietalbl(ieta)));
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/el_%s.pdf", gPrefix.Data(), ietalbl(ieta)));
}

void stackFRsMuT(int ieta, int idata=0) {
    frame->Draw();
    TLegend *leg = newLeg(.2,.7,.42,.9);
    leg->AddEntry(drawSlice(FR_tight_ttl_mu, ieta, 4, true), "MC tt+l", "LF");
    //leg->AddEntry(drawSlice(FR_tight_zl_mu, ieta, 7), "z+l", "LP");
    //leg->AddEntry(drawSlice(FR_tight_zlw_mu, ieta, 6), "z+l w", "LP");
    leg->AddEntry(drawSlice(FR_tight_qcd_mu, ieta, 206), "MC qcd #mu", "LP");
    //leg->AddEntry(drawSlice(FR_tight_qcdj_mu, ieta, 209), "MC qcd j", "LP");
    leg->Draw();
    if (idata) {
        TLegend *leg = newLeg(.45,.8,.87,.9);
        leg->AddEntry(drawSlice(d_FR_tight_qcd_mu, ieta, 1), "Data qcd #mu", "LP");
        leg->Draw();
    }
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/mu_tight_%s.png", gPrefix.Data(), ietalbl(ieta)));
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/mu_tight_%s.pdf", gPrefix.Data(), ietalbl(ieta)));
}

void stackFRsElT(int ieta, int idata=0) {
    frame->Draw();
    TLegend *leg = newLeg(.2,.7,.42,.9);
    leg->AddEntry(drawSlice(FR_tight_ttl_el, ieta, 4, true), "MC tt+l", "LF");
    //leg->AddEntry(drawSlice(FR_tight_zl_el, ieta, 7), "z+l", "LP");
    //leg->AddEntry(drawSlice(FR_tight_zlw_el, ieta, 6), "z+l w", "LP");
    leg->AddEntry(drawSlice(FR_tight_qcd_el, ieta, 206), "MC qcd #mu", "LP");
    leg->Draw();
    if (idata) {
        TLegend *leg = newLeg(.45,.8,.87,.9);
        leg->AddEntry(drawSlice(d_FR_tight_qcd_el, ieta, 1), "Data #mu", "LP");
        leg->Draw();
    }
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/el_tight_%s.png", gPrefix.Data(), ietalbl(ieta)));
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/el_tight_%s.pdf", gPrefix.Data(), ietalbl(ieta)));
}

void stackFRs1MuMu(int ieta, int idata=0) {
    frame->Draw();
    TLegend *leg = newLeg(.2,.65,.42,.9);
    //leg->AddEntry(drawSlice(FR_ttl_mu, ieta, 4, true), "MC tt+l", "LF");
    leg->AddEntry(drawSlice(FR_qcd_mu, ieta, 1, true), "MC NoT", "LP");
    for (int it = 0; it < ntrig1mu; ++it) {
        leg->AddEntry(drawSlice(FR_qcd1mu_mu[it], ieta, 206+4*it), Form("MC Mu%d",trig1mu[it]), "LP");
    }
    leg->Draw();
    if (idata) {
        TLegend *leg = newLeg(.45,.8,.87,.9);
        //leg->AddEntry(drawSlice(d_FR_qcd_mu, ieta, 1), "Data qcd #mu", "LP");
        leg->Draw();
    }
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/mu_%s_1mu.png", gPrefix.Data(), ietalbl(ieta)));
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/mu_%s_1mu.pdf", gPrefix.Data(), ietalbl(ieta)));
}

void stackFRs1MuEl(int ieta, int idata=0) {
    frame->Draw();
    TLegend *leg = newLeg(.2,.65,.42,.9);
    leg->AddEntry(drawSlice(FR_qcd_el, ieta, 1, true), "MC NoT", "LP");
    for (int it = 0; it < ntrig1mu; ++it) {
        leg->AddEntry(drawSlice(FR_qcd1mu_el[it], ieta, 206+4*it), Form("MC Mu%d",trig1mu[it]), "LP");
    }
    leg->Draw();
    if (idata) {
        TLegend *leg = newLeg(.45,.8,.87,.9);
        //leg->AddEntry(drawSlice(d_FR_qcd_el, ieta, 1), "Data qcd #mu", "LP");
        leg->Draw();
    }
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/el_%s_1mu.png", gPrefix.Data(), ietalbl(ieta)));
    c1->Print(Form("ttH_plots/270413/FR_QCD_Simple/stacks/%s/el_%s_1mu.pdf", gPrefix.Data(), ietalbl(ieta)));
}


void stackFRs(int what=0, int idata=0, int itrigg=1) {
    switch (what) {
        case 0: loadData("FR",itrigg);  gPrefix = "";           break;
        case 1: loadData("FRC",itrigg); gPrefix = "cut_based/"; break;
        case 2: loadData("FRH",itrigg); gPrefix = "hybrid/";    break;
    }
    if (idata) gPrefix += "with_data/";
    switch (itrigg) {
        case 0: gPrefix += "non_trig/"; break;
        case 1: break;
        case 2: gPrefix += "tag_trig/"; break;
    }

    gSystem->Exec("mkdir -p ttH_plots/270413/FR_QCD_Simple/stacks/"+gPrefix);
    gROOT->ProcessLine(".x ~gpetrucc/cpp/tdrstyle.cc");
    gStyle->SetOptStat(0);
    c1 = new TCanvas("c1","c1");
    c1->SetLogx(1);
    frame = new TH1F("frame",";p_{T} (GeV);Fake rate",100,5, itrigg ? 80 : 50);
    frame->GetYaxis()->SetRangeUser(0.,1.);
    frame->GetYaxis()->SetDecimals(1);
    for (int i = 0; i < neta; ++i) {
        frame->GetYaxis()->SetRangeUser(0.0,1.0);
        stackFRsMu(i, idata);
        stackFRsEl(i, idata);
        //frame->GetYaxis()->SetRangeUser(0.0,0.6);
        //stackFRs1MuMu(i, idata);
        //stackFRs1MuEl(i, idata);
        frame->GetYaxis()->SetRangeUser(0.0,0.5);
        stackFRsMuT(i, idata);
        stackFRsElT(i, idata);
    }
}
