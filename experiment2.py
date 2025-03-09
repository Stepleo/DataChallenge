import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib
import os
import gc

# Function to load data from a specified path
def load_data(file_path):
    return pd.read_csv(file_path)

# Paths to the data files
train_data_path = 'data/flood_risk_data.csv'  # Replace with your actual file path
inference_data_paths = [
    'data/ssp1_df.csv',  # Replace with your actual file path
    'data/ssp2_df.csv',  # Replace with your actual file path
    'data/ssp5_df.csv'   # Replace with your actual file path
]

# Load the training data
train_df = load_data(train_data_path)

# Convert target to categorical levels
train_df['target_category'] = pd.qcut(train_df['target'], q=4, labels=False)

# Features and target
features = ['Runoff', 'SnowDepth']
X = train_df[features]
y = train_df['target_category']

print("Training Data Summary:")
print(X.info())
print("\n")
print("Target Distribution:")
print(y.value_counts(normalize=True))
print("\n")

# StratifiedShuffleSplit for cross-validation
cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=42)

# Check if the model is already trained and saved
model_path = 'model.pkl'
if os.path.exists(model_path):
    del X, y
    gc.collect()
    print("Loading existing model...")
    model = joblib.load(model_path)
else:
    print("Training a new model...")
    # Train a Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)

    # Evaluate the model using cross-validation
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring='accuracy', verbose=2)
    print(f"Cross-validation accuracy scores: {cv_scores}")
    print(f"Mean cross-validation accuracy: {cv_scores.mean():.4f}")

    # Fit the model on the entire training data
    model.fit(X, y)

    # Save the model
    joblib.dump(model, model_path)
    del X, y
    gc.collect()

# Process each inference dataset separately to manage memory
for i, path in enumerate(inference_data_paths, start=1):
    print(f"Processing Inference Dataset {i}...")
    df = load_data(path)

    # Prepare the features for inference
    df['Runoff'] = df['total_runoff'].fillna(0)  # Assuming missing values are filled with 0
    df['SnowDepth'] = df['snowfall_flux']  # Assuming snowfall_flux is equivalent to SnowDepth

    # Make predictions
    X_new = df[features]
    df['predicted_target_category'] = model.predict(X_new)

    # Save the new predictions
    output_path = f'{path}_predictions.csv'
    df.to_csv(output_path, index=False)
    print(f"Predictions saved to {output_path}\n")

    # Analyze the results
    print(f"Inference Dataset {i} - Flood Risk Analysis:")
    print(df['predicted_target_category'].value_counts(normalize=True))
    print("\n")

# Compare the overall flood risks across the datasets
overall_risks = []
for i, path in enumerate(inference_data_paths, start=1):
    df = load_data(f'{path}_predictions.csv')
    overall_risks.append(df['predicted_target_category'].mean())

print("Overall Flood Risks for Each Lifestyle Hypothesis:")
for i, risk in enumerate(overall_risks, start=1):
    print(f"Lifestyle Hypothesis {i}: {risk:.4f}")
