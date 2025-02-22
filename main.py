import pythonCheck
import jsCheck
import sys

args = sys.argv

if len(args) != 2:
    print("Correct usage: python3 main.py <file.js or file.py>")
    sys.exit(1)

isPython = args[1].endswith(".py")
file_extension = args[1].split('.')[-1]

if file_extension not in ["py", "js"]:
    sys.exit("Unsupported file extension. Please provide a .py or .js file.")

try:
    with open(args[1], 'r') as file:
        file_content = file.read()
        
        # Debug print
        print("File content read successfully.")

        if isPython:
            # results = pythonCheck.run_tests(file_content)  # Should return a dictionary
            # print("Results from run_tests (Python):", results)  # Check the dictionary structure
            print(pythonCheck.build_summary(file_content))      # Pass dictionary to build_summary
        else:
            results = jsCheck.run_tests(file_content)      # Should return a dictionary
            # print("Results from run_tests (JS):", results)  # Check the dictionary structure
            print(jsCheck.build_summary(results))          # Pass dictionary to build_summary

except FileNotFoundError:
    sys.exit(f"File not found: {args[1]}")
except IOError as e:
    sys.exit(f"Error reading file: {str(e)}")
except Exception as e:
    sys.exit(f"Unexpected error: {str(e)}")
