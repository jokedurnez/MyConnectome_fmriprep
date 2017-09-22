# MyConnectome run through fmriprep

This repository contains code to preprocess the MyConnectome data with fmriprep.  Most importantly, some changes had to be made to MyConnectome (R1.0.3) using `add_bids.py` to R1.0.4.  An overview of the changes:

- session 107 was added to sessions.tsv
- `EffectiveEchoSpacing` was added to each scan based on the dicom headers (present in sourcedata).  This is not the same for each scan, so it's session specific.
- `PhaseEncodingDirection` was added to the top level task jsons for the tasks and phasediff jsons.
- `IntendedFor` was added to the fmap jsons: each functional scan is now linked to an fieldmap.  If no fieldmap was collected in the same session, then the fieldmap closest in time is used.

The preprocessing was run with the following commands:
```
$IMAGE $BIDSDIR $PREPDIR participant --participant_label 01 -w $LOCAL_SCRATCH --anat-only --output-space T1w fsaverage5 template --nthreads 16 --mem_mb 200000
$IMAGE $BIDSDIR $PREPDIR participant --participant_label 01 -w $LOCAL_SCRATCH -t rest --output-space T1w fsaverage5 template --nthreads 16 --mem_mb 200000
$IMAGE $BIDSDIR $PREPDIR participant --participant_label 01 -w $LOCAL_SCRATCH -t $task --output-space T1w fsaverage5 template --nthreads 16 --mem_mb 200000
```

with
- `task` in `tasks=( breathhold dotstop eyesopen languagewm nback objects retinotopy spatialwm )`
- `$IMAGE`: the singularity container created with `singularityware/docker2singularity` from docker container `poldracklab/fmriprep:1.0.0-rc2` available on docker hub.
- `$BIDSDIR`: the folder with raw data
- `$PREPDIR`: the output folder (`$BIDSDIR/derivatives/fmriprep_1.0.0/`)
