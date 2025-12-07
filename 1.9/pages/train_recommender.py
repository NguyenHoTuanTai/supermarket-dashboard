import torch
import torch.nn as nn
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle
import os

# ===== LOAD DATASET =====
DATA_PATH = "data/cart.csv"
MODEL_PATH = "ai/deep_recommender.pth"
USER_ENCODER_PATH = "ai/user_enc.pkl"
PRODUCT_ENCODER_PATH = "ai/product_enc.pkl"

df = pd.read_csv(DATA_PATH)

# ===== ENCODE CATEGORICAL FIELDS =====
user_enc = LabelEncoder()
product_enc = LabelEncoder()

df["user_id"] = user_enc.fit_transform(df["Customer Name"])
df["product_id"] = product_enc.fit_transform(df["Product Name"])

# Lưu encoders để dùng khi inference
with open(USER_ENCODER_PATH, "wb") as f:
    pickle.dump(user_enc, f)

with open(PRODUCT_ENCODER_PATH, "wb") as f:
    pickle.dump(product_enc, f)

# ===== TẠO TENSOR =====
X = torch.tensor(df[["user_id", "product_id"]].values, dtype=torch.long)
y = torch.ones(len(df), dtype=torch.float32)  # giả sử mua = 1

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ===== DEEP LEARNING MODEL =====
class RecommenderNet(nn.Module):
    def __init__(self, n_users, n_products, embed_dim=32):
        super().__init__()
        self.user_embed = nn.Embedding(n_users, embed_dim)
        self.product_embed = nn.Embedding(n_products, embed_dim)
        self.fc = nn.Sequential(
            nn.Linear(embed_dim*2, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        user = self.user_embed(x[:, 0])
        product = self.product_embed(x[:, 1])
        out = torch.cat([user, product], dim=1)
        return self.fc(out)

# ===== INIT MODEL =====
model = RecommenderNet(
    n_users=df["user_id"].nunique(),
    n_products=df["product_id"].nunique()
)

loss_fn = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# ===== TRAIN =====
EPOCHS = 30
for epoch in range(EPOCHS):
    model.train()
    pred = model(X_train)
    loss = loss_fn(pred.squeeze(), y_train)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    if (epoch+1) % 5 == 0 or epoch == 0:
        with torch.no_grad():
            model.eval()
            val_pred = model(X_test)
            val_loss = loss_fn(val_pred.squeeze(), y_test)
        print(f"Epoch {epoch+1}/{EPOCHS} - Train Loss: {loss.item():.4f} - Val Loss: {val_loss.item():.4f}")

# ===== SAVE MODEL =====
torch.save(model.state_dict(), MODEL_PATH)
print(f">> Saved model to {MODEL_PATH}")
print(f">> Saved encoders: {USER_ENCODER_PATH}, {PRODUCT_ENCODER_PATH}")
