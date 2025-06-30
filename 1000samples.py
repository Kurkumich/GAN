import torch
import dnnlib
import legacy
import os
from tqdm import tqdm
from PIL import Image

device = torch.device('cuda')
outdir = 'latent_dataset'
os.makedirs(outdir + '/images', exist_ok=True)

with open('/content/drive/MyDrive/Colab_Notebooks/somestuff/stylegan3_main/stylegan3-t-ffhqu-256x256.pkl', 'rb') as f:
    G = legacy.load_network_pkl(f)['G_ema'].to(device)

N = 1000
latents = []
w_vectors = []

for i in tqdm(range(N)):
    z = torch.randn([1, G.z_dim]).to(device)
    w = G.mapping(z, None)
    img = G.synthesis(w, noise_mode='const')
    img = (img * 127.5 + 128).clamp(0, 255).to(torch.uint8)
    img_pil = Image.fromarray(img[0].permute(1, 2, 0).cpu().numpy(), 'RGB')
    img_pil.save(f'{outdir}/images/{i:04d}.png')
    latents.append(z.cpu().numpy())
    w_vectors.append(w.cpu().numpy())
import numpy as np
np.save(f'{outdir}/latents_z.npy', latents)
np.save(f'{outdir}/latents_w.npy', w_vectors)
