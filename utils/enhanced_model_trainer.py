import os
import json
import logging
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from utils.dataset_manager import DatasetManager

logger = logging.getLogger(__name__)

class EnhancedModelTrainer:
    def __init__(self):
        self.dataset_manager = DatasetManager()
        self.model_path = "./models/trained_model.pkl"
        self.model = None
        
    def train_model_from_dataset(self):
        """
        Train the model using the real C code dataset
        """
        # Load the dataset
        dataset = self.dataset_manager.load_dataset()
        
        if len(dataset) < 5:
            logger.warning("Not enough training data. Building initial dataset...")
            added_codes = self.dataset_manager.build_initial_dataset()
            logger.info(f"Added {added_codes} codes to initial dataset")
            dataset = self.dataset_manager.load_dataset()
        
        if len(dataset) < 5:
            logger.warning("Still not enough data. Using enhanced rule-based system.")
            return self.create_enhanced_default_model()
        
        # Prepare training data
        X = []
        y = []
        
        for item in dataset:
            features = item["features"]
            # Extract feature values in the correct order
            feature_vector = [
                features["loop_count"],
                features["func_calls"], 
                features["instr_count"],
                features["has_branch"],
                features["uses_memory"],
                features["uses_global"]
            ]
            X.append(feature_vector)
            y.append(item["best_optimization"])
        
        X = np.array(X)
        y = np.array(y)
        
        logger.info(f"Training model with {len(X)} real code examples")
        logger.info(f"Optimization distribution: {np.unique(y, return_counts=True)}")
        
        # Split data for training and validation
        if len(X) > 10:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        else:
            X_train, X_test, y_train, y_test = X, X, y, y
        
        # Train the model
        self.model = RandomForestClassifier(
            n_estimators=50,
            max_depth=10,
            random_state=42,
            class_weight='balanced'  # Handle imbalanced classes
        )
        
        self.model.fit(X_train, y_train)
        
        # Evaluate the model
        if len(X_test) > 0:
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            logger.info(f"Model accuracy: {accuracy:.2f}")
            logger.debug(f"Classification report:\n{classification_report(y_test, y_pred)}")
        
        # Save the trained model
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save model: {str(e)}")
            return False
    
    def create_enhanced_default_model(self):
        """
        Create an enhanced default model with better training data
        """
        logger.info("Creating enhanced default model with comprehensive training data")
        
        # Enhanced training data based on common C code patterns
        X = [
            # Simple programs - O1 is usually best
            [0, 0, 8, 0, 0, 0],    # Hello world type - O1
            [0, 1, 12, 0, 1, 0],   # Simple I/O - O1
            [1, 0, 15, 1, 1, 0],   # Simple loop - O1
            
            # Moderate complexity - O2 is usually best
            [1, 2, 25, 1, 1, 0],   # Loop with function calls - O2
            [2, 1, 30, 1, 1, 0],   # Nested loops - O2
            [0, 3, 20, 1, 1, 1],   # Multiple functions with globals - O2
            [1, 1, 35, 1, 1, 0],   # Moderate algorithm - O2
            
            # Complex programs - O3 is usually best
            [3, 5, 60, 1, 1, 0],   # Matrix operations - O3
            [2, 8, 55, 1, 1, 0],   # Recursive algorithms - O3
            [4, 3, 70, 1, 1, 0],   # Complex nested loops - O3
            [1, 10, 45, 1, 1, 0],  # Heavy recursion - O3
            [5, 4, 80, 1, 1, 0],   # Very complex algorithms - O3
            
            # Memory-intensive - O2 or Os
            [2, 2, 40, 1, 1, 1],   # Array processing with globals - O2
            [1, 1, 25, 0, 1, 1],   # Memory operations without branches - Os
            [0, 2, 18, 0, 1, 1],   # Simple memory ops - Os
            
            # Size-critical programs - Os
            [0, 1, 10, 0, 0, 1],   # Simple with globals - Os
            [1, 0, 12, 0, 1, 1],   # Small with memory and globals - Os
        ]
        
        y = [
            "O1", "O1", "O1",                    # Simple programs
            "O2", "O2", "O2", "O2",              # Moderate complexity
            "O3", "O3", "O3", "O3", "O3",        # Complex programs
            "O2", "Os", "Os",                    # Memory-intensive
            "Os", "Os"                           # Size-critical
        ]
        
        self.model = RandomForestClassifier(
            n_estimators=30,
            max_depth=8,
            random_state=42,
            class_weight='balanced'
        )
        
        self.model.fit(X, y)
        
        # Save the model
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            joblib.dump(self.model, self.model_path)
            logger.info(f"Enhanced default model saved to {self.model_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save enhanced default model: {str(e)}")
            return False
    
    def update_model_with_new_code(self, c_code, code_name):
        """
        Add new code to dataset and retrain the model
        """
        success = self.dataset_manager.add_code_to_dataset(c_code, code_name)
        
        if success:
            # Retrain the model with the updated dataset
            return self.train_model_from_dataset()
        
        return False
    
    def get_model_performance_info(self):
        """
        Get information about the current model performance
        """
        dataset_stats = self.dataset_manager.get_dataset_stats()
        
        model_info = {
            "dataset_size": dataset_stats["total_codes"],
            "optimization_distribution": dataset_stats["optimization_distribution"],
            "feature_stats": dataset_stats["feature_stats"],
            "model_type": "Real Data Trained" if dataset_stats["total_codes"] >= 5 else "Enhanced Default"
        }
        
        return model_info