# MyConnectome_fmriprep

This repository contains code to preprocess the MyConnectome data with fmriprep.  Most importantly, some changes had to be made to MyConnectome (R1.0.3) using `add_bids.py`.  An overview of the changes:

- session 107 was added to sessions.tsv
- `EffectiveEchoSpacing` was added to each scan based on the dicom headers (present in sourcedata).  This is not the same for each scan, so it's session specific.
- `PhaseEncodingDirection` was added to the top level task jsons for the tasks and phasediff jsons.
- `IntendedFor` was added to the fmap jsons: each functional scan is now linked to an fieldmap.  If no fieldmap was collected in the same session, then the fieldmap closest in time is used.
