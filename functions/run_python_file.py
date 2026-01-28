def run_python_file(working_directory, file_path, args=None):
    import os, subprocess
    try:
        # Make working directory absolute
        working_directory_abs = os.path.abspath(working_directory)

        # Build and normalize target directory inside working_directory
        target_file = os.path.normpath(os.path.join(working_directory_abs, file_path))

        # Block access outside the working directory
        if os.path.commonpath([working_directory_abs, target_file]) != working_directory_abs:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        # Check if file exists
        if not os.path.exists(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'

        # Must be a file
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        
        # File must have .py extension
        if not target_file.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'
        
        # Prepare command
        command = ["python", target_file]
        if args:
            command.extend(args)

        # run the command
        result = subprocess.run(
            command,
            cwd=working_directory_abs,  # Set working directory
            capture_output=True,         # Capture stdout and stderr
            text=True,                   # Decode output to strings
            timeout=30                   # 30 second timeout
        )
        # Build output string
        output_parts = []
        
        # Check for non-zero exit code
        if result.returncode != 0:
            output_parts.append(f"Process exited with code {result.returncode}")
        
        # Check if any output was produced
        if not result.stdout and not result.stderr:
            output_parts.append("No output produced")
        else:
            # Include stdout if present
            if result.stdout:
                output_parts.append(f"STDOUT:\n{result.stdout}")
            
            # Include stderr if present
            if result.stderr:
                output_parts.append(f"STDERR:\n{result.stderr}")
        
        # Return the output string
        return "\n".join(output_parts)
        
    except subprocess.TimeoutExpired:
        return f"Error: Process timed out after 30 seconds"
    except Exception as e:
        return f"Error: executing Python file: {e}"