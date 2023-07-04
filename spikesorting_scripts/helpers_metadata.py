from pathlib import Path
import os
import numpy as np
from tqdm import tqdm
import shutil
import pickle
from helpers import get_channelmap_names

def getchanmapnames_andmove(datadir, ferret):
    subfolder ='/'
    fulldir = datadir / ferret
    print([f.name for f in fulldir.glob('*g0')])
    list_subfolders_with_paths = [f.path for f in os.scandir(fulldir) if f.is_dir()]
    session_list = list(fulldir.glob('*_g0'))
    bigdict = {}
    for session in tqdm(session_list):

        chanmapdict = get_channelmap_names(session)
        print(chanmapdict)
        #append chan map dict to big dict
        bigdict.update(chanmapdict)
    for keys in bigdict:
        print(keys)
        print(bigdict[keys])
        #find out if filename contains keyword
        upperdirec = keys.replace('_imec0', '')
        if 'S3' in bigdict[keys]:
            print('found s3')
            dest = Path(str(fulldir)+'/S3')
        elif 'S4' in bigdict[keys]:
            print('found S4')
            dest = Path(str(fulldir)+'/S4')
        elif 'S2_CGmod' in bigdict[keys]:
            print('found S2mod')
            dest = Path(str(fulldir)+'/S2mod')
        elif 'S1' in bigdict[keys]:
            print('found S1')
            dest = Path(str(fulldir)+'/S1')
        try:
            shutil.move(str(fulldir / upperdirec), str(dest))
        except:
            print('already moved')

    return bigdict


def writeprobeinformationtocsv(recording, save_path):

    '''takes a recording and saves the channel positions in ground truth distance space to a pickle file
    Parameters
    ----------
    recording : RecordingExtractor
        The recording extractor to be saved, e.g.   recording = se.read_spikeglx(datadir / session, stream_id='imec0.ap')
    # recording = spikeglx_preprocessing(recording)
    # recordings_list.append(recording)
    save_path : str
    Returns
    -------
    None
    '''
    probe = recording.get_probe()

    contactpos = probe.contact_positions
    channel_ids = probe.device_channel_indices
    # combine the channel ids and the contact positions in an array
    channel_ids = np.array(channel_ids)
    # reshape channel_ids to a column vector
    channel_ids = np.reshape(channel_ids, (len(channel_ids), 1))
    channel_ids = channel_ids.astype(int)
    contactpos = np.array(contactpos)

    channelpos_array = np.concatenate((channel_ids, contactpos), axis=1)
    # sort rows by y position
    channelpos_array = channelpos_array[channelpos_array[:, 2].argsort()]

    # save this array as a csv file
    with open('D:/channelpos.pkl', 'wb') as f:
        pickle.dump(channelpos_array, f)