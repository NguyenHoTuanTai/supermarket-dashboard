import torch
import torch.nn as nn
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import pickle

DATA_PATH = "data/cart.csv"
MODEL_PATH = "ai/deep_recommender.pth"
USER_ENCODER_PATH = "ai/user_enc.pkl"
PRODUCT_ENCODER_PATH = "ai/product_enc.pkl"

df = pd.read_csv(DATA_PATH)

# ==== ENCODERS ====
user_enc = LabelEncoder()
product_enc = LabelEncoder()

df["user_id"] = user_enc.fit_transform(df["Customer Name"])
df["product_id"] = product_enc.fit_transform(df["Product Name"])

with open(USER_ENCODER_PATH, "wb") as f:
    pickle.dump(user_enc, f)
with open(PRODUCT_ENCODER_PATH, "wb") as f:
    pickle.dump(product_enc, f)

# ===== MODEL =====
class RecommenderNet(nn.Module):
    def __init__(self, n_users, n_products, embed_dim=32):
        super().__init__()
        self.user_embed = nn.Embedding(n_users, embed_dim)
        self.product_embed = nn.Embedding(n_products, embed_dim)
        self.fc = nn.Sequential(
            nn.Linear(embed_dim * 2, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        u = self.user_embed(x[:, 0])
        p = self.product_embed(x[:, 1])
        return self.fc(torch.cat([u, p], dim=1))

X = torch.tensor(df[["user_id", "product_id"]].values, dtype=torch.long)
y = torch.ones(len(df), dtype=torch.float32)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RecommenderNet(df["user_id"].nunique(), df["product_id"].nunique())

loss_fn = nn.BCELoss()
opt = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(20):
    model.train()
    pred = model(X_train).squeeze()
    loss = loss_fn(pred, y_train)

    opt.zero_grad()
    loss.backward()
    opt.step()

torch.save(model.state_dict(), MODEL_PATH)
print(">> TRAIN DONE")
