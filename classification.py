from pathlib import Path
import pickle
from matplotlib import pyplot
import numpy as np
import torch
from torch import optim
from torch import nn
from torch.utils.data import TensorDataset
from torch.utils.data import DataLoader
import os
import torch.nn.functional as F


print(torch.cuda.is_available())

os.environ["CUDA_VISIBLE_DEVICES"] = "1"
dev = torch.device(
    "cuda") if torch.cuda.is_available() else torch.device("cpu")
# dev = torch.device("cpu")

torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True

DATA_PATH = Path("data")
MODEL_PATH = Path("models")
PATH = DATA_PATH / "DWI"
model_PATH = MODEL_PATH / "Sig70_2"

PATH.mkdir(parents=True, exist_ok=True)

# FILENAME = "Signature_bin35_train200_validation72_test200.pkl"
# FILENAME = "Signature_bin35_train200_validation72_test200_shuffle_bvalue.pkl"
FILENAME = "Signature_bin70_train200_validation72_test200.pkl"

with open((PATH / FILENAME).as_posix(), "rb") as f:
    ((x_train, y_train), (x_valid, y_valid), (x_test, y_test)) = pickle.load(f, encoding="latin-1")


pyplot.imshow(x_train[0].reshape((12, 70)), cmap="gray")
pyplot.show()
print(x_train.shape)
x_train = x_train.astype('float32')
x_valid = x_valid.astype('float32')
x_test = x_test.astype('float32')
y_train = y_train.astype('int64')
y_valid = y_valid.astype('int64')
y_test = y_test.astype('int64')
# PyTorch uses torch.tensor, rather than numpy arrays, so we need to convert our data.
x_train, y_train, x_valid, y_valid, x_test, y_test = map(
    torch.tensor, (x_train, y_train, x_valid, y_valid, x_test, y_test)
)

bs = 200  # batch size

def accuracy(out, yb):
    preds = torch.argmax(out, dim=1)
    return (preds == yb).float().mean()

lr = 0.00001  # learning rate
epochs = 200000 # how many epochs to train for

loss_func = F.cross_entropy

train_ds = TensorDataset(x_train, y_train)
valid_ds = TensorDataset(x_valid, y_valid)
test_ds = TensorDataset(x_test, y_test)

def loss_batch(model, loss_func, xb, yb, opt=None):
    loss = loss_func(model(xb), yb)

    if opt is not None:
        loss.backward()
        opt.step()
        opt.zero_grad()

    return loss.item(), len(xb)


def fit(epochs, model, loss_func, opt, train_dl, valid_dl, test_dl):
    for epoch in range(epochs):
        model.train()
        losses_train, nums_train = zip(
            *[loss_batch(model, loss_func, xb, yb, opt) for xb, yb in train_dl]
        )
        model.eval()
        with torch.no_grad():
            losses_valid, nums_valid = zip(
                *[loss_batch(model, loss_func, xb, yb) for xb, yb in valid_dl]
            )
            losses_test, nums_test = zip(
                *[loss_batch(model, loss_func, xb, yb) for xb, yb in test_dl]
            )

        train_loss = np.sum(np.multiply(losses_train, nums_train)) / np.sum(nums_train)
        accuracies_train = [accuracy(model(xb), yb) for xb, yb in train_dl]
        train_accuracy = np.sum(np.multiply(accuracies_train, nums_train)) / np.sum(nums_train)

        valid_loss = np.sum(np.multiply(losses_valid, nums_valid)) / np.sum(nums_valid)
        accuracies_valid = [accuracy(model(xb), yb) for xb, yb in valid_dl]
        valid_accuracy = np.sum(np.multiply(accuracies_valid, nums_valid)) / np.sum(nums_valid)

        test_loss = np.sum(np.multiply(losses_test, nums_test)) / np.sum(nums_test)
        accuracies_test = [accuracy(model(xb), yb) for xb, yb in test_dl]
        test_accuracy = np.sum(np.multiply(accuracies_test, nums_test)) / np.sum(nums_test)

        print(epoch, train_loss, train_accuracy.cpu().numpy(), valid_loss, valid_accuracy.cpu().numpy(),test_loss, test_accuracy.cpu().numpy())
        save_PATH = os.path.join(model_PATH, 'parameters_' + str(epoch) + '.pt')
        with torch.no_grad():
            torch.save({
                'epoch': epoch,
                'train_loss': train_loss,
                'train_accuracy': train_accuracy.cpu().numpy(),
                'valid_loss': valid_loss,
                'valid_accuracy': valid_accuracy.cpu().numpy(),
                'test_loss': test_loss,
                'test_accuracy': test_accuracy.cpu().numpy(),
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': opt.state_dict(),
            }, save_PATH)

def get_data(train_ds, valid_ds, test_ds, bs):
    return (
        DataLoader(train_ds, batch_size=bs, shuffle=False),
        DataLoader(valid_ds, batch_size=bs),
        DataLoader(test_ds, batch_size=bs),
    )

# nn.Sequential

class Lambda(nn.Module):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def forward(self, x):
        return self.func(x)



def preprocess(x, y):
    return x.view(-1, 1, 12, 70).to(dev), y.to(dev)

class WrappedDataLoader:
    def __init__(self, dl, func):
        self.dl = dl
        self.func = func

    def __len__(self):
        return len(self.dl)

    def __iter__(self):
        batches = iter(self.dl)
        for b in batches:
            yield (self.func(*b))

train_dl, valid_dl, test_dl = get_data(train_ds, valid_ds, test_ds, bs)
train_dl = WrappedDataLoader(train_dl, preprocess)
valid_dl = WrappedDataLoader(valid_dl, preprocess)
test_dl = WrappedDataLoader(test_dl, preprocess)

model = nn.Sequential(
    nn.Conv2d(1, 16, kernel_size=3, stride=1, padding=[1, 0]),
    nn.AdaptiveAvgPool2d([6, 17]),
    nn.ReLU(),
    nn.Conv2d(16, 16, kernel_size=3, stride=1, padding=[1, 0]),
    nn.AdaptiveAvgPool2d([3, 5]),
    nn.ReLU(),
    nn.Conv2d(16, 2, kernel_size=3, stride=1, padding=[1, 0]),
    nn.ReLU(),
    nn.AdaptiveAvgPool2d(1),

    Lambda(lambda x: x.view(x.size(0), -1)),
)
model.to(dev)
opt = optim.SGD(model.parameters(), lr=lr, momentum=0)

print('Wrapping DataLoader')
fit(epochs, model, loss_func, opt, train_dl, valid_dl, test_dl)
#

