# MRI2MNIST is used to convert diffusion weighted images scanned at multiple b-values into a signature-like image
# and classify the signature-like images by networks that originally designed for the recognition of handwritting digits

# DWI2mnist.py convert diffusion weighted images scanned at multiple b-values into a signature-like image
# DWI2mnist_augmentation.py performs augmentation besides the function of DWI2mnist.py
# grouping.py devides the data into a training group, a validation group and a test group

# Signature_bin35_training200_validation72_test200.rar contains the data used for Sig-35 model.
# Signature_bin70_training200_validation72_test200.rar contains the data used for Sig-70 model.

# classification.py constructs the network, train, validate and test the models.

# signature_like_result.xlsx contains the prediction results of Sig-35 and Sig-70 models
# Gaussian_non_Gaussian_result.xls constains the ADC value and 7 values from non-Gaussian fitting models for comparison
