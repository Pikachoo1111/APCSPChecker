import re

def check_list_usage(py_code):
    """
    Checks for the use of at least one list (or other collection type)
    by searching for a list literal (e.g. [1, 2, 3]).
    """
    pattern = r'\[.*?\]'
    return bool(re.search(pattern, py_code))

def check_procedure_presence(py_code):
    """
    Checks for at least one student-developed procedure.
    Here a procedure is a function definition that has at least one parameter.
    """
    # Look for function definitions: def name(params):
    pattern = r'^\s*def\s+\w+\s*\(([^)]*)\)\s*:'
    matches = re.findall(pattern, py_code, re.MULTILINE)
    # Must have at least one non-empty parameter list.
    for params in matches:
        if params.strip():
            return True
    return False

def extract_functions(py_code):
    """
    Extracts function definitions along with their bodies.
    This simple regex looks for lines with a function header followed by an indented block.
    """
    # This regex expects at least one indented line after the header.
    function_pattern = r'^\s*def\s+(\w+)\s*\(([^)]*)\)\s*:\s*\n((?:\s+.*\n)+)'
    functions = re.findall(function_pattern, py_code, re.MULTILINE)
    # Each match is a tuple: (name, params, body)
    return [{'name': name, 'params': params, 'body': body} for name, params, body in functions]

def check_procedure_elements(py_code):
    """
    For a student-developed procedure (a function with non-empty parameters),
    verifies that its body includes:
      - Selection (an if-statement using at least one parameter),
      - Iteration (a for or while loop), and
      - A return statement.
    Returns True if at least one function satisfies these conditions.
    """
    functions = extract_functions(py_code)
    for func in functions:
        # Only consider functions with non-empty parameters.
        params = [p.strip() for p in func['params'].split(',') if p.strip()]
        if not params:
            continue
        body = func['body']
        # Check for a selection statement that uses one of the parameters.
        selection_found = False
        for param in params:
            # Look for an if-statement that uses the parameter.
            pattern = r'\bif\b.*\b' + re.escape(param) + r'\b'
            if re.search(pattern, body):
                selection_found = True
                break
        # Check for an iteration statement (for or while)
        iteration_found = bool(re.search(r'\b(for|while)\b', body))
        # Check for a return statement.
        return_found = bool(re.search(r'\breturn\b', body))
        if selection_found and iteration_found and return_found:
            return True
    return False

def check_function_calls(py_code):
    """
    Checks if any student-developed procedure (function with non-empty parameters)
    is called elsewhere in the code.
    This function extracts functions and then looks for an occurrence of the function name
    outside its definition (assuming one occurrence is in the definition itself).
    """
    functions = extract_functions(py_code)
    for func in functions:
        if func['params'].strip():
            pattern = r'\b' + re.escape(func['name']) + r'\s*\('
            occurrences = re.findall(pattern, py_code)
            # One occurrence is the definition; need at least one call.
            if len(occurrences) > 1:
                return True
    return False

def check_output(py_code):
    """
    Checks for instructions for output by searching for common output calls
    such as print(), logging methods, or sys.stdout.write().
    """
    patterns = [
        r'\bprint\s*\(',
        r'\blogging\.\w+\s*\(',
        r'\bsys\.stdout\.write\s*\('
    ]
    for pattern in patterns:
        if re.search(pattern, py_code):
            return True
    return False

def build_summary(py_code):
    """
    Builds a summary report that checks for:
      □ Use of at least one list (or other collection type)
      □ At least one student-developed procedure (with a defined name and parameters)
      □ A student-developed procedure that includes sequencing, selection (with parameter used), iteration, and a return statement
      □ Calls to your student-developed procedure
      □ Instructions for output (tactile, audible, visual, or textual)
    """
    summary_lines = []
    statuses = []
    list_status = "Passed" if check_list_usage(py_code) else "Failed"
    summary_lines.append("□ Use of at least one list (or other collection type): " + list_status)
    statuses.append(list_status)

    proc_presence_status = "Passed" if check_procedure_presence(py_code) else "Failed"
    summary_lines.append("□ At least one student-developed procedure (with a defined name and parameters): " + proc_presence_status)
    statuses.append(proc_presence_status)

    proc_elements_status = "Passed" if check_procedure_elements(py_code) else "Failed"
    summary_lines.append("□ A student-developed procedure that includes sequencing, selection (with parameter used), iteration, and a return statement: " + proc_elements_status)
    statuses.append(proc_elements_status)

    calls_status = "Passed" if check_function_calls(py_code) else "Failed"
    summary_lines.append("□ Calls to your student-developed procedure: " + calls_status)
    statuses.append(calls_status)

    output_status = "Passed" if check_output(py_code) else "Failed"
    summary_lines.append("□ Instructions for output (tactile, audible, visual, or textual): " + output_status)
    statuses.append(output_status)

    if(len(set(statuses)) == 1):
        summary_lines.append("Passed all tests!")
    else:
        summary_lines.append("Failed some/all tests")
        print(len(set(statuses)))
    return "\n".join(summary_lines)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py <filename.py>")
        sys.exit(1)
    filename = sys.argv[1]
    try:
        with open(filename, 'r') as file:
            python_code = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # results = run_tests(python_code)
    summary = build_summary(python_code)
    print(summary)
