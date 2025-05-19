import re
import logging

logger = logging.getLogger(__name__)

def extract_features_from_ir(ir_text):
    """
    Extract features from LLVM IR code for optimization prediction
    
    Args:
        ir_text: The LLVM IR code as text
        
    Returns:
        Dictionary with all extracted features and optimization potential scores
    """
    try:
        features = {}
        
        # Count loops by looking for branch instructions to labels and loop metadata
        loop_count = len(re.findall(r'br label %', ir_text))
        
        # Better loop detection - looks for backward branches which often indicate loops
        backward_branches = len(re.findall(r'br .+, label %\S+ to label %\S+', ir_text))
        loop_count = max(loop_count, backward_branches)
        features['loop_count'] = loop_count
        
        # Check loop unrolling potential
        loop_unroll_potential = 0
        if loop_count > 0:
            # Check for loops with constant bounds (good candidates for unrolling)
            const_loops = len(re.findall(r'icmp .+ %\w+, \d+', ir_text))
            simple_increments = len(re.findall(r'add .+ %\w+, 1', ir_text))
            
            if const_loops > 0 and simple_increments > 0:
                loop_unroll_potential = min(const_loops, simple_increments)
        features['loop_unroll_potential'] = loop_unroll_potential
        
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
        features['func_calls'] = func_calls
        
        # Check inlining potential - small functions are good candidates
        small_funcs = 0
        for func in func_defs:
            func_pattern = rf'define[^@]+@{func}[^{{]+{{(.*?)}}' 
            func_match = re.search(func_pattern, ir_text, re.DOTALL)
            if func_match:
                func_body = func_match.group(1)
                # Count instructions in function body
                instr_count_func = len(re.findall(r'^\s+[^;]\S+', func_body, flags=re.MULTILINE))
                if instr_count_func < 20:  # Small functions are good for inlining
                    small_funcs += 1
        features['inlining_potential'] = small_funcs
        
        # Count total instructions (more accurately)
        actual_instructions = len(re.findall(r'^\s+[^;]\S+', ir_text, flags=re.MULTILINE))
        instr_count = actual_instructions
        features['instr_count'] = instr_count
        
        # Check for conditional branches (if statements, switches)
        has_branch = 1 if re.search(r'br i1|switch', ir_text) else 0
        features['has_branch'] = has_branch
        
        # Check for memory operations
        alloca_count = len(re.findall(r'alloca ', ir_text))
        load_count = len(re.findall(r'load ', ir_text))
        store_count = len(re.findall(r'store ', ir_text))
        
        # mem2reg optimization potential (converting stack vars to registers)
        mem2reg_potential = min(alloca_count, load_count + store_count)
        features['mem2reg_potential'] = mem2reg_potential
        
        # Check memory operations (more comprehensive)
        uses_memory = 1 if re.search(r'(alloca|load|store|malloc|free|call.*mem)', ir_text) else 0
        
        # Enhanced memory detection - check for stack allocations and array operations
        has_arrays = 1 if re.search(r'getelementptr|alloca .+x', ir_text) else 0
        uses_memory = 1 if (uses_memory or has_arrays) else 0
        features['uses_memory'] = uses_memory
        
        # Check for global variable usage
        uses_global = 1 if re.search(r'@\w+\s*=', ir_text) or re.search(r'load .+@\w+', ir_text) else 0
        features['uses_global'] = uses_global
        
        # Check constant folding potential - how many operations use constants
        const_ops = len(re.findall(r'(add|sub|mul|div|shl|lshr|ashr|and|or|xor) .+, \d+', ir_text))
        features['const_folding_potential'] = const_ops
        
        # Check dead code elimination potential
        # Look for assignments that aren't used
        all_assigns = re.findall(r'%(\w+) =', ir_text)
        unused_vars = 0
        for var in all_assigns:
            # Check if variable is used elsewhere (exclude its definition)
            var_def = re.search(rf'%{var} =', ir_text)
            if var_def:
                var_def_pos = var_def.start()
                # Look for usage after definition
                rest_of_ir = ir_text[var_def_pos+len(var_def.group(0)):]
                if not re.search(rf'[^%]%{var}[^0-9a-zA-Z_]', rest_of_ir):
                    unused_vars += 1
        features['dce_potential'] = unused_vars
        
        # Enhance features for better optimization detection
        # For Fibonacci-like recursive algorithms, we need to account for their complexity
        if recursive_funcs > 0 and loop_count > 0:
            # These will benefit greatly from memoization and aggressive optimization
            features['instr_count'] = max(features['instr_count'], 50)  # Represent runtime complexity
        
        logger.debug(f"Extracted features: {features}")
        
        # For backward compatibility, return the tuple of basic features as well
        return (
            features['loop_count'], 
            features['func_calls'], 
            features['instr_count'], 
            features['has_branch'], 
            features['uses_memory'], 
            features['uses_global'], 
            features
        )
        
    except Exception as e:
        logger.exception(f"Error extracting features: {str(e)}")
        # Return default values in case of error
        return 0, 0, 0, 0, 0, 0, {}
