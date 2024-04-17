from sklearn.metrics import mean_squared_error
import glob
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from bs4 import BeautifulSoup
import pandas as pd
import re
from collections import Counter
import matplotlib.pyplot as plt


def find_symbols(text):
    # Convert to string in case of non-string data (like NaN)
    text = str(text)
    # Regular expression to find non-alphanumeric characters
    symbols = re.findall(r"[^\w\s]", text)
    return symbols


# Simple tokenize function to split text into words
def simple_tokenize(text):
    return text.split()


def preprocess_text(text):
    # Convert to string (in case of NaN or non-string)
    text = str(text)
    # Escape the hyphen or place it at the end of the character set
    cleaned_text = re.sub(r"[^\w\s.,()'\-]", '', text)
    return cleaned_text


df = pd.read_csv('/Users/ormeiri/Desktop/Work/sci-search/parser/data/combined_data_new.csv')
# Apply preprocessing to the text column
# df['cleaned_text'] = df['text'].apply(preprocess_text)
df['cleaned_text'] = df['extracted_text'].apply(preprocess_text)
# Find the most common words in the cleaned text
all_words = sum(df['cleaned_text'].apply(simple_tokenize), [])
word_counts = Counter(all_words)
most_common_words = word_counts.most_common(100)

# Extract just the words from the most_common_words
common_words_set = set([word for word, count in most_common_words])


# Function to remove most common words
def remove_common_words(text):
    return ' '.join([word for word in text.split() if word not in common_words_set])


# Remove the most common words from the cleaned_text
df['cleaned_text'] = df['cleaned_text'].apply(remove_common_words)

# Create a combined DataFrame (assuming 'quality_mean', 'accessibility_mean', 'ssi_mean' are columns in df)
combined_df = df[['cleaned_text', 'quality_mean', 'accessibility_mean']]

# Remove rows where any of the target variables are NaN
combined_df = df.dropna(subset=['quality_mean', 'accessibility_mean'])

# Split data into features (X) and target (y)
X = combined_df['cleaned_text']
# Create separate datasets for each target
y_quality = combined_df['quality_mean']
y_accessibility = combined_df['accessibility_mean']


# Train a Multilinear Regression model
def train_linear_model(X_train, y_train, X_test):
    pipeline = make_pipeline(TfidfVectorizer(), LinearRegression())
    pipeline.fit(X_train, y_train)
    predictions = pipeline.predict(X_test)
    return pipeline, predictions


# Function to get feature importances (coefficients in case of linear regression)
def get_feature_importances(pipeline):
    tfidf = pipeline.named_steps['tfidfvectorizer']
    linear_model = pipeline.named_steps['linearregression']
    feature_names = tfidf.get_feature_names_out()
    coefficients = linear_model.coef_
    importance = dict(zip(feature_names, coefficients))
    return importance


def plot_predictions(y_test, predictions, title):
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, predictions, alpha=0.5)
    plt.title(title)
    plt.xlabel("Actual Values")
    plt.ylabel("Predicted Values")
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--')  # Diagonal line
    plt.show()


# Train, evaluate and extract feature importances for each target
for y in [y_quality, y_accessibility]:
    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    # Train the model
    model, predictions = train_linear_model(X_train, y_train, X_test)

    # Evaluate the model
    mse = mean_squared_error(y_test, predictions)
    print(f"MSE for {y.name}: {mse}")

    # Plot actual vs predicted values
    plot_predictions(y_test, predictions, f"Actual vs Predicted for {y.name}")
    # Get feature importances
    importances = get_feature_importances(model)
    sorted_importances = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    print(f"Top 10 influential features for {y.name}: {sorted_importances[:10]}")
