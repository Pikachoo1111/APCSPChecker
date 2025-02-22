def process_numbers(numbers):
    # Ensure there's a selection with one of the parameters
    if len(numbers) > 0:  
        result = 0
        for num in numbers:  # Iteration
            result += num
        return result  # Return statement
    return None

# Call the function
nums = [1, 2, 3, 4]
result = process_numbers(nums)
print(result)
