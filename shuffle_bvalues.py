import pickle, os
import numpy as np

bin_num = 35
bvalue_num = 12

PATH = "D:\\rectal"
FILENAME = "Signature_bin35_train200_validation72_test200.pkl"

with open((os.path.join(PATH, FILENAME)), "rb") as f:
    ((x_train, y_train), (x_valid, y_valid), (x_test, y_test)) = pickle.load(f, encoding="latin-1")

np.random.seed(3)

Unit = np.arange(bin_num)
Shuffle_unit = np.arange(bvalue_num)
np.random.shuffle(Shuffle_unit)

Shuffles = Unit+bin_num*(Shuffle_unit[0])
for ii in range(bvalue_num-1):
    Shuffles = np.concatenate((Shuffles,Unit+bin_num*(Shuffle_unit[ii+1])))

print(Shuffles)

x_train = x_train[:, Shuffles]
x_valid = x_valid[:, Shuffles]
x_test = x_test[:, Shuffles]

with open ('D:\\rectal\\Signature_bin35_train200_validation72_test200_shuffle_bvalue', 'wb') as pickle_file:
    pickle.dump(((x_train, y_train),(x_valid, y_valid),(x_test, y_test)), pickle_file)