# SIH26038 — End-to-End Project Plan (v2)
**Explainable AI for Diabetic Retinopathy Screening in Rural India (MathWorks)**
Plan date: 29 Aug 2026 · Team of 6 · Objectives are grouped into workstreams, not yet assigned to people.

---

## 0. Parameters & assumptions

| Param | Value | Basis / adjust if |
|---|---|---|
| `EXAMS` | 31 Aug → 5 Sep | given |
| `COLLEGE_PPT_DUE` | 3 Sep (beta version; editable afterwards — confirmed) | given |
| `STUDY_WINDOW` | 6 → 7 Sep (2–4 days, exam-end to college round) | given |
| `COLLEGE_ROUND` | 7–11 Sep, most likely 8–9 Sep | given |
| `PORTAL_DEADLINE` | 20 Sep; aim to upload by ~17 Sep, PDF only | given |
| `SHORTLIST` | ~19 Oct 2026 | historical; Phase 2 slides with it |
| `FINALE` | ~10–11 Dec 2026, 36 h on-site | historical; if gap < 7 weeks, cut "practice-deep" items first |
| Compute | 4 GPU laptops (incl. Kavya's) + campus GPU if available | given — training jobs are split across the 4 laptops (§6.5) |
| AI tooling | 2 Claude Pro accounts (Kavya, Krisha); Claude can spec Simulink but not generate `.slx` | given |
| Licences | Campus MATLAB + 6 toolboxes; **SimEvents unconfirmed** | gate G1 |
| Venue | No reliable internet, GPU not guaranteed | hard constraint |

### Compliance posture (pre-hackathon work)
The team's reading is that building the deliverable before the finale can disqualify. The plan therefore treats everything before the finale as **learning, practice prototypes, and rehearsal** — not the submission:

| Allowed (per this posture) | Not done before finale |
|---|---|
| MathWorks Onramps, docs, official examples run as-is | A polished end-to-end product repo |
| Public datasets downloaded, preprocessed, split | Claiming pre-built results as "built at SIH" |
| Throwaway practice builds of each module, deleted or kept private | Reusing practice code verbatim on stage without saying so |
| Public pretrained weights (ImageNet, MathWorks example nets) | — |
| Practicing the Simulink model so it can be rebuilt in ~3 h on site | — |
| Design docs, interface contracts, demo script, slides | — |

**Action:** confirm the actual SIH rule with the college SPOC before Phase 2 — many finalists arrive with trained models. If prior work is permitted, promote "practice prototypes" to "kept builds" and the plan is unchanged otherwise.

### Decision gates
| Gate | When | Question | Fail → |
|---|---|---|---|
| G1 | Phase 2 week 1 | MATLAB + 6 toolboxes activate on ≥3 laptops? SimEvents present? | SimEvents missing → Simulink-base/Stateflow discrete model + pure-MATLAB event-list sim (§9); MATLAB missing → G2 now |
| G2 | Phase 2 week 3 | Grading net trained **in MATLAB** reaches ≥85% referable sensitivity on val (practice run)? | Hybrid: train in PyTorch → ONNX → `importNetworkFromONNX` in MATLAB for inference + Grad-CAM. Pure Python is never chosen while any MATLAB licence works |
| G3 | Phase 2 week 6 | Practice pipeline runs end-to-end on CPU, 10 images < 60 s? | Drop IRMA/NV, drop live segmentation from stage flow, demo from cache |

---

## 1. Phase map

| Phase | Dates | Entry | Exit / done | Shown at end |
|---|---|---|---|---|
| **0a — Beta PPT** | 29 Aug → 3 Sep (overlaps exams) | this plan | 6-slide PDF submitted to college; content = §12 beta column | PDF |
| **0b — Study sprint + college round** | 6 → 11 Sep | exams over | PPT v2 with diagram + refined tech slide; each member can explain one module for 2 min; theme-clarification email sent | Presentation to college judges |
| **0c — Portal submission** | 12 → 17 Sep | college feedback | Final PDF on SIH portal; dataset access requests sent (IDRiD, FGADR, Messidor-2) | Portal confirmation |
| **1 — Learning ramp** | 12 Sep → 18 Oct (~5 wks, low-medium capacity) | PPT submitted | All Onramps done; MATLAB on ≥3 laptops; all datasets on disk + manifest; MathWorks DR example reproduced; first U-Net and first SimEvents tutorial run | "Hello fundus" from each workstream |
| **2 — Practice sprint** | ~19 Oct → ~6 Dec (7 wks) | shortlisted (or 50% effort until result) | Every MD item practiced at least once end-to-end; Simulink rebuild practiced ≤3 h; validation numbers known; demo rehearsed 3×; offline kit packaged | Full practice pipeline + Simulink sweep + ablation table |
| **3 — Finale + report** | ~7 → 18 Dec | practice frozen | 36-h build from a fresh repo using practiced recipes; demo delivered; report + repo tagged | Judges' Q&A survived |

---

## 2. Work-breakdown structure

Tier: **MD** must demo · **ND** nice to have · **AS** architect-only / stub.

### Module 1 — Image quality assessment & enhancement
| ID | Task | Tier | Depends on | When |
|---|---|---|---|---|
| 1.1 | FOV crop + circular mask + resize (shared utility) | MD | — | P1 |
| 1.2 | Classical scores: Laplacian-variance blur, sector illumination uniformity, FOV coverage | MD | 1.1 | P1 |
| 1.3 | 3-way rule decision Good / Enhance / Reject, thresholds tuned on EyeQ | MD | 1.2 | P2 early |
| 1.4 | Enhancement: `adapthisteq` (CLAHE, L-channel) → `imflatfield` → `imnlmfilt` | MD | 1.1 | P2 early |
| 1.5 | Learned gradability classifier (MobileNetV2/ResNet-18 on EyeQ) | ND | 1.3 | P2 mid |
| 1.6 | Recapture feedback text from sub-scores | MD | 1.2 | P2 early |
| 1.7 | Field-condition augmentation set (blur, vignette, exposure, JPEG) | ND | 1.1 | P2 mid |

### Module 2 — Retinal structure segmentation
| ID | Task | Tier | Depends on | When |
|---|---|---|---|---|
| 2.1 | 512×512 patch pipeline from full-res IDRiD/DDR, lesion-positive oversampling | MD | 1.1 | P2 early |
| 2.2 | Vessel U-Net (DRIVE+STARE+CHASE) | MD | 2.1 | P1 late / P2 early |
| 2.3 | OD + fovea localisation — classical first, U-Net heatmap if time | MD / ND | 2.2 | P2 early |
| 2.4 | Exudate + soft-exudate U-Net | MD | 2.1 | P2 early–mid |
| 2.5 | Hemorrhage U-Net + blob classifier (dot/blot/flame) | MD | 2.1 | P2 mid |
| 2.6 | Microaneurysm full-res patch U-Net, focal-Tversky, AUPR on IDRiD test | MD | 2.1 | P2 mid |
| 2.7 | IRMA + neovascularization (FGADR) | AS → ND if access granted early | FGADR | P2 late |
| 2.8 | `lesionStats` feature export (counts, areas, quadrants) | MD | 2.4–2.6 | P2 mid |

### Module 3 — DR severity grading
| ID | Task | Tier | Depends on | When |
|---|---|---|---|---|
| 3.1 | Reproduce MathWorks multilabel DR example (ResNet-101) as-is | MD | MATLAB | P1 |
| 3.2 | EyePACS pretrain, ResNet-50, 512 px, ordinal head | MD | data, 3.1 | P2 early (multi-night) |
| 3.3 | Fine-tune APTOS + IDRiD-train; validate on IDRiD-test | MD | 3.2 | P2 early–mid |
| 3.4 | Referable threshold tuning (sens > 90%) | MD | 3.3 | P2 mid |
| 3.5 | External test on untouched Messidor-2 | MD | 3.3 | P2 mid |
| 3.6 | Fusion model: CNN logits + `lesionStats` + quality → `fitcensemble`/`fitglm` | MD | 2.8, 3.3 | P2 mid–late |
| 3.7 | Temperature-scaling calibration + ECE | MD | 3.3 | P2 mid |
| 3.8 | ONNX import path tested (hybrid readiness) | ND | 3.1 | P2 early |

### Module 4 — Explainability
| ID | Task | Tier | Depends on | When |
|---|---|---|---|---|
| 4.1 | `gradCAM` per class + overlay utility | MD | 3.1 | P2 early |
| 4.2 | `imageLIME` + `occlusionSensitivity` comparison panel | ND | 4.1 | P2 mid |
| 4.3 | Evidence mapper: `lesionStats` → ICDR-criteria text | MD | 2.8 | P2 mid |
| 4.4 | Calibrated confidence display + reliability diagram | MD | 3.7 | P2 mid |
| 4.5 | Annotated PDF report + JSON sidecar | MD | 4.1, 4.3 | P2 late |
| 4.6 | 30-second reviewer UI (App Designer) with timing log | MD | 4.5 | P2 late |
| 4.7 | Clinician rating session (≥1 rater, 20 images) | ND, pitch-critical | 4.6 | P2 late |

### Module 5 — Simulink / SimEvents district simulation
| ID | Task | Tier | Depends on | When |
|---|---|---|---|---|
| 5.1 | Simulink Onramp + SimEvents getting-started reproduced | MD | licence | P1 |
| 5.2 | Base model: generator → upload link → AI server → reject loop → grader queue → sinks | MD | 5.1 | P2 early |
| 5.3 | Workspace-parameterised model + `Simulink.SimulationInput` sweep harness | MD | 5.2 | P2 mid |
| 5.4 | Validation vs Erlang-C (M/M/c) | MD | 5.3 | P2 mid |
| 5.5 | Sizing study for 100k patients/yr; plots | MD | 5.3 | P2 mid–late |
| 5.6 | Dashboard blocks for live stage tweaking | ND | 5.5 | P2 late |
| 5.7 | Pure-MATLAB event-list fallback sim | MD (insurance) | — | P2 early (1 day) |
| 5.8 | **Timed rebuild drill**: rebuild 5.2–5.3 from the block spec in ≤3 h | MD | 5.3 | P2 late, twice |

### Integration, validation, pitch
| ID | Task | Tier | Depends on | When |
|---|---|---|---|---|
| I.1 | `+drpipe` package skeleton + interface contracts (§10) | MD | — | P1 |
| I.2 | Data manifest + leakage-check script | MD | data | P1 |
| I.3 | `runPipeline` orchestrator + cache | MD | all modules | P2 mid–late |
| I.4 | Demo app (App Designer) | MD | I.3, 4.6 | P2 late |
| I.5 | Ablation runs + tables | MD | 3.6 | P2 late |
| I.6 | Offline kit: licence checklist, cached cases, videos, install test on 2 laptops | MD | I.4 | P2 late |
| I.7 | Report skeleton + finale slides | MD | I.5 | P2 late → P3 |

**Critical path:** 1.1 → manifest → 3.1/3.2 (GPU nights) ∥ 2.2/2.4 ∥ 5.2 → 3.3/3.4 → 2.8 → 3.6 + 4.3 → I.3 → I.4 → I.6.

---

## 3. Workstreams (grouped objectives — assign people later)

Six workstreams; a person may hold more than one. Constraints to honour when assigning: ≥3 members on MATLAB from Phase 1; the Simulink stream needs one dedicated person from Phase 2 week 1; the two Claude Pro accounts sit with the two heaviest porting streams (B and C); the 4 GPU laptops go to streams A–C plus one shared.

| Stream | Scope | Skill needed | Load |
|---|---|---|---|
| **A — Quality & data** | Module 1; shared preprocessing; dataset download/storage/manifest; augmentation | Image Processing Toolbox, basic MATLAB | Medium, front-loaded (P1) |
| **B — Segmentation** | Module 2 end-to-end; `lesionStats` | Deep Learning + Medical Imaging Toolbox; the hardest porting | High, P2 |
| **C — Grading & integration** | Module 3; fusion; calibration; `+drpipe` orchestrator; demo app; repo | Deep Learning Toolbox, App Designer | High, P2 |
| **D — Explainability & clinical** | Module 4; reviewer UI; report generator; clinician liaison + rating session | `gradCAM`/LIME built-ins, App Designer, communication | Medium, P2 mid–late |
| **E — Simulink** | Module 5; licence checklist; venue logistics; rebuild drills | Simulink + SimEvents (no ML) — good fit for a less-technical member | Medium, steady from P2 W1 |
| **F — Pitch & validation** | PPT (both rounds), demo script, Q&A drills, results tables, ablation runner, final report | Writing, Stats Toolbox basics | Medium, spikes at P0 and P3 |

Comprehension rule for AI-generated code: every file gets an `%% UNDERSTOOD-BY: <name> <date>` header only once the stream owner can explain it line-by-line; a weekly whiteboard round from Phase 2 week 3 enforces it.

### Sequencing by phase (objectives, not names)
| Phase | Objectives |
|---|---|
| 0a | Beta 6-slide PDF (§12); repo created; theme-clarification email to SIH desk |
| 0b | Study: each module's MathWorks example page read; pipeline diagram drawn; Q&A answers (§12) rehearsed; PPT v2 |
| 0c | Portal upload; IDRiD / FGADR / Messidor-2 access requests; Kaggle team |
| 1 | Onramps (§4); MATLAB installed + toolbox inventory; all datasets on SSD; manifest + leakage check; 1.1–1.2; 3.1 reproduced; 2.2 first run; 5.1; Erlang-C script; clinician contact made; interface contracts written |
| 2 early (W1–2) | G1; 3.2 pretrain launched; 2.1, 2.2, 2.4; 1.3, 1.4, 1.6; 5.2, 5.7; 4.1; 3.8 |
| 2 mid (W3–5) | G2; 3.3–3.5, 3.7; 2.3, 2.5, 2.6, 2.8; 5.3–5.5; 4.3, 4.4; 1.5, 1.7; 3.6; I.3; I.5 |
| 2 late (W6–7) | G3; 4.5–4.7; I.4, I.6; 5.6, 5.8 drills; three full rehearsals; comprehension reviews; report skeleton |
| 3 | Fresh-repo 36-h build following practiced recipes; demo; report |

---

## 4. MATLAB + Simulink learning curriculum

| Item | Who | Hours | When |
|---|---|---|---|
| MATLAB Onramp | everyone | 2 | 0b–P1 |
| Deep Learning Onramp | streams A–D | 2 | P1 |
| Image Processing Onramp | streams A, B, D | 2 | P1 |
| MathWorks multilabel-DR example, run + read every line | stream C (then D) | 4 | 0b/P1 |
| `unet` / `deeplabv3plusLayers` doc example | stream B | 4 | P1 |
| Medical Imaging Toolbox labeler + `imageDatastore` patterns | stream B | 2 | P2 early |
| `gradCAM`, `imageLIME`, `occlusionSensitivity` docs | stream D | 2 | P1 |
| App Designer tutorial | streams C, D | 3 | P1 late |
| Simulink Onramp | stream E (+F optional) | 3 | 0b–P1 |
| SimEvents: getting started + discrete-event model + patient-flow example | stream E | 8 | P1 → P2 W1 |
| `Simulink.SimulationInput`, `parsim`, `simlog` | stream E | 3 | P2 early |
| Stats Toolbox: `fitglm`, `fitcensemble`, `confusionmat`, `perfcurve` | streams C, F | 2 | P2 mid |
| Reading: IDRiD paper, DRG-Net, ICDR grading table, EyeQ paper | streams B, C, D, F | 4 | 0b–P1 |

Study-sprint (6–7 Sep) minimum: MATLAB Onramp started, one MathWorks example page per module skimmed, ICDR grading table memorised, pipeline diagram drawn. MathWorks SIH mentoring: request a SimEvents review call in P2 W2 and a training-pipeline review in P2 W3.

---

## 5. Dataset acquisition, storage, preprocessing

### 5.1 Acquisition
| Dataset | Module | Size | Access | When |
|---|---|---|---|---|
| APTOS 2019 | 3 | ~10 GB | Kaggle | 0c |
| IDRiD | 2, 3, benchmark | ~1 GB | IEEE DataPort (free account); keep official train/test folders | 0c |
| DRIVE | 2 | 30 MB | grand-challenge login | 0c |
| Messidor-2 | 3 external test | ~3 GB | ADCIS form + published Abràmoff grades | P1 |
| EyePACS (Kaggle DR Detection) | 3 pretrain | ~85 GB | Kaggle, overnight on campus network | P1 |
| EyeQ | 1 | labels (images = EyePACS) | GitHub CSV | 0c |
| DDR | 2 | ~15 GB | Kaggle/GitHub | P1 |
| DeepDRiD | 1 | ~2 GB | challenge site | P1 |
| STARE / CHASE_DB1 / HRF | 2 | <1 GB | open | P1 |
| e-ophtha, DIARETDB1, ROC | 2 | <2 GB | open | P1 |
| FGADR | 2 IRMA/NV | ~5 GB | request form — send in 0c; 2–6 weeks | 0c |
| RFMiD | robustness | 1 GB | open | optional |

### 5.2 Storage
1 TB external SSD = source of truth, second SSD mirror; raw never modified. Processed 512 px sets (~8 GB) copied to all 4 GPU laptops. `data/` gitignored; `manifest.csv` committed.

### 5.3 Manifest columns
`image_id, dataset, patient_id, eye, orig_path, proc_path, phash, split, grade, referable, quality_label, has_masks` — built by one script `buildManifest.m`.

### 5.4 Common preprocessing (`+drpipe/preprocess.m`)
1. FOV detection (red channel > 20 → largest component → circle fit)
2. Crop, pad square, zero outside circle
3. 512×512 for grading/quality; full-res + 512 patches for segmentation
4. Ben-Graham normalised variant for grading
5. PNG, folder = split, read by `imageDatastore`

### 5.5 Splits & leakage rules
| Rule | Why |
|---|---|
| Messidor-2 never seen in training; only `evalExternal.m` loads it | clean external test |
| IDRiD official train/test split kept exactly | leaderboard comparability |
| EyePACS split by `patient_id` (both eyes together), 90/10 | two eyes ≈ duplicates |
| EyeQ ⊂ EyePACS: EyeQ-test images placed in EyePACS *val*, never train | cross-module hygiene |
| APTOS 85/15 stratified, fixed seed | — |
| Global perceptual-hash dedup (Hamming ≤ 6) across all sets; collision → strictest split (test > val > train); log | Kaggle mirrors re-host IDRiD/Messidor |
| DDR for segmentation training only | avoid doubt |
| Seeds fixed; `splits.json` committed | reproducibility |

Imbalance (EyePACS ~73% grade 0): stratified sampling + class-weighted loss; report per-class recall.

---

## 6. Model plan

### 6.1 Grading
| Step | Detail |
|---|---|
| Backbone | ResNet-50 (ImageNet init) via `imagePretrainedNetwork`; MathWorks example structure |
| Input | 512 px Ben-Graham variant; augment rotation ±180°, flips, brightness ±20%, slight blur |
| Head | Ordinal regression (0–4 continuous, MSE), thresholds tuned on val; referable score via calibrated sigmoid on margin; keep a 5-way softmax variant for per-class Grad-CAM |
| Pretrain | EyePACS train, 6–8 epochs, mixed precision, batch 32; multi-night |
| Fine-tune | APTOS-train + IDRiD-train, LR 1e-5, ~15 epochs; early-stop on APTOS val only (never on IDRiD-test) |
| Threshold | pick for sens ≥ 92% on APTOS/EyePACS val; report resulting spec on IDRiD-test and Messidor-2 |
| Calibration | temperature scaling on APTOS val; ECE before/after |
| Fusion | [5 logits, calibrated p, quality score, MA count, HE count, EX area %, SE count, NV flag, blot-HE quadrants] → `fitcensemble` or `fitglm`, 5-fold CV on train sets |

### 6.2 Segmentation
| Structure | Architecture | Data | Loss / imbalance | Metric |
|---|---|---|---|---|
| Vessels | U-Net 4 levels, 256 px patches, green+CLAHE | DRIVE+STARE+CHASE | Dice+BCE | Dice, AUC (DRIVE test) |
| OD / fovea | classical v1; U-Net heatmap v2 | IDRiD localisation | — / MSE | distance error |
| EX, SE | U-Net 512 px, RGB | IDRiD+DDR+e-ophtha EX | Dice+focal; 1:2 positive:random patches | AUPR |
| HE | as EX + blob classifier | IDRiD+DDR | Dice+focal | AUPR |
| MA | full-res 512 patches, 32→64 filters, focal-Tversky α=0.7, 1:3 positive oversampling, TTA flips, area ≤120 px & circularity filter | IDRiD+e-ophtha+ROC+DDR | try `deeplabv3plusLayers` if AUPR < 0.30 | AUPR; sensitivity @ FP/image |
| IRMA, NV | same recipe | FGADR | — | only if granted |

Also train one multi-class U-Net (bg/EX/SE/HE/MA) plus the dedicated MA net; keep the better per class.

### 6.3 Quality
Classical scores → rules (MD); MobileNetV2 3-class on EyeQ (ND). Report EyeQ accuracy and the "gate effect" (grading sens/spec with vs without rejection).

### 6.4 Fallbacks
| Missed | Ladder |
|---|---|
| Referable sens < 90% | lower threshold (spec ≥ 85%) → quality-gated subset → fusion → 2-seed ensemble → report honestly with CIs + inter-grader framing |
| Spec < 85% | fusion + gated subset; show ROC curve not one point |
| MA AUPR < 0.25 | reframe as lesion-level sensitivity @ 2 FP/image; qualitative heatmaps |
| Too slow on CPU | 1024 px inference for demo; full-res cached |
| G2 fails | PyTorch → ONNX → MATLAB inference |

### 6.5 Splitting training across the 4 GPU laptops
| Laptop | Job |
|---|---|
| 1 | EyePACS pretrain (longest; runs nights for ~a week), then fine-tune |
| 2 | Lesion U-Nets: EX/SE, then HE |
| 3 | MA net (full-res, slow) + vessels |
| 4 | Quality classifier, OD/fovea heatmap, fusion/ablation runs, spare capacity |
Sync via the processed-data SSD copy + weights pushed to a shared drive nightly. Campus GPU (if any) takes the pretrain to free laptop 1.

---

## 7. Validation protocol

**Headline:** referable-DR (grade ≥ 2) sensitivity/specificity on IDRiD-test and Messidor-2 with 95% Wilson CIs. **Secondary:** 5-class accuracy + quadratic-weighted kappa, stated beside the ~80–85% inter-grader agreement figure.

| Benchmark | Our number | Compare to |
|---|---|---|
| IDRiD sub-challenge 1 (segmentation) | AUPR per lesion | leaderboard AUPRs (re-verify on `idrid.grand-challenge.org/Leaderboard` before any slide) |
| IDRiD sub-challenge 2 (grading) | 5-class accuracy, 103 images | leaderboard |
| IDRiD sub-challenge 3 (localisation) | OD/fovea distance | leaderboard |
| Messidor-2 referable DR | sens/spec | IDx-DR / literature range |
| EyeQ | gradability accuracy | EyeQ paper |

One frozen `evalAll.m` writes `results/<date>/tables.csv`; every number on a slide traces to a file there.

### Ablation ("integrated beats any single technique")
| Config | On |
|---|---|
| A0 | CNN grading only |
| A1 | A0 + quality gate |
| A2 | A1 + enhancement |
| A3 | lesion-count classifier only (classical single technique) |
| A4 | full fusion |
Sens/spec/QWK per config on both test sets; one bar chart.

---

## 8. Explainability deliverables

| Deliverable | Spec |
|---|---|
| Grad-CAM | `gradCAM(net, img, class)` for predicted + referable class; jet overlay α=0.4; LIME/occlusion panel (ND) |
| Lesion evidence | Module 2 contours (MA red, HE orange, EX yellow, SE white, NV magenta) + counts per ETDRS quadrant |
| Clinical text | ICDR rules: 0 none; 1 MA only; 2 more than MA, less than severe; 3 = 4-2-1 rule; 4 = NV / vitreous HE. Output e.g. "Grade 2 (moderate). Evidence: 7 MA, 3 dot HE in 2 quadrants, 2 hard exudates <1 DD from fovea." |
| Confidence | temperature-scaled probability; reliability diagram (10 bins) + ECE in report appendix |
| Report | 1-page PDF (`mlreportgen` or `exportgraphics`): IDs, quality verdict, grade/referable/confidence, 3-panel figure, evidence bullets, "Reviewed by" line; JSON sidecar |
| **30-s reviewer UI** | one screen, no scroll: left original + toggle overlays; right grade, confidence, ≤4 bullets, **Agree / Override** (grade + reason). Metric: load-to-click time. Target median ≤ 30 s, ≥80% of 20 images ≤ 30 s; auto-logged |
| Clinician rating | 1 ophthalmologist (fallbacks: optometry faculty, MBBS intern, the team's existing dental-faculty contact for a referral); 20 images (10/10), Likert 1–5 usefulness + agree/override rate; if none, two proxy raters, disclosed |

---

## 9. Simulink / SimEvents model spec

`dr_district_pipeline.slx` — built by hand from this spec; Claude supplies spec + harness only.

| # | Block | Config |
|---|---|---|
| 1 | Entity Generator "Camera sites" | exponential intergeneration, mean 1/λ, λ = N_sites × imgs/site/hr; attributes `imgSizeMB` U(2,8), `quality` with P(reject)=`p_rej` |
| 2 | Entity Queue "Upload buffer" | FIFO, capacity `Q_up`; log length |
| 3 | Entity Server "Bandwidth link" | capacity 1; service = `imgSizeMB×8/BW_Mbps` s |
| 4 | Entity Queue "AI inbox" | FIFO |
| 5 | Entity Server "AI inference" | capacity `c_ai`; exponential mean `1/μ_ai` (10 s CPU / 1 s GPU) |
| 6 | Entity Output Switch "Quality gate" | attribute: reject → 7, pass → 8 |
| 7 | Entity Server "Recapture delay" → back to 2 | `t_recapture` (300 s); count |
| 8 | Entity Output Switch "Referable?" | P=`p_ref` (~0.25) → 9, else → 12 |
| 9 | Entity Queue "Grader review" | FIFO; log length + wait |
| 10 | Entity Server "Graders" | capacity `c_gr`; exponential mean `t_review` (60 s with report / 240 s without) |
| 11 | Terminator "Referred" | count |
| 12 | Terminator "Auto-cleared" | count |
| 13 | `simlog` / Simulink Function | mean wait, max queue, utilisation |

Parameters in `params.m` → struct `p` in base workspace; all blocks reference `p.*`.

Harness sketch (`runSweep.m`):
```matlab
p = defaultParams(); mdl = 'dr_district_pipeline';
graders = 1:10; bws = [2 5 10 25 50]; k = 0;
for g = graders, for b = bws, k = k+1;
  in(k) = Simulink.SimulationInput(mdl);
  in(k) = in(k).setVariable('p', setfield(setfield(p,'c_gr',g),'BW_Mbps',b));
  in(k) = in(k).setModelParameter('StopTime','86400*5');
end, end
out = sim(in);                              % parsim if Parallel Toolbox present
res = collectStats(out, graders, bws);      % grader wait, AI utilisation, end-of-day backlog
plotSweep(res);
```

Sizing: 100k patients/yr ≈ 400/day ≈ 50/hr over 8 h, 2 images each → λ ≈ 100 img/hr. Plots: grader wait vs #graders; backlog vs bandwidth; AI utilisation vs `c_ai`; recapture load vs `p_rej`.

Analytic check: grader stage with `p_rej=0`, `BW=∞`: Erlang-C `P_wait`, `W_q = P_wait/(cμ−λ)`, `L_q = λW_q`; table analytic vs simulated for c = 1..6, target < 5% error over 5 simulated days.

Fallbacks: no SimEvents anywhere → Simulink-base/Stateflow discrete-time model, `eventSim.m` event-list sim (same params/plots), Erlang-C dashboard; Simulink missing at venue → video + `eventSim.m` live; slow → one-day run live, sweep pre-computed.

---

## 10. Integration plan

Pipeline: `image → preprocess → assessQuality → {reject+feedback | enhance | pass} → segment → grade (CNN + fusion) → explain → writeReport → PDF/JSON/UI`

| Function | Out (struct) |
|---|---|
| `preprocess(imgPath)` | `.img512 .imgFull .fovMask .meta` |
| `assessQuality(pp)` | `.decision {good,enhance,reject} .scores.blur/.illum/.fov .feedback .imgEnhanced` |
| `segment(pp)` | `.masks.vessel/.od/.fovea/.EX/.SE/.HE/.MA/.NV .lesionStats .odCenter .foveaCenter` |
| `grade(pp, seg)` | `.probs(1×5) .grade .referable .pReferable .fusionUsed .cnnOnlyGrade` |
| `explain(pp, seg, gr)` | `.gradcam .lime .evidence .reliabilityFig` |
| `writeReport(all, outDir)` | paths to pdf/json/png |
| `runPipeline(imgPath, opts)` | everything + timings; `opts.useCache`, `opts.cpuOnly` |

Each has `test_<name>.m`; `runtests` before merge. Repo layout: `+drpipe/ models/ app/ simulink/ scripts/ results/ data/(ignored) docs/ tests/`. Branches `main` (always demo-able), `dev`, `feat/*`; PR review by a non-author. At the finale, start a **fresh repo** and rebuild from the practiced recipes; the practice repo stays private.

---

## 11. Finale demo script (~8 min)

| Min | On stage | Fallback |
|---|---|---|
| 0–1 | Hook: 77M, 1:100k, 90% preventable | — |
| 1–2 | Drop blurred image → rejected with recapture feedback | cached case |
| 2–3 | Borderline image → CLAHE/flat-field before/after → passes | cached case |
| 3–5 | Moderate NPDR image → overlays → "Grade 2, referable 91%" → Grad-CAM + evidence | live seg > 20 s → `useCache`, said openly |
| 5–6 | Reviewer UI: Agree in ~18 s; PDF pops | PDF from `results/` |
| 6–7.5 | Simulink: graders 3→5, one simulated day live, backlog plot; then sweep heatmap | no Simulink → `eventSim.m`; slow → video |
| 7.5–8 | Validation slide (IDRiD row, Messidor-2, ablation chart), toolbox map, next steps | — |

Offline kit on two laptops + USB: activated MATLAB, weights, 30 cached cases, two videos, slides PDF; tested Wi-Fi-off on battery. Licence checklist: for each of 6 toolboxes + SimEvents — `ver` screenshot, activation type, expiry, venue contact.

---

## 12. Idea PPT — 6 slides, fixed template order (PDF upload)

Rules from the template: max 6 slides incl. title; points/diagrams, no paragraphs; template pointers unchanged; PDF only; delete the instructions slide. Two versions: **Beta** (by 3 Sep, during exams — text only, no built work) and **v2** (by college round 8–9 Sep, after the study sprint; then final for portal by ~17 Sep).

| # | Template slide | Beta (3 Sep) | Add for v2 / portal |
|---|---|---|---|
| 1 | **Title page** | PS ID 26038; title; Theme: MedTech/BioTech/HealthTech (note catalogue lists Clean & Green — clarification sent); Category: Software; Team ID; Team name | — |
| 2 | **Idea title + Proposed Solution** | Idea title (e.g. "RetinaGuard: explainable, quality-gated DR screening + district capacity model"). Bullets: (a) 5-stage MATLAB pipeline — quality gate/enhance → structure segmentation → 5-level grading, judged on referable-DR sens/spec → Grad-CAM + lesion evidence + calibrated confidence + report → Simulink district model; (b) addresses black-box AI, portable-camera failures, no planning tool; (c) unique: reject-and-explain, evidence tied to ICDR criteria, 30-s reviewer loop, benchmark-validated, SimEvents capacity sizing | One pipeline diagram (image → gate → segment → grade → explain → report; district model beside) |
| 3 | **Technical approach** | Technologies: MATLAB; Image Processing, Computer Vision, Deep Learning, Medical Imaging, Statistics & ML toolboxes, Simulink/SimEvents; ResNet transfer learning, U-Net segmentation, `gradCAM`/`imageLIME`, temperature calibration, ordinal grading; datasets APTOS, IDRiD, DRIVE, Messidor-2 (+EyePACS, DDR, EyeQ, FGADR). Methodology: 5 module boxes each mapped to toolbox function + dataset | Flowchart figure; module→function→dataset table as infographic |
| 4 | **Feasibility & viability** | Feasibility: every module ↔ public dataset ↔ official MathWorks example; binary referable metric is the attainable target (deployed systems 87–97%). Risks: MATLAB/Simulink ramp; clinical bar; sub-pixel MA; licences at venue; no clinician. Strategies: official examples + MathWorks mentoring; EyePACS-scale pretraining + quality gate; fine-tune on IDRiD/ROC/e-ophtha; offline kit + fallbacks; measurable 30-s UI + rating session | Risk/strategy as a 3-column mini-table |
| 5 | **Impact & benefits** | Target: PHCs in rural India, 77M diabetics, 1 ophthalmologist / 100k rural. Social: earlier referral, blindness prevented; Economic: grader time cut per image, district sized for 100k patients/yr; Environmental/operational: fewer futile referrals & travel; Trust: every grade explained and auditable | Two or three icon-style stats |
| 6 | **Research & references** | IDRiD challenge (Porwal 2020, leaderboard); MathWorks multilabel-DR example; MathWorks DR blog; DRG-Net; Biomarker Activation Map; EyeQ (Fu 2019); FGR-Net; ResViT FusionNet; PMC12472159 (DNN vs human criteria); SimEvents docs — with links | Trim to fit, keep links |

### Q&A prep (college round and finale)
| Question | Answer |
|---|---|
| DR AI exists (ARDA, Medios) — why you? | They output grades; we reject ungradeable images, explain with ICDR-tied lesion evidence, and size the district program — a deployable combination, not an accuracy delta |
| Can undergrads hit >90/85? | Binary referable target; literature 87–97% on public sets; EyePACS pretraining; quality gate; honest CIs |
| Sub-pixel MA? | Fine-tune on IDRiD/e-ophtha/ROC at full resolution; AUPR vs leaderboard; lesion-level sensitivity framing |
| Why MATLAB? | Built-in Grad-CAM/LIME, medical labelers, SimEvents — one language across all 5 modules; ONNX import if needed |
| Clinical validation? | One clinician rating session + measurable 30-s UI; proxy raters disclosed if needed |
| Was this AI-generated? | Every component has a named owner who can whiteboard it |
| Indian data bias? | IDRiD is Indian; Messidor-2/EyePACS external; per-dataset reporting |
| What have you built so far? (college round) | Nothing yet — by rule and by design; we show the plan, the dataset/toolbox map, and the practice roadmap |

---

## 13. Risk register

| # | Risk | Trigger | Mitigation | Contingency |
|---|---|---|---|---|
| R1 | MATLAB/Simulink ramp too slow | Onramps not done by end of P1 week 2; 3.1 not reproduced by end P1 | curriculum §4; Claude Pro scaffolds; MathWorks mentor | hybrid G2; shift data chores to stream F |
| R2 | Clinical bar missed | G2; sens < 90% mid-P2 | §6.4 ladder | report with CIs + gate-effect ablation |
| R3 | MA detection weak | AUPR < 0.25 mid-P2 | full-res patches, focal-Tversky, DeepLab | reframe metric, qualitative maps |
| R4 | SimEvents licence missing | G1 | ask admin + MathWorks in 0c | `eventSim.m` + Erlang-C |
| R5 | Simulink left late | 5.2 not done by P2 W2 | dedicated owner W1; no data dependency | second person joins stream E |
| R6 | Venue: no GPU/internet/licence | freeze test fails | offline kit, 1024 px CPU inference, cache | video + cached outputs |
| R7 | No clinician | none confirmed by P2 W4 | start in P1; 3 candidates | proxy raters, disclosed |
| R8 | Theme mislabel | — | email SIH desk in 0b | note on slide 1 |
| R9 | Label noise across datasets | disagreements found | official labels; per-dataset reporting | — |
| R10 | "All AI-generated" | owner can't explain a file | `UNDERSTOOD-BY` headers; weekly whiteboards | assign explainer per module |
| R11 | Pre-hackathon build judged as disqualifying | rule confirmed strict | compliance posture §0; fresh repo at finale; practice artifacts private | present as learning/rehearsal only |
| R12 | Not shortlisted | ~19 Oct | — | repo becomes OEP/course project |
| R13 | Shortlist later than assumed | no result by late Oct | continue at 50% | compress P2 late; drop ND items |
| R14 | GPU laptops insufficient for EyePACS pretrain | > 1 week per epoch set | 4-laptop split §6.5; campus GPU; Kaggle/Colab with ONNX round-trip | ResNet-18, 384 px, APTOS+DDR only |
| R15 | 85 GB EyePACS download stalls | not done by P1 end | campus network overnight; Kaggle CLI resumable | pretrain on APTOS+DDR labels |
| R16 | FGADR denied | no reply by P2 W2 | request in 0c | IRMA/NV = AS tier |
| R17 | Team bandwidth (coursework, OEP) | two missed weekly reviews | weekly review + re-plan | cut ND items first, never MD |
| R18 | Pure-Python temptation | G2 | never while MATLAB licence works | hybrid only |
| R19 | Toolbox activation fails on laptops | G1 | licence checklist | MathWorks hackathon licence |
| R20 | Beta PPT too thin for college judges | feedback 8–9 Sep | study sprint 6–7 Sep; diagram + Q&A table | editable before presentation — iterate v2 |

---

## 14. Review cadence

Monday 20-min standup (done / blocked / this week). Friday 60-min review from Phase 1: demo anything working, one comprehension whiteboard, status per workstream (green/amber/red). Amber two weeks running → re-plan; red on an MD item → reassign from ND work the same day. Gates G1–G3 are reviewed in the Friday slot of their week.
