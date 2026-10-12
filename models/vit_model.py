"""
Vision Transformer (ViT) Architecture & Attention Rollout Engine
Engineered for Feedstock Quality Assessment and Industrial Steel Defect Detection.
"""

import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from PIL import Image
from typing import Tuple, Dict, Any, List, Optional


class PatchEmbedding(nn.Module):
    """Splits image into non-overlapping patches and projects them to embedding dimension."""
    def __init__(self, img_size: int = 224, patch_size: int = 16, in_channels: int = 3, embed_dim: int = 384):
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.n_patches = (img_size // patch_size) ** 2
        self.proj = nn.Conv2d(in_channels, embed_dim, kernel_size=patch_size, stride=patch_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, C, H, W) -> proj: (B, embed_dim, H/P, W/P) -> (B, n_patches, embed_dim)
        x = self.proj(x)
        x = x.flatten(2).transpose(1, 2)
        return x


class MultiHeadSelfAttention(nn.Module):
    """Multi-Head Self-Attention with Attention Matrix Caching for Heatmap Rollout."""
    def __init__(self, embed_dim: int = 384, num_heads: int = 6, qkv_bias: bool = True, attn_drop: float = 0.0):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = embed_dim // num_heads
        self.scale = self.head_dim ** -0.5

        self.qkv = nn.Linear(embed_dim, embed_dim * 3, bias=qkv_bias)
        self.attn_drop = nn.Dropout(attn_drop)
        self.proj = nn.Linear(embed_dim, embed_dim)
        self.last_attn_weights: Optional[torch.Tensor] = None

    def forward(self, x: torch.Tensor, save_attn: bool = True) -> torch.Tensor:
        B, N, C = x.shape
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]

        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)
        if save_attn:
            self.last_attn_weights = attn.detach()

        attn = self.attn_drop(attn)
        out = (attn @ v).transpose(1, 2).reshape(B, N, C)
        out = self.proj(out)
        return out


class MLPBlock(nn.Module):
    """Transformer Feed-Forward MLP Block."""
    def __init__(self, in_features: int, hidden_features: int, drop: float = 0.1):
        super().__init__()
        self.fc1 = nn.Linear(in_features, hidden_features)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(hidden_features, in_features)
        self.drop = nn.Dropout(drop)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        x = self.drop(x)
        return x


class TransformerEncoderBlock(nn.Module):
    """Standard ViT Transformer Encoder Block."""
    def __init__(self, embed_dim: int = 384, num_heads: int = 6, mlp_ratio: float = 4.0):
        super().__init__()
        self.norm1 = nn.LayerNorm(embed_dim)
        self.attn = MultiHeadSelfAttention(embed_dim=embed_dim, num_heads=num_heads)
        self.norm2 = nn.LayerNorm(embed_dim)
        self.mlp = MLPBlock(in_features=embed_dim, hidden_features=int(embed_dim * mlp_ratio))

    def forward(self, x: torch.Tensor, save_attn: bool = True) -> torch.Tensor:
        x = x + self.attn(self.norm1(x), save_attn=save_attn)
        x = x + self.mlp(self.norm2(x))
        return x


class FeedstockVisionTransformer(nn.Module):
    """
    Industry 4.0 Vision Transformer for Feedstock Quality Assessment.
    Outputs binary defect classification, multi-class categorization, and patch attention map.
    """
    def __init__(
        self,
        img_size: int = 224,
        patch_size: int = 16,
        in_channels: int = 3,
        embed_dim: int = 384,
        depth: int = 6,
        num_heads: int = 6,
        num_classes: int = 4
    ):
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.num_patches_per_side = img_size // patch_size
        self.n_patches = self.num_patches_per_side ** 2
        self.embed_dim = embed_dim

        self.patch_embed = PatchEmbedding(img_size, patch_size, in_channels, embed_dim)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, 1 + self.n_patches, embed_dim))
        self.pos_drop = nn.Dropout(p=0.05)

        self.blocks = nn.ModuleList([
            TransformerEncoderBlock(embed_dim=embed_dim, num_heads=num_heads)
            for _ in range(depth)
        ])
        self.norm = nn.LayerNorm(embed_dim)

        # Classification Heads
        self.defect_binary_head = nn.Sequential(
            nn.Linear(embed_dim, 128),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(128, 1)  # Sigmoid for binary presence
        )

        self.defect_multiclass_head = nn.Sequential(
            nn.Linear(embed_dim, 128),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(128, num_classes)  # 4 classes: Pitted, Scratched, Scale, Gouge
        )

        self.grade_head = nn.Sequential(
            nn.Linear(embed_dim, 64),
            nn.GELU(),
            nn.Linear(64, 3)  # Grade A, Grade B, Grade C
        )

        self._init_weights()

    def _init_weights(self):
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        nn.init.trunc_normal_(self.cls_token, std=0.02)
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.trunc_normal_(m.weight, std=0.02)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.LayerNorm):
                nn.init.constant_(m.bias, 0)
                nn.init.constant_(m.weight, 1.0)

    def forward(self, x: torch.Tensor, save_attn: bool = True) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        B = x.shape[0]
        x = self.patch_embed(x)
        cls_tokens = self.cls_token.expand(B, -1, -1)
        x = torch.cat((cls_tokens, x), dim=1)
        x = self.pos_drop(x + self.pos_embed)

        for block in self.blocks:
            x = block(x, save_attn=save_attn)

        x = self.norm(x)
        cls_feat = x[:, 0]  # [B, embed_dim]

        binary_logits = self.defect_binary_head(cls_feat)
        multiclass_logits = self.defect_multiclass_head(cls_feat)
        grade_logits = self.grade_head(cls_feat)

        return binary_logits, multiclass_logits, grade_logits

    def get_attention_rollout(self, target_shape: Tuple[int, int] = (256, 1600)) -> np.ndarray:
        """
        Computes attention rollout from [CLS] token across transformer layers.
        Returns 2D attention map resized to target_shape with range [0.0, 1.0].
        """
        all_attns = []
        for block in self.blocks:
            w = block.attn.last_attn_weights
            if w is not None:
                # Average across heads: [B, H, N, N] -> [N, N]
                avg_head = w[0].mean(dim=0)
                all_attns.append(avg_head)

        if not all_attns:
            return np.zeros(target_shape, dtype=np.float32)

        # Attention Rollout algorithm
        eye = torch.eye(all_attns[0].size(-1), device=all_attns[0].device)
        rollout = eye
        for a in all_attns:
            a_with_residual = 0.5 * a + 0.5 * eye
            a_norm = a_with_residual / a_with_residual.sum(dim=-1, keepdim=True)
            rollout = a_norm @ rollout

        # CLS token attention to spatial patches (excluding CLS token at index 0)
        cls_attn = rollout[0, 1:].detach().cpu().numpy()  # length 196

        # Reshape to 14 x 14 patch grid
        grid_size = self.num_patches_per_side
        grid_attn = cls_attn.reshape(grid_size, grid_size)

        # Normalize grid attention
        grid_min, grid_max = grid_attn.min(), grid_attn.max()
        if grid_max > grid_min:
            grid_attn = (grid_attn - grid_min) / (grid_max - grid_min)

        # Bilinear resize to original image dimensions (target_shape)
        grid_tensor = torch.from_numpy(grid_attn).unsqueeze(0).unsqueeze(0).float()
        upsampled = F.interpolate(grid_tensor, size=target_shape, mode='bicubic', align_corners=False)
        heatmap = upsampled.squeeze().clamp(0.0, 1.0).numpy()

        return heatmap
