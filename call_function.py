import json
from google.genai import types
from functions.get_files_info import get_files_info
from functions.run_python_file import run_python_file
from functions.write_file_content import write_file
from functions.get_file_content import get_file_content

# Shared function map
function_map = {
    "get_file_content": get_file_content,
    "write_file_content": write_file,
    "get_files_info": get_files_info,
    "run_python_file": run_python_file,
}

# ============== GEMINI ==============
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from"
            )
        }
    )
)

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads and returns the content of a file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file to read"
            )
        },
        required=["file_path"]
    )
)

schema_write_file_content = types.FunctionDeclaration(
    name="write_file_content",
    description="Writes content to a file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the file"
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write"
            )
        },
        required=["file_path", "content"]
    )
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a Python file and returns the output",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the Python file"
            )
        },
        required=["file_path"]
    )
)

available_functions_gemini = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file_content,
        schema_run_python_file,
    ]
)

def call_function_gemini(function_call, verbose=False):
    function_name = function_call.name or ""

    if verbose:
        print(f"Calling function: {function_name}({function_call.args})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[types.Part.from_function_response(
                name=function_name,
                response={"error": f"Unknown function: {function_name}"}
            )]
        )

    try:
        args = dict(function_call.args) if function_call.args else {}
        args["working_directory"] = "."
        result = function_map[function_name](**args)

        return types.Content(
            role="tool",
            parts=[types.Part.from_function_response(
                name=function_name,
                response={"result": result}
            )]
        )
    except Exception as e:
        return types.Content(
            role="tool",
            parts=[types.Part.from_function_response(
                name=function_name,
                response={"error": str(e)}
            )]
        )


# ============== OPENAI ==============
available_functions_openai = [
    {
        "type": "function",
        "function": {
            "name": "get_files_info",
            "description": "Lists files in a specified directory",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory path to list files from"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_file_content",
            "description": "Reads and returns the content of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file to read"}
                },
                "required": ["file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file_content",
            "description": "Writes content to a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the file"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["file_path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python_file",
            "description": "Runs a Python file and returns the output",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to the Python file"}
                },
                "required": ["file_path"]
            }
        }
    }
]

def call_function_openai(tool_call, verbose=False):
    function_name = tool_call.function.name

    if verbose:
        print(f"Calling function: {function_name}({tool_call.function.arguments})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in function_map:
        return json.dumps({"error": f"Unknown function: {function_name}"})

    try:
        args = json.loads(tool_call.function.arguments)
        args["working_directory"] = "."
        result = function_map[function_name](**args)

        return json.dumps({"result": result})
    except Exception as e:
        return json.dumps({"error": str(e)})