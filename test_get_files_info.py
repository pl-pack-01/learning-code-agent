
from functions.get_files_info import get_files_info

print("Results for current directory:")
print(get_files_info("calculator", "."))

print("\nResults for 'pkg' directory:")
print(get_files_info("calculator", "pkg"))

print("\nResults for '/bin' directory:")
print(get_files_info("calculator", "/bin"))

print("\nResults for '../' directory:")
print(get_files_info("calculator", "../"))