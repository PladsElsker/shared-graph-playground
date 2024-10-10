import functools
import gc
import math
from typing import Any, Optional


import torch
from PIL import Image
from pathlib import Path

LATENT_FACTOR = 0.18215


vae_device = "cuda"
dtype = torch.float


def load_images(image_paths):
    # Load images and convert to tensors
    images = []
    for image_path in list(image_paths):
        try:
            img = Image.open(image_path).convert('RGB')
        except OSError:
            print(f"broken {image_path}, excluding it.")
            image_paths.remove(image_path)
            continue
        width, height = img.size
        min_dim = min(width, height)
        # Crop to a square
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = (width + min_dim) // 2
        bottom = (height + min_dim) // 2
        img = img.crop((left, top, right, bottom))
        # Downsample to 256x256
        img = img.resize((256, 256))
        images.append(img)
    return images


def u_ids_count(iterations):
    return (iterations + 1) * (2*iterations + 1)


def sinusoidal_embedding_2d(h, w, d, device=None):
    # Ensure 'd' is even for proper splitting
    assert d % 2 == 0, "Dimension 'd' should be even."

    # Create grid for height and width
    grid_h = torch.arange(h//2 - h, h//2, device=device, dtype=torch.float32)
    grid_w = torch.arange(w, device=device, dtype=torch.float32)

    # Dimension factors for scaling (dividing by log-scale)
    div_term_h = torch.pow(10000, torch.arange(0, d//2, device=device, dtype=torch.float32) / (d//2))
    div_term_w = torch.pow(10000, torch.arange(0, d//2, device=device, dtype=torch.float32) / (d//2))

    # Positional encodings for height and width
    pos_h = grid_h[:, None] / div_term_h
    pos_w = grid_w[:, None] / div_term_w

    # Sinusoidal embeddings using Euler's formula: e^(iθ) = cos(θ) + i*sin(θ)
    embed_h = torch.exp(1j * pos_h)
    embed_w = torch.exp(1j * pos_w)

    # Combine embeddings
    embeds = torch.zeros((h, w, d), device=device, dtype=torch.complex64)
    embeds[:, :, :d//2] = embed_h[:, None, :]  # Broadcast along width
    embeds[:, :, d//2:] = embed_w[None, :, :]  # Broadcast along height

    return embeds


def create_attention_mask(h, w, device=None):
    s = max(h, w)
    mask = torch.full((s**2, s**2), -float("inf"), device=device, dtype=torch.float32)
    for t in range(s):
        start_index = u_ids_count(t)
        end_index = u_ids_count(t+1)
        mask[start_index:end_index, 0:end_index] = 0
    reorder = create_u_ids(s, s).reshape(s, s)[:h, :w].flatten().msort()
    reordered = mask[reorder][:, reorder]
    return reordered


@functools.lru_cache
def create_u_ids(h, w, device=None):
    """
    Generate a " sequential U id map" for the output of torch.fft.rfft2
    For h = 8, w = 5:

    y
    4:    28 29 30 31 32
    5:    15 16 17 18 33
    6:    6  7  8  19 34
    7:    1  2  9  20 35
    0:    0  3  10 21 36
    1:    5  4  11 22 37
    2:    14 13 12 23 38
    3:    27 26 25 24 39

    If you squint a little, you can see it creates incremental layers of spirals around 0
    (note that the rows have been rotated by h//2 for an easier explanation of the pattern)
    """

    # split the final matrix in two for easier bounds cropping
    # matrix_neg is built flipped in dim 0 and then unflipped at the end
    matrix_neg = torch.zeros((h // 2, w), dtype=torch.int, device=device)
    matrix_pos = torch.zeros(((h + 1) // 2, w), dtype=torch.int, device=device)
    if matrix_pos.numel():
        matrix_pos[0, 0] = 0

    start_val = 1

    for i in range(0, max((h + 1) // 2, w)):
        # first horizontal bar (leaving the last item out for the first half of vertical bar)
        if matrix_neg[i:i+1, :i+1].numel():
            matrix_neg[i, :i+1] = torch.arange(start_val, start_val + len(matrix_neg[i, :i+1]))
            start_val += len(matrix_neg[i, :i+1])

        # first half of vertical bar
        if matrix_neg[:i+1, i+1:i+2].numel():
            matrix_neg[:i+1, i+1] = torch.arange(start_val + len(matrix_neg[:i+1, i+1]) - 1, start_val - 1, -1)
            start_val += len(matrix_neg[:i+1, i+1])

        # second half of vertical bar
        if matrix_pos[:i+2, i+1:i+2].numel():
            matrix_pos[:i+2, i+1] = torch.arange(start_val, start_val + len(matrix_pos[:i+2, i+1]))
            start_val += len(matrix_pos[:i+2, i+1])

        # second horizontal bar (leaving the last item out for the second half of vertical bar)
        if matrix_pos[i+1:i+2, :i+1].numel():
            matrix_pos[i+1, :i+1] = torch.arange(start_val + len(matrix_pos[i+1, :i+1]) - 1, start_val - 1, -1)
            start_val += len(matrix_pos[i+1, :i+1])

    return torch.cat([matrix_pos, matrix_neg.flip(0)]).flatten()


def create_noise_matrix(b, h, w, d, seed=None, device=None, dtype=None):
    if seed is None:
        generator = None
    else:
        generator = torch.Generator(device=device)
        generator.manual_seed(seed)

    return torch.randn(b, h, w, d, generator=generator, device=device, dtype=dtype)


class ArSpectralDiffusionTransformer(torch.nn.Module):
    def __init__(self, hidden_dim: int = 512, heads: int = 8, blocks: int = 12, dropout: float = 0.5):
        super().__init__()
        self.tokens_in = torch.nn.Linear(4, hidden_dim, dtype=torch.complex64)
        self.positional_embeddings = PositionalEmbedding(hidden_dim, dropout)
        self.encoder_blocks = torch.nn.Sequential(*[
            SpectralTransformerEncoderBlock(hidden_dim, heads, dropout)
            for _ in range(blocks)
        ])
        self.tokens_out = torch.nn.Linear(hidden_dim, 4, dtype=torch.complex64)

    def forward(self, x, mask=None, padding=None):
        """
        :param x: Tensor(B, H, W, C)
        :param mask: Tensor(HxW, HxW)
        :param padding: Tensor(B, HxW)
        :return:
        """
        x = self.tokens_in(x)
        x = self.positional_embeddings(x)

        b, h, w, d = x.shape
        u_ids = create_u_ids(h, w, device=x.device)
        x = x.reshape(b, h*w, d)[:, u_ids]

        for block in self.encoder_blocks:
            x = block(x, mask, padding)

        iu_ids = torch.argsort(u_ids)
        x = x[:, iu_ids].reshape(b, h, w, d)

        return self.tokens_out(x)


class PositionalEmbedding(torch.nn.Module):
    def __init__(self, hidden_dim, dropout):
        super().__init__()
        self.dropout = SpectralDropout(p=dropout)
        positional_embeddings = sinusoidal_embedding_2d(32, 17, hidden_dim)
        self.register_buffer('positional_embeddings', positional_embeddings)

    def forward(self, x):
        """
        :param x: Tensor(B, H, W, D) with HxW the size of the image
        :return:
        """
        x = x + self.positional_embeddings[:x.shape[1], :x.shape[2]]
        x = self.dropout(x)
        return x


class SpectralTransformerEncoderBlock(torch.nn.Module):
    def __init__(self, hidden_dim: int, heads: int, dropout: float, ff_hidden_dim: Optional[int] = None):
        super().__init__()
        self.self_attn = SpectralMultiheadAttention(hidden_dim, heads, dropout)
        self.norm1 = SpectralLayerNorm(hidden_dim)
        self.dropout_sa = SpectralDropout(dropout)

        self.ff1 = torch.nn.Linear(hidden_dim, ff_hidden_dim or hidden_dim, dtype=torch.complex64)
        self.activation = SpectralSoftplus(beta=8, threshold=1)
        self.dropout_ff1 = SpectralDropout(dropout)
        self.ff2 = torch.nn.Linear(ff_hidden_dim or hidden_dim, hidden_dim, dtype=torch.complex64)
        self.dropout_ff2 = SpectralDropout(dropout)
        self.norm2 = SpectralLayerNorm(hidden_dim)

    def forward(self, x, mask=None, padding=None):
        x = x + self.dropout_sa(self.self_attn(x, mask, padding))
        x = self.norm1(x)

        x = x + self.dropout_ff2(self.ff2(self.dropout_ff1(self.activation(self.ff1(x)))))
        return self.norm2(x)


class SpectralLayerNorm(torch.nn.Module):
    def __init__(self, hidden_dim, eps: float = 1e-5):
        super().__init__()
        self.gamma = torch.nn.Parameter(torch.tensor([[1 / math.sqrt(2), 0, 1 / math.sqrt(2)]], dtype=torch.float32).repeat(hidden_dim, 1).clone())
        self.beta = torch.nn.Parameter(torch.zeros(hidden_dim, dtype=torch.complex64))
        self.eps = eps

    def forward(self, x):
        b, s, d = x.shape
        x = x - x.mean(dim=-1, keepdim=True)
        var = torch.bmm(
            torch.view_as_real(x).transpose(-2, -1).reshape(b * s, 2, d),
            torch.view_as_real(x).reshape(b * s, d, 2)
        ) / (d - 1)

        eigen_vals, eigen_vecs = torch.linalg.eigh(var + torch.diag(torch.tensor([self.eps] * 2, device=x.device)))
        eigen_vals = 1 / torch.sqrt(eigen_vals)
        std_inv = torch.bmm(torch.bmm(eigen_vecs, torch.diag_embed(eigen_vals)), torch.linalg.inv(eigen_vecs))

        x = torch.bmm(std_inv, torch.view_as_real(x).transpose(-2, -1).flatten(end_dim=1))
        gamma = torch.stack([self.gamma[:, :2], self.gamma[:, 1:]], dim=-1).repeat(b * s, 1, 1)
        x = torch.view_as_complex((gamma @ x.permute(2, 0, 1).reshape(d * b * s, 2, 1)).reshape(d, b * s, 2).permute(1, 0, 2).contiguous()) + self.beta
        return x.view(b, s, d)


class SpectralMultiheadAttention(torch.nn.Module):
    def __init__(self, hidden_dim: int, heads: int, dropout: float):
        super().__init__()
        self.head_dim = hidden_dim // heads
        assert self.head_dim * heads == hidden_dim, "hidden_dim must be divisible by the number of heads"

        self.to_q = torch.nn.Linear(hidden_dim, hidden_dim, dtype=torch.complex64)
        self.to_k = torch.nn.Linear(hidden_dim, hidden_dim, dtype=torch.complex64)
        self.to_v = torch.nn.Linear(hidden_dim, hidden_dim, dtype=torch.complex64)
        self.dropout = SpectralDropout(dropout)
        self.to_out = torch.nn.Linear(hidden_dim, hidden_dim, dtype=torch.complex64)

        self.scale = math.sqrt(self.head_dim)
        self.hidden_dim = hidden_dim
        self.heads = heads

        self.saved_attn = None  # test

    def forward(self, x, mask=None, padding=None):
        b, s, d = x.shape
        query = self.to_q(x).view(b, s, self.heads, self.head_dim).permute(0, 2, 1, 3).reshape(b * self.heads, s, self.head_dim)
        key = self.to_k(x).view(b, s, self.heads, self.head_dim).permute(0, 2, 1, 3).reshape(b * self.heads, s, self.head_dim)
        value = self.to_v(x).view(b, s, self.heads, self.head_dim).permute(0, 2, 1, 3).reshape(b * self.heads, s, self.head_dim)
        attn = torch.bmm(query, key.conj().transpose(-1, -2)) / self.scale
        if mask is not None:
            attn = attn + mask
        if padding is not None:
            attn = attn + padding[:, None] + padding[None, :]
        attn = (attn - attn.real.max(dim=-1, keepdim=True)[0]).exp()
        attn = (attn / attn.sum(dim=-1, keepdim=True))
        self.saved_attn = attn
        res = torch.bmm(attn, value).view(b, self.heads, s, self.head_dim).permute(0, 2, 1, 3).reshape(b, s, self.heads * self.head_dim)
        res = self.dropout(res)
        return self.to_out(res)

    def get_last_attention_weights(self):
        return self.saved_attn


class SpectralDropout(torch.nn.Module):
    def __init__(self, p: float = 0.5):
        super().__init__()
        self.p = p

    def forward(self, x):
        return spectral_dropout(x, self.p)


def spectral_dropout(x, p):
    magnitude = torch.nn.functional.dropout(x.abs(), p)
    phase = torch.nn.functional.dropout(x.angle(), p)
    real_part = magnitude * torch.cos(phase)
    imag_part = magnitude * torch.sin(phase)
    return torch.complex(real_part, imag_part)


class SpectralSoftplus(torch.nn.Module):
    def __init__(self, beta, threshold):
        super().__init__()
        self.softplus = torch.nn.Softplus(beta=beta, threshold=threshold)

    def forward(self, x):
        return self.softplus(x.real) + 1j * self.softplus(x.imag)


def warmup_scheduler(optimizer, warmup_steps, min_lr, max_lr):
    def lr_lambda(step):
        if step < warmup_steps:
            scale = math.sin(step / warmup_steps * math.pi / 2)
            res = min_lr + (max_lr - min_lr) * scale
        else:
            res = max_lr

        # pytorch stupid quirk: the result is multiplied by max_lr,
        #   so we divide it in advance. say hi to numerical instability!
        return res / max_lr

    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
