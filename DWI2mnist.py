import numpy as np
import os
import SimpleITK as sitk
import pickle
import pandas as pd

src_root = 'D:\\DWI_multi_bvalue'
labelfilename = 'D:\\rectal\\pcr_label.xlsx'
src_root_vec = src_root.split(os.path.sep)


BINS=70

Xdata = np.zeros([472,BINS*12])
Patient_num = 0

label = pd.read_excel(labelfilename)
Ydata = label.values[:,-1]


for patient_root, subdirs1, files in os.walk(src_root):
    patient_root_vec = patient_root.split(os.path.sep)
    if len(patient_root_vec) != len(src_root_vec)+1:
        continue
    ID = patient_root_vec[-1]

    nii_number = 0

    for file in files:
        if 'mask' in file:
            MaskImage = sitk.ReadImage(os.path.join(patient_root,file))
            MaskArray = sitk.GetArrayFromImage(MaskImage)
    print(ID)
    START = BINS
    for file in files:

        if file.endswith('.nii') and 'mask' not in file:

            Image = sitk.ReadImage(os.path.join(patient_root,file))
            Array = sitk.GetArrayFromImage(Image)
            Array = np.log(Array*MaskArray+1)
            arr = Array.flatten()
            arr = arr[arr>0]
            nii_number += 1
            n,bins = np.histogram(arr, bins=BINS, normed=0,range=(3,10))
            if START<BINS*12:
                Xdata[Patient_num,START:START+BINS] = n
            else:
                Xdata[Patient_num, 0:BINS] = n
            START += BINS
    Patient_num += 1

with open ('D:\\rectal\\Signature_bin70.pkl', 'wb') as pickle_file:
    pickle.dump((Xdata, Ydata), pickle_file)
