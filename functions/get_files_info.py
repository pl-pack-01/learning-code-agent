def get_files_info(working_directory, directory="."):
    import os

    try:
        # Make working directory absolute
        working_directory_abs = os.path.abspath(working_directory)

        # Build and normalize target directory inside working_directory
        target_directory = os.path.normpath(os.path.join(working_directory_abs, directory))

        # Block access outside the working directory
        if os.path.commonpath([working_directory_abs, target_directory]) != working_directory_abs:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # Must be a directory
        if not os.path.isdir(target_directory):
            return f'Error: "{directory}" is not a directory'

        files_info = []
        for entry in os.scandir(target_directory):
            try:
                size = os.path.getsize(entry.path)
            except OSError:
                size = 0
            files_info.append(f"- {entry.name}: file_size={size} bytes, is_dir={entry.is_dir()}")

        return "\n".join(files_info)

    except Exception as e:
        # No traceback; just return a message
        return f"Error: {e}"
