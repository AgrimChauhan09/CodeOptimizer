import os
import subprocess
import logging

logger = logging.getLogger(__name__)

def compile_c_to_ir(c_file_path, output_dir):
    """
    Compile C code to LLVM IR without optimization
    
    Args:
        c_file_path: Path to the C file
        output_dir: Directory where the IR file will be saved
        
    Returns:
        Path to the generated IR file or None if compilation failed
    """
    try:
        # Get the filename without extension
        filename = os.path.splitext(os.path.basename(c_file_path))[0]
        ir_file_path = os.path.join(output_dir, f"{filename}.ll")
        
        # Compile C code to LLVM IR with clang
        cmd = ['clang', '-S', '-emit-llvm', '-O0', c_file_path, '-o', ir_file_path]
        process = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if os.path.exists(ir_file_path):
            logger.debug(f"Successfully compiled {c_file_path} to {ir_file_path}")
            return ir_file_path
        else:
            logger.error(f"IR file not generated despite successful compilation: {process.stderr}")
            return None
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Compilation failed: {e.stderr}")
        return None
    except Exception as e:
        logger.exception(f"Error in compile_c_to_ir: {str(e)}")
        return None

def compile_c_with_optimization(c_file_path, output_dir, opt_level):
    """
    Compile C code with the specified optimization level
    
    Args:
        c_file_path: Path to the C file
        output_dir: Directory where the compiled executable will be saved
        opt_level: Optimization level (O0, O1, O2, O3, Os, Oz)
        
    Returns:
        Path to the compiled executable or None if compilation failed
    """
    try:
        # Get the filename without extension
        filename = os.path.splitext(os.path.basename(c_file_path))[0]
        exe_file_path = os.path.join(output_dir, f"{filename}_{opt_level}")
        
        # Compile C code with the specified optimization level
        cmd = ['clang', f'-{opt_level}', c_file_path, '-o', exe_file_path]
        process = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        if os.path.exists(exe_file_path):
            # Make the executable file executable
            os.chmod(exe_file_path, 0o755)
            logger.debug(f"Successfully compiled {c_file_path} to {exe_file_path} with {opt_level}")
            return exe_file_path
        else:
            logger.error(f"Executable not generated despite successful compilation: {process.stderr}")
            return None
            
    except subprocess.CalledProcessError as e:
        logger.error(f"Compilation with {opt_level} failed: {e.stderr}")
        return None
    except Exception as e:
        logger.exception(f"Error in compile_c_with_optimization: {str(e)}")
        return None
