import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

def train_model():
    print("Loading dataset...")
    df = pd.read_csv("fake_or_real_news.csv")
    
    # Shuffle
    df = df.sample(frac=1).reset_index(drop=True)
    
    X = df['text']
    y = df['label']
    
    # Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Model (TF-IDF + Logistic Regression)...")
    
    # Create a pipeline (Vectorizer -> Classifier)
    # This handles tokenization automatically and is very robust
    model = Pipeline([
        ('tfidf', TfidfVectorizer(stop_words='english', max_df=0.7)),
        ('clf', LogisticRegression())
    ])
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc*100:.2f}%")
    
    # Save Model
    with open('fake_news_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("Model saved to fake_news_model.pkl")

if __name__ == "__main__":
    train_model()
