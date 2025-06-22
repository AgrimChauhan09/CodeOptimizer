import os
import tempfile
import subprocess
import uuid
import logging
import json
from flask import Flask, render_template, request, jsonify, session
from utils.compiler import compile_c_to_ir, compile_c_with_optimization
from utils.timer import measure_execution_time
from utils.feature_extractor import extract_features_from_ir
from utils.model_predictor import predict_optimization_pass
from utils.enhanced_model_trainer import EnhancedModelTrainer
from utils.dataset_manager import DatasetManager
from utils.cache_manager import OptimizationCache

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

# Initialize the enhanced training system
model_trainer = EnhancedModelTrainer()
dataset_manager = DatasetManager()
optimization_cache = OptimizationCache()

# Initialize with enhanced default model for immediate functionality
try:
    logger.info("Initializing enhanced optimization system...")
    model_trainer.create_enhanced_default_model()
    logger.info("Optimization system ready")
except Exception as e:
    logger.error(f"Failed to initialize optimization system: {str(e)}")
    raise

# Example C code for demonstration - using a matrix multiplication example instead of Fibonacci
EXAMPLE_C_CODE = '''
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define SIZE 100

void matrix_multiply(int A[SIZE][SIZE], int B[SIZE][SIZE], int C[SIZE][SIZE]) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            C[i][j] = 0;
            for (int k = 0; k < SIZE; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}

int main() {
    int A[SIZE][SIZE], B[SIZE][SIZE], C[SIZE][SIZE];
    
    // Initialize matrices with random values
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            A[i][j] = rand() % 10;
            B[i][j] = rand() % 10;
        }
    }
    
    // Perform matrix multiplication
    matrix_multiply(A, B, C);
    
    // Print a sample value to verify
    printf("Sample value C[0][0]: %d\\n", C[0][0]);
    
    return 0;
}
'''

@app.route('/')
def index():
    return render_template('index.html', example_code=EXAMPLE_C_CODE)

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.get_json()
        c_code = data.get('code', '')
        
        if not c_code:
            return jsonify({'error': 'No code provided'}), 400
        
        # Check if this code has been optimized before
        cached_result = optimization_cache.get_cached_result(c_code)
        if cached_result:
            cached_data = cached_result['result']
            cached_data['cached'] = True
            cached_data['optimization_message'] = "This code has already been optimized. Using cached results for consistency."
            logger.info("Returning cached optimization result")
            return jsonify(cached_data)
        
        # Generate unique ID for this optimization run
        run_id = str(uuid.uuid4())
        
        # Create temporary directory for this optimization
        with tempfile.TemporaryDirectory() as temp_dir:
            c_file_path = os.path.join(temp_dir, f"{run_id}.c")
            
            # Save C code to file
            with open(c_file_path, 'w') as f:
                f.write(c_code)
            
            # Compile to LLVM IR without optimization
            ir_file_path = compile_c_to_ir(c_file_path, temp_dir)
            if not ir_file_path:
                return jsonify({'error': 'Failed to compile C code to LLVM IR'}), 500
            
            # Extract features from IR
            with open(ir_file_path, 'r') as f:
                ir_code = f.read()
            
            # Get both basic features and detailed optimization potential
            basic_features, detailed_features = None, None
            features_result = extract_features_from_ir(ir_code)
            
            # Handling the new return format
            if len(features_result) == 7:  # New format with detailed features dict
                loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global, detailed_features = features_result
                basic_features = (loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global)
            else:  # Old format fallback
                basic_features = features_result
                detailed_features = {}
            
            # Predict best optimization pass
            predicted_pass = predict_optimization_pass(basic_features)
            
            # Measure execution time without optimization (baseline)
            unoptimized_exe = compile_c_with_optimization(c_file_path, temp_dir, "O0")
            if not unoptimized_exe:
                return jsonify({'error': 'Failed to compile unoptimized version'}), 500
            
            unoptimized_time = measure_execution_time(unoptimized_exe)
            if unoptimized_time <= 0:
                return jsonify({'error': 'Failed to measure unoptimized execution time'}), 500
            
            # Test multiple optimization levels to find the actual best one
            optimization_results = {}
            for opt_level in ["O1", "O2", "O3", "Os", "Oz"]:
                opt_exe = compile_c_with_optimization(c_file_path, temp_dir, opt_level)
                if opt_exe:
                    opt_time = measure_execution_time(opt_exe)
                    if opt_time > 0:
                        optimization_results[opt_level] = opt_time
            
            if not optimization_results:
                return jsonify({'error': 'Failed to compile any optimized versions'}), 500
            
            # Find the actual best optimization level
            best_opt_level = min(optimization_results.keys(), key=lambda x: optimization_results[x])
            best_opt_time = optimization_results[best_opt_level]
            
            # Use the actual best optimization instead of predicted
            optimized_time = best_opt_time
            actual_best_optimization = best_opt_level
            
            # Calculate improvement with proper validation
            if optimized_time < unoptimized_time:
                time_improvement = ((unoptimized_time - optimized_time) / unoptimized_time) * 100
                optimization_message = f"Performance improved by {time_improvement:.2f}% with {actual_best_optimization} optimization"
            elif optimized_time == unoptimized_time:
                time_improvement = 0.0
                optimization_message = "No performance improvement detected. Code may already be optimal."
            else:
                # This shouldn't happen with proper measurement, but handle gracefully
                time_improvement = 0.0
                optimization_message = "Optimization did not improve performance. Using unoptimized version."
                optimized_time = unoptimized_time
                actual_best_optimization = "O0"
            
            # Read the IR code for display
            with open(ir_file_path, 'r') as f:
                ir_code_content = f.read()
            
            # Determine which specific optimizations were most beneficial
            optimization_details = []
            
            if detailed_features:
                # Check loop unrolling potential
                if detailed_features.get('loop_unroll_potential', 0) > 0:
                    optimization_details.append({
                        'name': 'Loop Unrolling',
                        'benefit': 'Reduced branch overhead',
                        'potential': detailed_features.get('loop_unroll_potential', 0)
                    })
                
                # Check function inlining potential
                if detailed_features.get('inlining_potential', 0) > 0:
                    optimization_details.append({
                        'name': 'Function Inlining',
                        'benefit': 'Removed function call cost',
                        'potential': detailed_features.get('inlining_potential', 0)
                    })
                
                # Check memory-to-register promotion potential
                if detailed_features.get('mem2reg_potential', 0) > 0:
                    optimization_details.append({
                        'name': 'Memory-to-Register Promotion',
                        'benefit': 'Faster memory access',
                        'potential': detailed_features.get('mem2reg_potential', 0)
                    })
                
                # Check constant folding potential
                if detailed_features.get('const_folding_potential', 0) > 0:
                    optimization_details.append({
                        'name': 'Constant Folding',
                        'benefit': 'Simplified computation',
                        'potential': detailed_features.get('const_folding_potential', 0)
                    })
                
                # Check dead code elimination potential
                if detailed_features.get('dce_potential', 0) > 0:
                    optimization_details.append({
                        'name': 'Dead Code Elimination',
                        'benefit': 'Removed unused code',
                        'potential': detailed_features.get('dce_potential', 0)
                    })
            
            # Prepare result with actual best optimization
            result = {
                'unoptimized_time': f"{unoptimized_time:.6f}",
                'optimized_time': f"{optimized_time:.6f}",
                'best_optimization': actual_best_optimization,
                'predicted_optimization': predicted_pass,
                'time_improvement': f"{time_improvement:.2f}%",
                'optimization_message': optimization_message,
                'llvm_ir': ir_code_content,
                'optimization_details': optimization_details,
                'optimization_results': optimization_results,
                'features': {
                    'loop_count': basic_features[0],
                    'func_calls': basic_features[1],
                    'instr_count': basic_features[2],
                    'has_branch': basic_features[3],
                    'uses_memory': basic_features[4],
                    'uses_global': basic_features[5]
                },
                'cached': False
            }
            
            # Cache the result to prevent inconsistent outputs on resubmission
            optimization_cache.cache_result(c_code, result)
            
            return jsonify(result)
            
    except Exception as e:
        logger.exception("Error in optimization process")
        return jsonify({'error': str(e)}), 500

@app.route('/contribute', methods=['POST'])
def contribute_code():
    """
    Allow users to contribute C code to the training dataset
    This improves the model's accuracy over time
    """
    try:
        data = request.get_json()
        c_code = data.get('code', '')
        code_name = data.get('name', '').strip()
        
        if not c_code or not code_name:
            return jsonify({'error': 'Both code and name are required'}), 400
        
        # Validate code name (basic sanitization)
        import re
        if not re.match(r'^[a-zA-Z0-9_]+$', code_name):
            return jsonify({'error': 'Code name can only contain letters, numbers, and underscores'}), 400
        
        # Add the code to the training dataset
        success = model_trainer.update_model_with_new_code(c_code, code_name)
        
        if success:
            # Get updated dataset statistics
            stats = dataset_manager.get_dataset_stats()
            
            return jsonify({
                'success': True,
                'message': f'Code "{code_name}" added to training dataset successfully!',
                'dataset_stats': stats
            })
        else:
            return jsonify({'error': 'Failed to add code to dataset'}), 500
            
    except Exception as e:
        logger.exception("Error in code contribution process")
        return jsonify({'error': str(e)}), 500

@app.route('/dataset-stats')
def get_dataset_stats():
    """
    Get current dataset statistics
    """
    try:
        stats = dataset_manager.get_dataset_stats()
        model_info = model_trainer.get_model_performance_info()
        
        return jsonify({
            'dataset_stats': stats,
            'model_info': model_info
        })
        
    except Exception as e:
        logger.exception("Error getting dataset stats")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
