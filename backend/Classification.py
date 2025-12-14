import asyncio
import os
import re
import ast
import json
from sentence_transformers import SentenceTransformer
import json
import pandas as pd
import torch 
import numpy as np
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset 
from dotenv import load_dotenv
load_dotenv()
embedder = SentenceTransformer("all-MiniLM-L6-v2")
class SimpleRegressor(nn.Module):
    def __init__(self, input_dim=384, output_dim=5):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, output_dim)
        )
    def forward(self, x):
        return self.fc(x)
model = SimpleRegressor()
model.load_state_dict(torch.load(r"C:\Users\qiu19\Unwrapathon\reddit-review-qualitative-to-quantitative\backend\model_weights.pt",
    map_location="cpu"))
model.eval()

async def analyze_comment(reviews: list[str]) -> list[float]:
    x = embedder.encode(reviews)
    x = torch.tensor(x).float()
    with torch.no_grad():
        preds = model(x)
    return preds.tolist()









    
    
