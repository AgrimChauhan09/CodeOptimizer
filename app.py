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

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")

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
            
            # Measure execution time without optimization
            unoptimized_exe = compile_c_with_optimization(c_file_path, temp_dir, "O0")
            unoptimized_time = measure_execution_time(unoptimized_exe)
            
            # Measure execution time with predicted optimization
            optimized_exe = compile_c_with_optimization(c_file_path, temp_dir, predicted_pass)
            optimized_time = measure_execution_time(optimized_exe)
            
            # Check if optimization actually improved performance
            optimization_message = ""
            if optimized_time >= unoptimized_time:
                optimization_message = "No performance improvement detected. Code may already be optimal."
                time_improvement = 0.0
            else:
                # Calculate improvement percentage
                time_improvement = ((unoptimized_time - optimized_time) / unoptimized_time) * 100
                optimization_message = f"Performance improved by {time_improvement:.2f}%"
            
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
            
            # Prepare result
            result = {
                'unoptimized_time': f"{unoptimized_time:.6f}",
                'optimized_time': f"{optimized_time:.6f}",
                'best_optimization': predicted_pass,
                'time_improvement': f"{time_improvement:.2f}%",
                'optimization_message': optimization_message,
                'llvm_ir': ir_code_content,
                'optimization_details': optimization_details,
                'features': {
                    'loop_count': basic_features[0],
                    'func_calls': basic_features[1],
                    'instr_count': basic_features[2],
                    'has_branch': basic_features[3],
                    'uses_memory': basic_features[4],
                    'uses_global': basic_features[5]
                }
            }
            
            return jsonify(result)
            
    except Exception as e:
        logger.exception("Error in optimization process")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
