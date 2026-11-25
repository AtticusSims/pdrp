---
id: M01
title: iEEG preprocessing, IED screening, ripple detection, and waveform validation
type: method
temporal_status: peer_review_revision
source_locators:
- article:58-58
- article:240-261
- author_response:41-41
- author_response:95-102
- author_response:370-372
relations:
- type: supports
  target: C01
  basis: defines signal preprocessing and ripple event extraction
linked_cards:
- Q01
- Q03
- U02
---

# M01: iEEG preprocessing, IED screening, ripple detection, and waveform validation

Intracranial EEG was recorded via 12- or 16-contact depth electrodes (2 mm length, 0.8 mm diameter, 1.5 mm spacing) using Brain Products (2500 Hz), NeuroScan (2000 Hz), or Nicolet (2048 Hz) amplifiers referenced online to a common subcutaneous electrode (`article:243`). Channel localization co-registered post-implantation CT to pre-implantation MRI, normalized to MNI space in SPM12, visualized in 3D Slicer, segmented via FreeSurfer, and visually verified HPC sites in native space (`article:249`). Channels within clinically identified epileptogenic zones or severely contaminated by epileptic activity were excluded; remaining HPC channels were bipolar re-referenced to the nearest white-matter contact, and LTL channels to an adjacent LTL contact (`article:243`).

Interictal epileptiform discharges (IEDs) were independently visually inspected, marked, and verified by two neurologists at Beijing Xuanwu Hospital prior to ripple detection, corroborated by Brainstorm time-frequency checks separating broadband IEDs (1–180 Hz) from narrowband ripples (70–180 Hz); candidate ripples within 50 ms of an IED duration were excluded (`article:259`, `author_response:370-372`).

Primary ripple detection (Norman et al. 2019/2021; Sakon & Kahana 2022; `article:255`) applied a 70–180 Hz Hamming-windowed FIR bandpass (5 Hz transition), squared the Hilbert amplitude, clipped extremes (≥4 SD) via least-median-square, smoothed with a 40 Hz Kaiser FIR low-pass (5 Hz transition), and selected events exceeding 4 SD above the all-runs channel mean (2 SD start/end; note `article:58` describes 4 SD above pre-encoding baseline), lasting 20–200 ms, merging `findpeaks.m` peaks <30 ms apart. Peri-ripple spectrograms used 6-cycle Morlet wavelets (1–250 Hz, 2 Hz steps) in FieldTrip (`article:261`). Three validations confirmed physiological waveforms: (1) raw unfiltered inter-peak intervals (IPIs) fell 89.84±3.31% within 70–180 Hz (`article:85, 257`, `author_response:41`); (2) an alternative Vaz et al. (2019) detector (80–120 Hz 2nd-order Butterworth, envelope >2 SD, peak >3 SD, duration ≥25 ms, merge <15 ms) replicated ramping (`article:113, 257`); and (3) aperiodic 1/f slope showed no maintenance ramp (`p>0.600`) or memory difference (`p=0.544`; `author_response:99-102`).
