#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Filename : ova.py
@CreatedTime : 2023/09/28 12:14


This program has a function to __summary__

'''


############################################################################
# Import modules
############################################################################
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


class Ova(object):
    def __init__(self, ova_dir, storage, vmid, prefix):
        self.ova_file = None
        self.storage = None
        self.vmid = None
        self.prefix = None
        
    
    def setupLogging(self):
        logging.basicConfig(filename='ova_importer.log', level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        
    def checkOva(self):
        if not os.path.exists(self.ova_dir):
            logging.error(f"File {self.ova_file} does not exist!")
            sys.exit(1)
        return self.ova_dir
        
    def importOva(self, ova_file, storage, vmid, prefix):
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
            logging.error(f"Error importing OVA {ova_file}: {e}")