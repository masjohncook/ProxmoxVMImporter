#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Filename : auto_ova_import.py
@CreatedTime : 2023/09/26 16:16


This program has a function to __summary__

'''


############################################################################
# Import modules
############################################################################
import argparse
import os
import subprocess
import sys
import logging

############################################################################

__author__ = 'masjohncook'
__copyright__ = '(C)Copyright 2023'
__credits__ = []
__license__ = 'None'
__version__ = '0.0.1'
__maintainer__ = 'masjohncook'
__email__ = 'mas.john.cook@gmail.com'
__status__ = 'None'

############################################################################


def setup_logging():
    logging.basicConfig(filename='ova_importer.log', level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')

def import_ova(ova_file, storage, vmid):
    try:
        # Extract OVA
        subprocess.run(['tar', '-xvf', ova_file, '-C', '/tmp'], check=True)
        
        # Get the name of the VMDK file
        for file_name in os.listdir('/tmp'):
            if file_name.endswith('.vmdk'):
                vmdk_file = os.path.join('/tmp', file_name)
                break
        else:
            logging.error(f"No VMDK file found in OVA: {ova_file}")
            return False
        
        qcow2_file = os.path.join('/tmp', f"{os.path.splitext(os.path.basename(ova_file))[0]}.qcow2")
        
        # Convert VMDK to QCOW2 format
        subprocess.run(['qemu-img', 'convert', '-f', 'vmdk', '-O', 'qcow2', vmdk_file, qcow2_file], check=True)
        
        # Import the QCOW2 into Proxmox
        subprocess.run(['qm', 'importdisk', str(vmid), qcow2_file, storage], check=True)
        
        # Cleanup temporary files
        os.remove(vmdk_file)
        os.remove(qcow2_file)
        os.remove(os.path.join('/tmp', f"{os.path.splitext(os.path.basename(ova_file))[0]}.ovf"))
        
        logging.info(f"Successfully imported {ova_file} with VMID {vmid}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Error processing {ova_file}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Import OVA files into a Proxmox server.')
    parser.add_argument('-o', '--ova-dir', required=True, help='Path to the directory containing OVA files.')
    parser.add_argument('-s', '--storage', default='local-lvm', help='PVE storage profile.')
    parser.add_argument('-n', '--vmid', type=int, default=101, help='Designated VMID.')
    parser.add_argument('-pn', '--prefix', type=int, default=100, help='Prefix for VMID.')
    args = parser.parse_args()
    
    ova_dir = args.ova_dir
    storage = args.storage
    vmid = args.vmid
    prefix = args.prefix
    
    if not os.path.exists(ova_dir):
        logging.error(f"Directory {ova_dir} does not exist!")
        sys.exit(1)
    
    if vmid <= prefix:
        vmid = prefix + 1
    
    setup_logging()

    for file_name in os.listdir(ova_dir):
        if file_name.endswith('.ova'):
            full_path = os.path.join(ova_dir, file_name)
            if import_ova(full_path, storage, vmid):
                vmid += 1
            else:
                logging.error(f"Failed to import {full_path}, continuing with the next file.")
    
    print("All tasks completed. Check the log file for details.")

if __name__ == "__main__":
    main()
