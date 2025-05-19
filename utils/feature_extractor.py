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
        # Count loops by looking for branch instructions to labels
        loop_count = len(re.findall(r'br label %', ir_text))
        
        # Count function calls
        func_calls = len(re.findall(r'call ', ir_text))
        
        # Count total instructions
        instr_count = len(re.findall(r'^\s*\S+', ir_text, flags=re.MULTILINE))
        
        # Check for conditional branches (if statements, switches)
        has_branch = 1 if re.search(r'br i1|switch', ir_text) else 0
        
        # Check for memory operations
        uses_memory = 1 if re.search(r'(alloca|load|store)', ir_text) else 0
        
        # Check for global variable usage
        uses_global = 1 if re.search(r'@', ir_text) else 0
        
        logger.debug(f"Extracted features: loops={loop_count}, calls={func_calls}, instructions={instr_count}, "
                    f"branches={has_branch}, memory={uses_memory}, globals={uses_global}")
        
        return loop_count, func_calls, instr_count, has_branch, uses_memory, uses_global
        
    except Exception as e:
        logger.exception(f"Error extracting features: {str(e)}")
        # Return default values in case of error
        return 0, 0, 0, 0, 0, 0
