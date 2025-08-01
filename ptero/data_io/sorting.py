import matplotlib.pyplot as plt
import re

def roman_to_int(r):
    mapping = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    total, prev = 0, 0
    for ch in r[::-1]:
        val = mapping.get(ch, 0)
        total = total - val if val < prev else total + val
        prev = val
    return total

def sort_key(line):
    # Remove leading/trailing square brackets.
    trimmed = line.strip("[]")
    
    # Move "log Hβ ergs/cm2/s" to end
    if trimmed.lower() == "log hβ ergs/cm2/s":
        return ("ZZZ", 9999, trimmed)
    
    # Use regex to capture the element, optional roman numeral, and remainder.
    m = re.match(r"^([A-Za-z]+)\s*([IVXLCDM]+)?(.*)$", trimmed)
    if m:
        element, numeral, rest = m.groups()
        return (element.upper(), roman_to_int(numeral) if numeral else 0, rest)
    return (trimmed, 0, "")