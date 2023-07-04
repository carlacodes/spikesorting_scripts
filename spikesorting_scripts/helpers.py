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

    
