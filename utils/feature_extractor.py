import re
import logging

logger = logging.getLogger(__name__)

def extract_features_from_ir(ir_text):
    """
    Extract features from LLVM IR code for optimization prediction
    
    Args:
        ir_text: The LLVM IR code as text
        
    Returns:
        Tuple of features (loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global)
    """
    try:
        # Count loops by looking for branch instructions to labels and loop metadata
        loop_count = len(re.findall(r'br label %', ir_text))
        
        # Better loop detection - looks for backward branches which often indicate loops
        backward_branches = len(re.findall(r'br .+, label %\S+ to label %\S+', ir_text))
        loop_count = max(loop_count, backward_branches)
        
        # Count function calls - basic and better detection of recursive patterns
        func_calls_basic = len(re.findall(r'call ', ir_text))
        
        # Check for recursive function patterns
        recursive_funcs = 0
        # Find function definitions
        func_defs = re.findall(r'define\s+.*?\s+@(\w+)\(', ir_text)
        for func in func_defs:
            # Check if the function calls itself
            if re.search(rf'call .+@{func}\(', ir_text):
                recursive_funcs += 1
                
        # For recursive functions, we should count them as having more function calls
        # since they'll execute many times at runtime
        func_calls = func_calls_basic
        if recursive_funcs > 0:
            # Weight recursive functions more heavily
            func_calls = max(func_calls, 8 * recursive_funcs)
        
        # Count total instructions (more accurately)
        actual_instructions = len(re.findall(r'^\s+[^;]\S+', ir_text, flags=re.MULTILINE))
        instr_count = actual_instructions
        
        # Check for conditional branches (if statements, switches)
        has_branch = 1 if re.search(r'br i1|switch', ir_text) else 0
        
        # Check for memory operations (more comprehensive)
        uses_memory = 1 if re.search(r'(alloca|load|store|malloc|free|call.*mem)', ir_text) else 0
        
        # Enhanced memory detection - check for stack allocations and array operations
        has_arrays = 1 if re.search(r'getelementptr|alloca .+x', ir_text) else 0
        uses_memory = 1 if (uses_memory or has_arrays) else 0
        
        # Check for global variable usage (more comprehensive)
        uses_global = 1 if re.search(r'@\w+\s*=', ir_text) or re.search(r'load .+@\w+', ir_text) else 0
        
        # Enhance features for better optimization detection
        # For Fibonacci-like recursive algorithms, we need to account for their complexity
        if recursive_funcs > 0 and loop_count > 0:
            # These will benefit greatly from memoization and aggressive optimization
            instr_count = max(instr_count, 50)  # Represent runtime complexity
        
        logger.debug(f"Extracted features: loops={loop_count}, calls={func_calls}, instructions={instr_count}, "
                    f"branches={has_branch}, memory={uses_memory}, globals={uses_global}")
        
        return loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global
        
    except Exception as e:
        logger.exception(f"Error extracting features: {str(e)}")
        # Return default values in case of error
        return 0, 0, 0, 0, 0, 0
