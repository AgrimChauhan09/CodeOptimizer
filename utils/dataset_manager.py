import os
import json
import logging
from datetime import datetime
from utils.compiler import compile_c_to_ir, compile_c_with_optimization
from utils.timer import measure_execution_time
from utils.feature_extractor import extract_features_from_ir

logger = logging.getLogger(__name__)

class DatasetManager:
    def __init__(self):
        self.training_codes_dir = "dataset/training_codes"
        self.optimization_results_dir = "dataset/optimization_results"
        self.dataset_file = "dataset/training_dataset.json"
        
        # Create directories if they don't exist
        os.makedirs(self.training_codes_dir, exist_ok=True)
        os.makedirs(self.optimization_results_dir, exist_ok=True)
    
    def find_best_optimization(self, c_code, code_name):
        """
        Test all optimization levels and find the best one
        """
        optimization_levels = ["O0", "O1", "O2", "O3", "Os", "Oz"]
        results = {}
        
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                c_file_path = os.path.join(temp_dir, f"{code_name}.c")
                
                # Save C code to file
                with open(c_file_path, 'w') as f:
                    f.write(c_code)
                
                # Test each optimization level
                for opt_level in optimization_levels:
                    try:
                        exe_path = compile_c_with_optimization(c_file_path, temp_dir, opt_level)
                        if exe_path:
                            exec_time = measure_execution_time(exe_path, runs=5)
                            results[opt_level] = exec_time
                    except Exception as e:
                        logger.warning(f"Failed to test {opt_level} for {code_name}: {str(e)}")
                        continue
                
                # Find the best optimization level (fastest execution)
                if results:
                    best_opt = min(results.keys(), key=lambda x: results[x])
                    return best_opt, results
                
        except Exception as e:
            logger.exception(f"Error finding best optimization for {code_name}: {str(e)}")
        
        return "O2", {}  # Default fallback
    
    def extract_and_store_features(self, c_code, code_name, best_optimization):
        """
        Extract features from C code and store with the best optimization
        """
        try:
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                c_file_path = os.path.join(temp_dir, f"{code_name}.c")
                
                # Save C code to file
                with open(c_file_path, 'w') as f:
                    f.write(c_code)
                
                # Compile to LLVM IR
                ir_file_path = compile_c_to_ir(c_file_path, temp_dir)
                if not ir_file_path:
                    return None
                
                # Extract features from IR
                with open(ir_file_path, 'r') as f:
                    ir_code = f.read()
                
                features_result = extract_features_from_ir(ir_code)
                
                if isinstance(features_result, dict):
                    # New format with detailed features
                    detailed_features = features_result
                    loop_count = detailed_features.get('loop_count', 0)
                    func_calls = detailed_features.get('func_calls', 0)
                    instr_count = detailed_features.get('instr_count', 0)
                    has_branch = detailed_features.get('has_branch', 0)
                    uses_memory = detailed_features.get('uses_memory', 0)
                    uses_global = detailed_features.get('uses_global', 0)
                elif len(features_result) == 7:
                    loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global, detailed_features = features_result
                else:
                    loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global = features_result
                    detailed_features = {}
                
                # Create training example
                training_example = {
                    "code_name": code_name,
                    "features": {
                        "loop_count": loop_count,
                        "func_calls": func_calls,
                        "instr_count": instr_count,
                        "has_branch": has_branch,
                        "uses_memory": uses_memory,
                        "uses_global": uses_global
                    },
                    "detailed_features": detailed_features,
                    "best_optimization": best_optimization,
                    "timestamp": datetime.now().isoformat()
                }
                
                return training_example
                
        except Exception as e:
            logger.exception(f"Error extracting features for {code_name}: {str(e)}")
            return None
    
    def add_code_to_dataset(self, c_code, code_name):
        """
        Add a new C code to the training dataset
        """
        # Save the C code file
        code_file_path = os.path.join(self.training_codes_dir, f"{code_name}.c")
        with open(code_file_path, 'w') as f:
            f.write(c_code)
        
        # Find the best optimization for this code
        best_opt, opt_results = self.find_best_optimization(c_code, code_name)
        
        # Extract features and create training example
        training_example = self.extract_and_store_features(c_code, code_name, best_opt)
        
        if training_example:
            # Add optimization results
            training_example["optimization_results"] = opt_results
            
            # Load existing dataset
            dataset = self.load_dataset()
            
            # Remove any existing entry with the same code name
            dataset = [item for item in dataset if item.get("code_name") != code_name]
            
            # Add new entry
            dataset.append(training_example)
            
            # Save updated dataset
            self.save_dataset(dataset)
            
            logger.info(f"Added {code_name} to dataset with best optimization: {best_opt}")
            return True
        
        return False
    
    def load_dataset(self):
        """
        Load the training dataset from file
        """
        if os.path.exists(self.dataset_file):
            try:
                with open(self.dataset_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading dataset: {str(e)}")
        
        return []
    
    def save_dataset(self, dataset):
        """
        Save the training dataset to file
        """
        try:
            with open(self.dataset_file, 'w') as f:
                json.dump(dataset, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving dataset: {str(e)}")
            return False
    
    def get_dataset_stats(self):
        """
        Get statistics about the current dataset
        """
        dataset = self.load_dataset()
        
        if not dataset:
            return {"total_codes": 0, "optimization_distribution": {}}
        
        stats = {
            "total_codes": len(dataset),
            "optimization_distribution": {},
            "feature_stats": {
                "avg_loop_count": 0,
                "avg_func_calls": 0,
                "avg_instr_count": 0,
                "codes_with_branches": 0,
                "codes_with_memory": 0,
                "codes_with_globals": 0
            }
        }
        
        # Count optimization distributions
        for item in dataset:
            best_opt = item.get("best_optimization", "Unknown")
            stats["optimization_distribution"][best_opt] = stats["optimization_distribution"].get(best_opt, 0) + 1
        
        # Calculate feature statistics
        if dataset:
            total_loop = sum(item["features"]["loop_count"] for item in dataset)
            total_func = sum(item["features"]["func_calls"] for item in dataset)
            total_instr = sum(item["features"]["instr_count"] for item in dataset)
            
            stats["feature_stats"]["avg_loop_count"] = total_loop / len(dataset)
            stats["feature_stats"]["avg_func_calls"] = total_func / len(dataset)
            stats["feature_stats"]["avg_instr_count"] = total_instr / len(dataset)
            stats["feature_stats"]["codes_with_branches"] = sum(1 for item in dataset if item["features"]["has_branch"])
            stats["feature_stats"]["codes_with_memory"] = sum(1 for item in dataset if item["features"]["uses_memory"])
            stats["feature_stats"]["codes_with_globals"] = sum(1 for item in dataset if item["features"]["uses_global"])
        
        return stats
    
    def build_initial_dataset(self):
        """
        Build the initial dataset from existing training codes
        """
        training_codes_added = 0
        
        # Process all existing .c files in training_codes directory
        if os.path.exists(self.training_codes_dir):
            for filename in os.listdir(self.training_codes_dir):
                if filename.endswith('.c'):
                    code_name = filename[:-2]  # Remove .c extension
                    file_path = os.path.join(self.training_codes_dir, filename)
                    
                    try:
                        with open(file_path, 'r') as f:
                            c_code = f.read()
                        
                        if self.add_code_to_dataset(c_code, code_name):
                            training_codes_added += 1
                            logger.info(f"Added {code_name} to training dataset")
                        
                    except Exception as e:
                        logger.warning(f"Failed to process {filename}: {str(e)}")
        
        return training_codes_added