import re
import sys

def check_input(js_code):
    """
    Checks if the JavaScript code contains any input method such as:
      - prompt() for user input,
      - addEventListener() for user-triggered events,
      - document.getElementById() for DOM interactions,
      - navigator for device information,
      - fetch() or WebSocket() for online data streams,
      - FileReader() or file system calls (e.g., fs.read*) for file input.
    """
    patterns = [
        r'prompt\s*\(',                # user input
        r'addEventListener\s*\(',      # user event
        r'document\.getElementById\s*\(',  # DOM based input
        r'navigator\.',                # device info
        r'fetch\s*\(',                 # online data stream
        r'WebSocket\s*\(',             # online data stream
        r'FileReader\s*\(',            # file input in browsers
        r'fs\.\w+\s*\('               # Node.js file system operations
    ]
    for pattern in patterns:
        if re.search(pattern, js_code):
            return True
    return False

def check_list_usage(js_code):
    """
    Checks if the JavaScript code uses at least one list (array).
    Looks for patterns like:
      var/let/const <identifier> = [ ... ];
    """
    pattern = r'\b(?:var|let|const)\s+\w+\s*=\s*\['
    return re.search(pattern, js_code) is not None

def extract_brace_content(code, start_index):
    """
    Given a starting index (right after an opening brace '{'),
    returns the substring of code that is within the balanced braces,
    and the index right after the closing brace.
    """
    brace_count = 1
    i = start_index
    while i < len(code) and brace_count > 0:
        if code[i] == '{':
            brace_count += 1
        elif code[i] == '}':
            brace_count -= 1
        i += 1
    return code[start_index:i-1], i

def extract_functions(js_code):
    """
    Extracts traditional function definitions from the JavaScript code.
    Returns a list of dictionaries with keys: 'name', 'params', and 'body'.
    (Note: This simple extraction does not handle nested functions or all edge cases.)
    """
    function_pattern = r'function\s+(\w+)\s*\(([^)]*)\)\s*\{'
    functions = []
    for match in re.finditer(function_pattern, js_code):
        name = match.group(1)
        params = match.group(2).strip()
        start_index = match.end()
        body, _ = extract_brace_content(js_code, start_index)
        functions.append({'name': name, 'params': params, 'body': body})
    return functions

def check_procedure_presence(js_code):
    """
    Checks if the JavaScript code contains at least one student-developed procedure.
    A procedure is considered student-developed if it is a function with one or more parameters.
    Returns a list of such functions.
    """
    functions = extract_functions(js_code)
    # Filter out functions with empty parameter lists.
    student_functions = [func for func in functions if func['params'].strip() != ""]
    return student_functions

def check_procedure_elements(js_code):
    """
    For each student-developed procedure, verifies that its body contains:
      - At least one selection statement (if/switch) where one of its parameters is used.
      - At least one iteration statement (for/while).
      - A return statement.
    Returns a list of procedures that satisfy these conditions.
    """
    procedures = check_procedure_presence(js_code)
    valid_functions = []
    for func in procedures:
        params_list = [p.strip() for p in func['params'].split(',')]
        # Look for selection (if) and verify one of the parameters is used in its condition.
        selection_matches = re.findall(r'\bif\s*\(([^)]*)\)', func['body'])
        parameter_used = False
        for condition in selection_matches:
            for param in params_list:
                if re.search(r'\b' + re.escape(param) + r'\b', condition):
                    parameter_used = True
                    break
            if parameter_used:
                break
        has_selection = bool(selection_matches) and parameter_used

        # Check for iteration (for or while)
        has_iteration = bool(re.search(r'\b(for|while)\s*\(', func['body']))
        # Check for a return statement.
        has_return = bool(re.search(r'\breturn\b', func['body']))

        if has_selection and has_iteration and has_return:
            func['details'] = {
                'has_selection': has_selection,
                'has_iteration': has_iteration,
                'has_return': has_return
            }
            valid_functions.append(func)
    return valid_functions

def check_function_calls(js_code, functions):
    """
    For each function in 'functions', check whether there is at least one call to that function
    in the JavaScript code (outside its own definition).
    Returns a dictionary mapping function names to a boolean indicating if a call was found.
    """
    calls_found = {}
    for func in functions:
        # Look for function calls using the function name followed by '('
        pattern = r'\b' + re.escape(func['name']) + r'\s*\('
        matches = re.findall(pattern, js_code)
        # Assuming one match is the definition, we need at least a second occurrence to count as a call.
        calls_found[func['name']] = len(matches) > 1
    return calls_found

def check_output(js_code):
    """
    Checks if the JavaScript code includes output instructions such as:
      - console.log() for logging output,
      - alert() for pop-up messages,
      - document.write() for writing to the document.
    """
    patterns = [
        r'console\.log\s*\(',
        r'alert\s*\(',
        r'document\.write\s*\('
    ]
    for pattern in patterns:
        if re.search(pattern, js_code):
            return True
    return False

def run_tests(js_code):
    """
    Runs all the checks on the provided JavaScript code and returns a dictionary with results.
    """
    results = {}
    results['input_found'] = check_input(js_code)
    results['list_found'] = check_list_usage(js_code)
    # Separate check: the mere presence of a student-developed procedure.
    results['procedure_presence'] = check_procedure_presence(js_code)
    # Separate check: the procedures that have correct elements.
    results['procedure_elements'] = check_procedure_elements(js_code)
    # Check calls only on the procedures that passed the element check.
    results['calls'] = check_function_calls(js_code, results['procedure_elements'])
    results['output_found'] = check_output(js_code)
    return results

def build_summary(results):
    """
    Builds and returns a summary string that checks for:
    □ Instructions for input from one of the following:
      ◆ the user (including user actions that trigger events)
      ◆ a device
      ◆ an online data stream
      ◆ a file
    □ Use of at least one list (or other collection type)
    □ At least one student-developed procedure with:
      ◆ a defined name and one or more parameters (presence check)
    □ A student-developed procedure that includes:
      ◆ an algorithm with sequencing,
      ◆ selection (with the function's parameter used in the condition),
      ◆ iteration, and
      ◆ a return statement (element check)
    □ Calls to the student-developed procedure
    □ Instructions for output based on input and program functionality

    For each criterion, the summary reports "Passed" if it is met, or "Failed" otherwise.
    Finally, it reports an overall "Passed" if all criteria are met, or "Failed" otherwise.
    """
    summary_lines = []

    # Check for input instructions
    input_status = "Passed" if results.get('input_found', False) else "Failed"
    summary_lines.append("□ Instructions for input from one of the following: " + input_status)

    # Check for list/collection usage
    list_status = "Passed" if results.get('list_found', False) else "Failed"
    summary_lines.append("□ Use of at least one list (or other collection type): " + list_status)

    # Check for the presence of a student-developed procedure (with non-empty parameters)
    proc_presence_status = "Passed" if results.get('procedure_presence') and len(results['procedure_presence']) > 0 else "Failed"
    summary_lines.append("□ At least one student-developed procedure (with a defined name and parameters): " + proc_presence_status)

    # Check that at least one procedure includes the correct algorithm elements:
    proc_elements_status = "Passed" if results.get('procedure_elements') and len(results['procedure_elements']) > 0 else "Failed"
    summary_lines.append("□ A student-developed procedure that includes sequencing, selection (with parameter used), iteration, and a return statement: " + proc_elements_status)

    # Check for calls to the student-developed procedure(s) that meet the element criteria.
    calls_status = "Passed"
    if results.get('procedure_elements'):
        for func in results['procedure_elements']:
            if not results['calls'].get(func['name'], False):
                calls_status = "Failed"
                break
    else:
        calls_status = "Failed"
    summary_lines.append("□ Calls to your student-developed procedure: " + calls_status)

    # Check for output instructions
    output_status = "Passed" if results.get('output_found', False) else "Failed"
    summary_lines.append("□ Instructions for output (tactile, audible, visual, or textual): " + output_status)

    # Overall result: all individual checks must be Passed.
    overall = ("Passed" if (input_status == "Passed" and list_status == "Passed" and 
                            proc_presence_status == "Passed" and proc_elements_status == "Passed" and 
                            calls_status == "Passed" and output_status == "Passed")
               else "Failed")
    summary_lines.append("\nOverall: " + overall)

    return "\n".join(summary_lines)

def main(filename):
    try:
        with open(filename, 'r') as file:
            js_code = file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    results = run_tests(js_code)

    print("=== Checking for Input Methods ===")
    print("Input method found:", results['input_found'])

    print("\n=== Checking for List/Collection Usage ===")
    print("List/collection usage found:", results['list_found'])

    print("\n=== Checking for Student-Developed Procedure Presence ===")
    if results['procedure_presence']:
        print("Found procedure(s):")
        for func in results['procedure_presence']:
            print("  Function:", func['name'], "with parameters:", func['params'])
    else:
        print("No student-developed procedures found.")

    print("\n=== Checking for Procedure Correctness (Elements) ===")
    if results['procedure_elements']:
        print("Procedure(s) with correct elements:")
        for func in results['procedure_elements']:
            details = func.get('details', {})
            print("  Function:", func['name'], "with parameters:", func['params'])
            print("    Selection:", details.get('has_selection', False), 
                  "Iteration:", details.get('has_iteration', False), 
                  "Return:", details.get('has_return', False))
    else:
        print("No procedure meets the required algorithm elements.")

    print("\n=== Checking for Calls to Student-Developed Procedures ===")
    calls = results['calls']
    for func_name, called in calls.items():
        print(f"Function '{func_name}' called outside definition:", called)

    print("\n=== Checking for Output Instructions ===")
    print("Output instructions found:", results['output_found'])

    print("\nSummary:")
    print(build_summary(results))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_js.py <javascript_file.js>")
        sys.exit(1)
    main(sys.argv[1])
