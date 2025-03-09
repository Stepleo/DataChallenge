import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler
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
features = ['longitude', 'latitude', 'Runoff', 'SnowDepth']
X = train_df[features]
y = train_df['target_category']

print("Training Data Summary:")
print(X.info())
print("\n")
print("Target Distribution:")
print(y.value_counts(normalize=True))
print("\n")

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Initialize the scaler
scaler = StandardScaler()

# Fit the scaler on the training data and transform both training and test data
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Check if the model is already trained and saved
model_path = 'model2.pkl'
scaler_path = 'scaler2.pkl'

if os.path.exists(model_path) and os.path.exists(scaler_path):
    del X, y, X_train, y_train, X_train_scaled, X_test_scaled
    gc.collect()
    print("Loading existing model and scaler...")
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
else:
    print("Training a new model...")
    # Train a Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100)

    # Fit the model on the scaled training data
    model.fit(X_train_scaled, y_train)

    # Evaluate the model on the scaled test data
    y_pred = model.predict(X_test_scaled)
    print("Test Set Classification Report:")
    print(classification_report(y_test, y_pred))

    # Save the model and scaler
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    del X, y, X_train, y_train, X_test, y_test, X_train_scaled, X_test_scaled
    gc.collect()

# Process each inference dataset separately to manage memory
for i, path in enumerate(inference_data_paths, start=1):
    print(f"Processing Inference Dataset {i}...")
    df = load_data(path)

    # Prepare the features for inference
    df['Runoff'] = df['total_runoff'].fillna(0)  # Assuming missing values are filled with 0
    df['SnowDepth'] = df['snowfall_flux']  # Assuming snowfall_flux is equivalent to SnowDepth

    # Scale the features
    X_new = df[features]
    X_new_scaled = scaler.transform(X_new)

    # Make predictions
    df['predicted_target_category'] = model.predict(X_new_scaled)

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
