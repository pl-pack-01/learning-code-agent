def get_file_content(working_directory, file_path):
    from config import characters_to_read
    import os
    try:
        # Make working directory absolute
        working_directory_abs = os.path.abspath(working_directory)

        # Build and normalize target directory inside working_directory
        target_file = os.path.normpath(os.path.join(working_directory_abs, file_path))

        # Block access outside the working directory
        if os.path.commonpath([working_directory_abs, target_file]) != working_directory_abs:
            return f'Error: Cannot list "{file_path}" as it is outside the permitted working directory'
        
        # Must be a file
        if not os.path.isfile(target_file):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(characters_to_read)
            if f.read(1):
                content += f'[...File "{file_path}" truncated at {characters_to_read} characters]'
 
        return content
    except Exception as e:
        return f"Error: {e}"