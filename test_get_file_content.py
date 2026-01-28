
from functions.get_file_content import get_file_content

print("Results for 'lorem.txt' file:")
print(get_file_content("calculator", "lorem.txt"))

print("\nResults for 'main.py' file:")
print(get_file_content("calculator", "main.py"))

print("\nResults for 'pkg/calculator.py' file:")
print(get_file_content("calculator", "pkg/calculator.py"))

print("\nResults for '/bin/cat' file:")
print(get_file_content("calculator", "/bin/cat")) # (this should return an error string)

print("\nResults for 'pkg/does_not_exist.py' file:")
print(get_file_content("calculator", "pkg/does_not_exist.py")) # (this should return an error string)