import os
import json
import numpy as np
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from sklearn.linear_model import LinearRegression

LATENTS_W_PATH = 'latent_dataset/latents_w.npy'
ATTRS_JSON_PATH = 'latent_dataset/attributes.json'
SCALER_PATH     = 'latent_dataset/scaler.save'
CLASSIFIERS_PATH= 'latent_dataset/classifiers.npz'

w = np.load(LATENTS_W_PATH)            
if w.ndim == 4:
    w = w.squeeze(1).mean(axis=1)      
elif w.ndim == 3:
    w = w.mean(axis=1)                 
else:
    raise ValueError(f"Неожиданный формат латентов: {w.shape}")

with open(ATTRS_JSON_PATH, 'r') as f:
    attrs = json.load(f)

files = sorted(attrs.keys())
N = len(files)

X = np.zeros((N, 512), dtype=np.float32)
Y_gender = np.zeros(N, dtype=np.int32)
Y_age    = np.zeros(N, dtype=np.float32)
Y_smile  = np.zeros(N, dtype=np.int32)

for i, fname in enumerate(files):
    X[i] = w[i]
    gender = attrs[fname]['gender']
    Y_gender[i] = 1 if gender.lower() == 'man' else 0
    Y_age[i]    = float(attrs[fname]['age']) / 100.0
    Y_smile[i]  = 1 if attrs[fname]['smile'] else 0

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
joblib.dump(scaler, SCALER_PATH)

if len(np.unique(Y_gender)) > 1:
    svm_gender = LinearSVC(max_iter=10000).fit(X_scaled, Y_gender)
    dir_gender = svm_gender.coef_[0]
else:
    dir_gender = np.zeros(512, dtype=np.float32)

if len(np.unique(Y_smile)) > 1:
    svm_smile = LinearSVC(max_iter=10000).fit(X_scaled, Y_smile)
    dir_smile = svm_smile.coef_[0]
else:
    dir_smile = np.zeros(512, dtype=np.float32)

reg_age = LinearRegression().fit(X_scaled, Y_age)
dir_age = reg_age.coef_.astype(np.float32)

np.savez(CLASSIFIERS_PATH,
         gender=dir_gender,
         smile=dir_smile,
         age=dir_age)

print("Training complete. Scaler and classifiers saved.")

