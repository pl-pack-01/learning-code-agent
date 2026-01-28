def write_file(working_directory, file_path, content):
    import os
    try:
       # Make working directory absolute
        working_directory_abs = os.path.abspath(working_directory)

        # Build and normalize target directory inside working_directory
        target_file = os.path.normpath(os.path.join(working_directory_abs, file_path))

        # Block access outside the working directory
        if os.path.commonpath([working_directory_abs, target_file]) != working_directory_abs:
            return f'Error: Cannot list "{target_file}" as it is outside the permitted working directory'

        # Must be a file
        if os.path.isdir(target_file):
            return f'Error: Cannot write to "{target_file}" as it is a directory'

        os.makedirs(os.path.dirname(target_file), exist_ok=True)

        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f"Error: {e}"