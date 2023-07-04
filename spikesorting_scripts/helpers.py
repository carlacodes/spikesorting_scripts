from pathlib import Path
import os
import numpy as np
from tqdm import tqdm
import shutil
import pickle

from probeinterface import generate_multi_columns_probe

from .npyx_metadata_fct import load_meta_file

def generate_warp_16ch_probe():
    probe = generate_multi_columns_probe(num_columns=8,
                                        num_contact_per_column=2,
                                        xpitch=350, ypitch=350,
                                        contact_shapes='circle')
    probe.create_auto_shape('rect')

    channel_indices = np.array([13, 15,
                                9, 11,
                                14, 16,
                                10, 12,
                                8, 6,
                                4, 2,
                                7, 5,
                                3, 1])

    probe.set_device_channel_indices(channel_indices - 1)

    return probe

def generate_warp_32ch_probe():
    probe = generate_multi_columns_probe(num_columns=8,
                                         num_contact_per_column=4,
                                         xpitch=350, ypitch=350,
                                         contact_shapes='circle')
    probe.create_auto_shape('rect')

    channel_indices = np.array([29, 31, 13, 15,
                                25, 27, 9, 11,
                                30, 32, 14, 16,
                                26, 28, 10, 12,
                                24, 22, 8, 6,
                                20, 18, 4, 2,
                                23, 21, 7, 5,
                                19, 17, 3, 1])

    probe.set_device_channel_indices(channel_indices - 1)

    return probe

def get_channelmap_names(dp):
    """Get the channel map name from the meta file

    Parameters
    ----------
    dp : str
        Path to the recording folder

    Returns
    -------
    channel_map_name : dict
        
    """

    dp = Path(dp)
    imec_folders = [imec_folder for imec_folder in dp.glob('*_imec*')]
    channel_map_dict = {}

    for imec_folder in imec_folders:
        metafile = [meta for meta in next(os.walk(imec_folder))[2] if meta.endswith('.meta')]
        if len(metafile)==0:
            raise(f'No metafile found in {imec_folder.name}')
        elif len(metafile)>1:
            print(f'More that 1 metafile found in {imec_folder.name}. Using {metafile[0]}')

        meta = load_meta_file(imec_folder / metafile[0])
        channel_map_name = Path(meta['imRoFile'])
        channel_map_dict[imec_folder.name] = channel_map_name.name

    return channel_map_dict

    
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

    '''takes a recording and saves the channel positions in ground truth distance space to a csv file
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