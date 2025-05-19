import os
import joblib
import logging
from sklearn.ensemble import RandomForestClassifier

logger = logging.getLogger(__name__)

# Path to the trained model
MODEL_PATH = os.environ.get("MODEL_PATH", "./models/trained_model.pkl")

def load_model():
    """
    Load the trained ML model for optimization prediction
    
    Returns:
        Loaded model or None if loading fails
    """
    try:
        if os.path.exists(MODEL_PATH) and os.path.getsize(MODEL_PATH) > 100:
            model = joblib.load(MODEL_PATH)
            logger.debug(f"Successfully loaded model from {MODEL_PATH}")
            return model
        else:
            logger.warning(f"Valid model file not found at {MODEL_PATH}, creating default model")
            # Create a simple default model
            model = create_default_model()
            return model
    except Exception as e:
        logger.exception(f"Error loading model: {str(e)}")
        return create_default_model()
        
def create_default_model():
    """Create a default model when the trained model is not available"""
    logger.info("Creating default RandomForest model")
    model = RandomForestClassifier(n_estimators=15, random_state=42)
    # Train with more comprehensive data
    # Features: loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global
    X = [
        [0, 0, 10, 0, 0, 0],  # Very simple code - O1
        [1, 1, 20, 1, 1, 0],  # Moderate code - O2
        [3, 5, 50, 1, 1, 1],  # Complex code - O3
        [0, 2, 15, 0, 1, 1],  # Memory-focused - Os
        [2, 3, 30, 1, 0, 0],  # Computation-focused - O3
        # Adding Fibonacci-like recursive patterns
        [1, 9, 50, 1, 1, 0],  # Recursive function with loop - O3
        [0, 10, 25, 1, 1, 0], # Pure recursion - O3
        [0, 8, 40, 1, 1, 0],  # Recursive with memoization potential - O3
        # Loops with different characteristics
        [4, 2, 45, 1, 1, 0],  # Loop-heavy computation - O2
        [5, 1, 60, 1, 1, 0],  # Very loop-intensive - O3
        # Memory patterns
        [2, 3, 35, 1, 1, 1],  # Memory operations with globals - O2
        [1, 2, 30, 0, 1, 1],  # Memory operations without branches - Os
    ]
    y = ["O1", "O2", "O3", "Os", "O3", "O3", "O3", "O3", "O2", "O3", "O2", "Os"]
    model.fit(X, y)
    
    # Save the model for future use
    try:
        joblib.dump(model, MODEL_PATH)
        logger.info(f"Default model saved to {MODEL_PATH}")
    except Exception as e:
        logger.warning(f"Could not save default model: {str(e)}")
        
    return model

def predict_optimization_pass(features):
    """
    Predict the best optimization pass based on code features
    
    Args:
        features: Tuple of features (loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global)
        
    Returns:
        Predicted optimization pass (O1, O2, O3, etc.)
    """
    try:
        model = load_model()
        
        if model:
            # Use the trained model for prediction
            prediction = model.predict([features])[0]
            logger.debug(f"Model predicted optimization pass: {prediction}")
            return prediction
        else:
            # Fallback to rule-based prediction if model is not available
            return rule_based_prediction(features)
            
    except Exception as e:
        logger.exception(f"Error in prediction: {str(e)}")
        # Default to O2 as a safe fallback
        return "O2"

def rule_based_prediction(features):
    """
    Rule-based predictor when the ML model is not available
    
    Args:
        features: Tuple of features (loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global)
        
    Returns:
        Predicted optimization pass (O1, O2, O3, etc.)
    """
    loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global = features
    
    # Recursive algorithms like Fibonacci benefit greatly from O3's function inlining
    # High func_calls with branching is a strong indicator of recursive code
    if func_calls > 7 and has_branch == 1:
        return "O3"  # Aggressive optimization for recursive functions
    
    # Complex code with lots of loops and function calls benefits from O3
    elif loop_count >= 2 and func_calls > 5:
        return "O3"
    
    # Memory-intensive code often benefits from O2
    elif uses_memory == 1 and instr_count > 30:
        return "O2"
        
    # Compute-bound code with moderate complexity benefits from O2
    elif loop_count > 0 and instr_count > 25:
        return "O2"
    
    # Code with branches but not too complex is good for O1
    elif has_branch == 1 and instr_count < 30:
        return "O1"
    
    # Simple code or global variable usage might benefit from Os (optimize for size)
    elif uses_global == 1 or instr_count < 15:
        return "Os"
    
    # Default to O2 as a balanced optimization
    else:
        return "O2"
