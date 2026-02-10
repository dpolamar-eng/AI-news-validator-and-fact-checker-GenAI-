import os
import requests
import zipfile
import io
import pandas as pd

# Using the "ISOT Fake News Dataset" or a similar balanced one
# For speed and reliability, I'll use a curated Kaggle-style CSV link that combines world news.
# This dataset contains ~45000 articles (Fake + True).
TRUE_URL = "https://raw.githubusercontent.com/laxmimerit/fake-news-dataset/master/True.csv"
FAKE_URL = "https://raw.githubusercontent.com/laxmimerit/fake-news-dataset/master/Fake.csv"

def download_and_merge():
    print("Downloading TRUE news dataset...")
    true_df = pd.read_csv(TRUE_URL)
    true_df['label'] = 'REAL'
    
    print("Downloading FAKE news dataset...")
    fake_df = pd.read_csv(FAKE_URL)
    fake_df['label'] = 'FAKE'
    
    print("Merging datasets...")
    df = pd.concat([true_df, fake_df], axis=0).sample(frac=1).reset_index(drop=True)
    
    # Save to our standard format
    df = df[['title', 'text', 'label']]
    df.to_csv("fake_or_real_news.csv", index=False)
    
    print(f"New High-Quality Dataset Saved! Shape: {df.shape}")
    print(df.head())

if __name__ == "__main__":
    download_and_merge()
