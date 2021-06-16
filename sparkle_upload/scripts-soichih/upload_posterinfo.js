#!/usr/bin/env node
const config = require('./config');
const admin = require('firebase-admin');
const keywordExtractor = require('keyword-extractor');

admin.initializeApp(config.firebase);

//ref https://github.com/margulies/ohbm2021/blob/main/sparkle_upload/scripts/create-posterpages.ts

//from #general
const posters = require('./posters.json');
//console.dir(posters["poster1050"]);
//process.exit(1);
/*
  poster2830: {
    title: 'Variability of the hemodynamic response function in the healthy human cervical spinal cord at 3T',
    authors: [ 'Rangaprakash Deshpande', 'Robert Barry' ],
    introduction: 'FMRI is the convolution of neural activity and the hemodynamic response function (HRF) [1]. The HRF contains variance from non-neural sources such as local vasculature and is variable across brain regions and individuals [2,3]. In the brain, HRF variability was found to confound functional connectivity (FC) by 14.7% [4]. However, resting-state spinal cord fMRI (rs-scfMRI) studies have not accounted for this variability, in part due to a lack of understanding of HRF variability in the cord. Using HRF parameters estimated in the cervical cord, we present within-subject HRF variability between cord quadrants and between spinal levels (a.k.a. fMRI slices), as well as between-subjects variability.',
    methods: "Rs-scfMRI data were obtained on a Philips Achieva 3T scanner (N=20, healthy adults, 10M/10F, age=32±11y). All participants provided informed consent; procedures were approved by the Vanderbilt University Institutional Review Board (IRB). Complete data acquisition details can be found in [5]. Briefly, two identical rs-scfMRI runs were performed: 3D gradient-echo sequence, volume acquisition time (VAT)=2.08s (288 volumes, 10min), TE=8ms, TR=34ms, FA=8°, SENSE=2.0 (left-right), FOV=150×150 mm, voxel size=1×1×5 mm3, 12 slices (cervical spine vertebral levels C2 through C5). Respiratory and cardiac cycles were recorded using respiratory bellows and pulse oximeter for data denoising. FMRI data were pre-processed using custom MATLAB scripts with the standard rs-scfMRI pipeline previously published by us [6]. Voxel-level HRF deconvolution was then performed using Wu et al.'s technique [7] to estimate one HRF for each voxel. This data-driven technique is being used in several studies [8–10]. HRF shape parameters (response height [RH], time-to-peak [TTP] and full-width-at-half-max [FWHM]) were calculated [3].\n" +
      'Each fMRI slice was divided into 4 gray (GM) and 4 white matter (WM) quadrants (left/right ventral/dorsal horns). The 95th percentile [5] HRF parameters among all voxels within a quadrant were chosen to represent the quadrant. With VAT=2.08s and FWHM having a range of just 1–2s 2, we did not further process FWHM values. Normalized root-mean-squared (RMS) variability of RH/TTP values across quadrants was computed as the percentage ratio of RMS difference between quadrants to the RMS mean of the quadrants (likewise for variability across spinal levels and subjects).',
    results: 'Simple statistics of HRF parameters, aggregated across all quadrants, levels and subjects, showed that (Fig.1) (i) HRF parameters were consistent across two runs in both GM and WM (p>0.13), and (ii) RH and TTP were significantly higher in GM compared to WM (p<5.1×10<sup>-3</sup>). FWHM was not significantly different between GM and WM, which may be attributed to the limited sampling rate [2]. Within- and between-subjects HRF variability were of the same order of magnitude (Fig.2). On average in GM, RH showed 6% variability in both runs and TTP showed 7–9% variability. The numbers were lower with about 4.5% RH variability and 3–4% TTP variability in WM.',
    conclusions: 'We found evidence that the HRF is variable in the spinal cord. We quantified this variability to identify certain cord-specific HRF characteristics. WM HRFs were shorter and quicker than GM HRFs. This could be because of lower metabolism in WM, its different vascular architecture, or its poorer fMRI signal power; available data cannot decipher this yet. Aggregated HRF parameters showed promising consistency across runs, an aspect to be investigated further in the future. RH results were the most robust across runs in both GM and WM. The variability was also similar within- and between-subjects. TTP findings were reliable but less consistent; this must be viewed carefully in view of the limited temporal resolution. The findings are important given that HRF variability can confound spinal cord FC, like in the brain [3,4]. HRF is variable across quadrants, spinal levels and subjects in the healthy human cervical spinal cord.',
    iframeUrl: 'https://anyscreeninc.com/PF/OHBM/2021/OHBM-Ed-Courses-and-Poster-Presenters/pdf_poster_files/Rangaprakash_Deshpande60ac199bd8556/Rangaprakash_Deshpande.pdf',
    thumbnailUrl: 'https://anyscreeninc.com/PF/OHBM/2021/OHBM-Ed-Courses-and-Poster-Presenters/pdf_poster_files/Rangaprakash_Deshpande60ac199bd8556/thumb.jpg',
    category: [
      'fMRI Connectivity and Network Modeling',
      'Cerebral Metabolism and Hemodynamics'
    ],
    previewurl: 'https://ww4.aievolution.com/hbm2101/index.cfm?do=abs.viewAbs&src=ext&abs=2699'
  }

*/
const db = admin.firestore();
const venuesRef = db.collection('venues');

async function update() {
    /*
    const venuesRef = db.collection('venues');
    await venuesRef.doc('testspace').update({
        bannerMessage: "Welcome\n\nHello",
    });
    console.log("updated");
    */

    //const res = await axios.get("https://raw.githubusercontent.com/htwangtw/ohbm2021/update-abstract-book/ohbm2021_abstract_book/2021_abstracts.csv");
    //const abstracts = res.data.trim().split("\n");
    //const header = abstracts.shift().split("€");//  'submissionNumber€title€authors€institution€previewurl€pdf',
    /*
    const venuesRef = db.collection('venues');
    abstracts.forEach(abstract=>{
        const posterID = "poster"+abstract[0];
        console.dir(abstract.split("€"));
        await venuesRef.doc(posterID).update({
            "poster.abstract": "Welcome\n\nHello",
        });
        process.exit(1);
    })
    */
    for(const posterid in posters) {
        const poster = posters[posterid];
        console.log(posterid);
        //console.dir(poster);

        const keywords = keywordExtractor.extract(poster.introduction,{
            language:"english",
            remove_digits: true,
            return_chaned_words: true,
            remove_duplicates: true,
        });


        const name = "Poster "+posterid.substring(6);

        //const presenter = poster.authors.find(a=>!!a.presentingAuthor);
        const update = {
            name,
            chatTitle: name,

            iframeUrl: poster.iframeUrl,

            poster: {
                title: poster.title,
                authors: poster.authors,
                presenter: poster.presenter,
                authorName: poster.authors[0],
                introduction: poster.introduction,
                categories: poster.category,
                thumbnailUrl: poster.thumbnailUrl,
                //softwareDemo: poster.softwareDemo,
                posterId: posterid.substring(6),
                moreInfoUrl: poster.previewurl,
                keywords,
            },
        }

        //optional fields
        if(poster.introVideoUrl) update.poster.introVideoUrl = poster.introVideoUrl;

        console.dir(update);

        await venuesRef.doc(posterid).update(update);
    }
}
update();


