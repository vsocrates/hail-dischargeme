# hail-dischargeme
2024 BioNLP DischargeMe Challenge

The codebase for the **2nd place** winning submission to the "Discharge Me!": BioNLP ACL'24 Shared Task on Streamlining Discharge Documentation. We have also submitted a publication which will be linked here for citation. 

## Experiments
The code includes a number of experiments outlined below:  

| Task                   | Model                            | Overall         | BLEU   | ROUGE-1 | ROUGE-2 | ROUGE-L | BERTScore | Meteor | AlignScore | MEDCON |
|------------------------|----------------------------------|-----------------|-----------------|------------------|------------------|------------------|--------------------|-----------------|---------------------|-----------------|
| Brief Hospital Course  | AIMI-Baseline                    | 0.1141          | 0.0171          | 0.1184           | 0.0698           | 0.1348           | 0.1726             | 0.0889          | 0.1714              | 0.1398          |
|                        | GPT 3.5 (0-shot)                 | 0.2035          | 0.0210          | 0.3472           | 0.0983           | 0.2289           | 0.2815             | 0.2232          | 0.1865              | 0.2410          |
|                        | Clinical-T5                      | 0.2068          | 0.0357          | 0.3145           | 0.1378           | 0.2273           | 0.3180             | 0.1678          | **0.2251**     | 0.2285          |
|                        | BioBART                          | 0.2198          | 0.0576          | 0.3161           | 0.1100           | 0.2021           | **0.3383**    | **0.2823** | 0.2007              | **0.2515** |
|                        | BioBART v2                       | 0.2227          | **0.0600** | 0.3310           | 0.1239           | 0.2231           | 0.3354             | 0.2802          | 0.1941              | 0.2340          |
|                        | BioBART-Shuffled                 | **0.2464** | 0.0488          | **0.3807**  | **0.2052**  | **0.3003**  | 0.3278             | 0.2661          | 0.1959              | 0.2463          |
|                        | GPT-3.5 + Pseudo-SOAP notes*     | 0.1498          | 0.0032          | 0.2603           | 0.0345           | 0.1233           | 0.2374             | 0.2037          | 0.2000              | 0.1360          |
|                        | BioBART + Conditional Generation | 0.1255          | 0.0045          | 0.2015           | 0.0381           | 0.0900           | 0.1607             | 0.2070          | 0.1739              | 0.1282          |
| Discharge Instructions | AIMI-Baseline                    | 0.0909          | 0.0119          | 0.1343           | 0.0335           | 0.0910           | 0.1026             | 0.0889          | 0.1622              | 0.1025          |
|                        | GPT-3.5 (0-shot)                 | 0.2289          | 0.0299          | 0.3761           | 0.1312           | 0.2271           | 0.3047             | 0.3109          | 0.1821              | 0.2690          |
|                        | BioBART                          | **0.3308** | **0.1458** | **0.4465**  | **0.1796**  | **0.2679**  | **0.4382**    | **0.3976** | **0.3527**     | **0.4183** |
