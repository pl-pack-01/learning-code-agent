import os, argparse
from dotenv import load_dotenv
from google import genai
from google.genai import types
from prompt import system_prompt

from call_function import available_functions, call_function

def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()


    config = types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt,
    )

    if api_key is None:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    else:
        client = genai.Client(api_key=api_key)
        messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
        for content in range(20):
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=messages,
                config=config,
            )

            # Add candidates to messages for next iteration
            if response.candidates:
                for candidate in response.candidates:
                    messages.append(candidate.content)            

            if args.verbose:
                print("User prompt: ", args.user_prompt)
                print("Prompt tokens: ", response.usage_metadata.prompt_token_count)
                print("Response tokens: ", response.usage_metadata.candidates_token_count)

            # Check for function calls
            if response.function_calls:
                function_results = []
                for function_call in response.function_calls:
                    function_call_result = call_function(function_call, verbose=args.verbose)

                    if not function_call_result.parts:
                        raise Exception("Function call result has empty parts list")
                    if function_call_result.parts[0].function_response is None:
                        raise Exception("Function call result has no function_response")
                    if function_call_result.parts[0].function_response.response is None:
                        raise Exception("Function call result has no response")
                    
                    function_results.append(function_call_result.parts[0])
                    
                    if args.verbose:
                        print(f"-> {function_call_result.parts[0].function_response.response}")

                messages.append(types.Content(role="user", parts=function_results))
            else:
                print("Function call result: ", function_call_result)
                print(response.text)
                break
        else:
            print("Max iterations reached without final response.")
            exit(1)

if __name__ == "__main__":
    main()
