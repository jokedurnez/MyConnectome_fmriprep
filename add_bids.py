import pandas as pd
import numpy as np
import json
import shutil
from datetime import datetime
import os

bidsdir = os.environ.get("BIDSDIR")
sessions = [x for x in os.listdir(os.path.join(bidsdir,'sub-01')) if x.startswith("ses")]
sessionsfile = os.path.join(bidsdir,"sub-01",'sub-01_sessions.tsv')

#####################################
## add session 107 to sessions.tsv ##
#####################################

sessionstsv = pd.read_csv(sessionsfile,sep="\t")
sessionstsv = sessionstsv.set_value(105,'sescode','ses-107')
sessionstsv.to_csv(sessionsfile,sep="\t",index=False)

################################################
## add EffectiveEchoSpacing: session-specific ##
################################################

for session in sessions:
    if 'func' in os.listdir(os.path.join(bidsdir,'sub-01',session)):
        bolds = [x.split(".")[0] for x in os.listdir(os.path.join(bidsdir,'sub-01',session,'func')) if '_bold.nii.gz' in x]
        for bold in bolds:
            # load in the dicom header of this scan
            dicomhdr = os.path.join(bidsdir,'sourcedata/dicom_headers/sub-01/%s/func/%s.json'%(session,bold))
            if os.path.exists(dicomhdr):
                dicomdata = json.loads(open(dicomhdr).read())
            else:
                dicomdata = {}
            # check if there is already a json for this scan
            bidsjson = os.path.join(bidsdir,'sub-01/%s/func/%s.json'%(session,bold))
            if os.path.exists(bidsjson):
                with open(bidsjson,'r') as f:
                    bidsdata = json.load(f)
            else:
                bidsdata = {}
            # session 105 does not have header info, but EES is same as other scans
            if session == 'ses-105':
                bidsdata['EffectiveEchoSpacing'] = 0.00035002083333333326
            else:
            # check if effective echo spacing can be found
                if 'CsaImage.BandwidthPerPixelPhaseEncode' in dicomdata.keys() and 'AcquisitionMatrix' in dicomdata.keys():
                    bidsdata['EffectiveEchoSpacing'] = dicomdata['CsaImage.BandwidthPerPixelPhaseEncode']/dicomdata['AcquisitionMatrix'][0]/1000
            with open(bidsjson,'w') as f:
                json.dump(bidsdata,f)

####################################################################
## add PhaseEncodingDirection: not session specific ==> top level ##
####################################################################

taskjsons = [x for x in os.listdir(bidsdir) if 'task' in x]
for taskjson in taskjsons:
    taskjson_fullpath = os.path.join(bidsdir,taskjson)
    with open(taskjson_fullpath,'r') as f:
        data = json.load(f)
    data['PhaseEncodingDirection']='j-'
    with open(taskjson_fullpath,'w') as f:
        json.dump(data,f)

phasejson = os.path.join(bidsdir,'phasediff.json')
with open(phasejson,'r') as f:
    data = json.load(f)
data['PhaseEncodingDirection']='j-'
with open(phasejson,'w') as f:
    json.dump(data,f)

##############################
## add IntendedFor to fmaps ##
##############################

def extract_time(x):
    try:
        return datetime.strptime(x,"%m/%d/%y")
    except:
        return 0

sessions = pd.read_csv(sessionsfile,sep="\t")
sessions['scan:has_fmap']=0
sessions['use_fmap']=''
sessions['timestamps']=[extract_time(x) for x in sessions['date']]

# fill in which sessions have fmaps
for index,row in sessions.iterrows():
    sesfolder = os.path.join(bidsdir,"sub-01",row.sescode)
    if 'fmap' in os.listdir(sesfolder):
        sessions = sessions.set_value(index,'scan:has_fmap',1)

# figure out which fmap each session should use (find closest date)
for index,row in sessions.iterrows():
    if row.sescode == 'ses-107':
        sessions.set_value(index,'use_fmap','ses-105')
        continue
    if row['scan:has_fmap']==1:
        sessions = sessions.set_value(index,'use_fmap',row.sescode)
    else:
        thisdate = row.timestamps
        subset = sessions.loc[sessions['scan:has_fmap']==1]
        subset['distance']=abs(thisdate-subset.timestamps)
        idx_closest = subset['distance'].idxmin()
        sestouse = sessions.loc[idx_closest,'sescode']
        sessions = sessions.set_value(index,'use_fmap',sestouse)

# fill in IntendedFor and EchoTime1 and EchoTime2
for session in sessions.sescode:
    if session == 'ses-107':
        continue
    sesfolder = os.path.join(bidsdir,'sub-01',session)
    if 'fmap' in os.listdir(sesfolder):
        fmapfolder = os.path.join(sesfolder,'fmap')
        fmaps = [x[:-7] for x in os.listdir(fmapfolder) if ('phasediff' in x and '.nii.gz' in x)]
        for fmap in fmaps:
            newjson = os.path.join(sesfolder,'fmap',fmap+'.json')
            # if there is a json in the new dir: use this
            if session in set(sessions['use_fmap']):
                IntendedFor = []
                whichuses = sessions['sescode'][sessions['use_fmap']==session]
                for index,value in whichuses.iteritems():
                    oldsesfolder = os.path.join(bidsdir,'sub-01',value)
                    funcfolder = os.path.join(oldsesfolder,'func')
                    if os.path.exists(funcfolder):
                        funcs = [os.path.join(value,'func',x) for x in os.listdir(funcfolder) if 'bold.nii.gz' in x]
                        IntendedFor = IntendedFor+funcs
            data = {'IntendedFor': IntendedFor}
            with open(newjson,'w') as f:
                json.dump(data,f)
