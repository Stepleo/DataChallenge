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
train_data_path = 'data/X_train.csv'
test_data_path = 'data/X_test.csv'
inference_data_paths = [
    'data/ssp1_df.csv',
    'data/ssp2_df.csv',
    'data/ssp5_df.csv'
]

# Load the training data
train_df = load_data(train_data_path)
test_df = load_data(test_data_path)

# Features and target
features = ['longitude', 'latitude', 'air_temperature', 'precipitation']
X_train = train_df[features]
y_train = train_df['target']

X_test = test_df[features]
y_test = test_df['target']

X = pd.concat([X_train, X_test])
y = pd.concat([y_train, y_test])

print("Training Data Summary:")
print(X.info())
print("\n")
print("Target Distribution:")
print(y.value_counts(normalize=True))
print("\n")

# Initialize the scaler
scaler = StandardScaler()

# Fit the scaler on the training data and transform both training and test data
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Check if the model is already trained and saved
model_path = 'model_target.pkl'
scaler_path = 'scaler_target.pkl'

if os.path.exists(model_path) and os.path.exists(scaler_path):
    del X, y, X_train, y_train, X_train_scaled, X_test_scaled
    gc.collect()
    print("Loading existing model and scaler...")
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
else:
    print("Training a new model...")
    # Train a Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)

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
    X_new = df[features]

    # Scale the features
    X_new_scaled = scaler.transform(X_new)

    # Make predictions
    df['predicted_target'] = model.predict(X_new_scaled)

    # Save the new predictions
    output_path = f'{path}_target_predictions.csv'
    df.to_csv(output_path, index=False)
    print(f"Predictions saved to {output_path}\n")

    # Analyze the results
    print(f"Inference Dataset {i} - Target Analysis:")
    print(df['predicted_target'].value_counts(normalize=True))
    print("\n")

# Compare the overall target predictions across the datasets
overall_targets = []
for i, path in enumerate(inference_data_paths, start=1):
    df = load_data(f'{path}_target_predictions.csv')
    overall_targets.append(df['predicted_target'].value_counts(normalize=True))

print("Overall Target Predictions for Each Lifestyle Hypothesis:")
for i, target_dist in enumerate(overall_targets, start=1):
    print(f"Lifestyle Hypothesis {i}:")
    print(target_dist)
