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

# Example C code for demonstration
EXAMPLE_C_CODE = '''
#include <stdio.h>

int fibonacci(int n) {
    if (n <= 1)
        return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

int main() {
    int result = 0;
    for (int i = 0; i < 20; i++) {
        result += fibonacci(i);
    }
    printf("Result: %d\\n", result);
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
            
            features = extract_features_from_ir(ir_code)
            
            # Predict best optimization pass
            predicted_pass = predict_optimization_pass(features)
            
            # Measure execution time without optimization
            unoptimized_exe = compile_c_with_optimization(c_file_path, temp_dir, "O0")
            unoptimized_time = measure_execution_time(unoptimized_exe)
            
            # Measure execution time with predicted optimization
            optimized_exe = compile_c_with_optimization(c_file_path, temp_dir, predicted_pass)
            optimized_time = measure_execution_time(optimized_exe)
            
            # Calculate improvement
            time_improvement = ((unoptimized_time - optimized_time) / unoptimized_time) * 100
            
            # Read the IR code for display
            with open(ir_file_path, 'r') as f:
                ir_code_content = f.read()
            
            # Prepare result
            result = {
                'unoptimized_time': f"{unoptimized_time:.6f}",
                'optimized_time': f"{optimized_time:.6f}",
                'best_optimization': predicted_pass,
                'time_improvement': f"{time_improvement:.2f}%",
                'llvm_ir': ir_code_content,
                'features': {
                    'loop_count': features[0],
                    'func_calls': features[1],
                    'instr_count': features[2],
                    'has_branch': features[3],
                    'uses_memory': features[4],
                    'uses_global': features[5]
                }
            }
            
            return jsonify(result)
            
    except Exception as e:
        logger.exception("Error in optimization process")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
