def reverse_string(string):
    # Base case
    if len(string) == 0:
        return ""

    # Recursive case
    return reverse_string(string[1:]) + string[0]

print(reverse_string("pmc"))