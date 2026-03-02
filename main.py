import os, argparse, json
from dotenv import load_dotenv
from prompt import system_prompt
from call_function import (
    available_functions_claude,
    available_functions_gemini,
    available_functions_openai,
    call_function_claude,
    call_function_gemini,
    call_function_openai,
)

def run_claude(client, messages, args):
    for iteration in range(20):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            system=system_prompt,
            messages=messages,
            tools=available_functions_claude,
            max_tokens=8096,
        )

        if args.verbose:
            print("Input tokens:", response.usage.input_tokens)
            print("Output tokens:", response.usage.output_tokens)

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = call_function_claude(block, verbose=args.verbose)
                    if args.verbose:
                        print(f"-> {result}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            for block in response.content:
                if hasattr(block, "text"):
                    print(block.text)
            return

    print("Max iterations reached without final response.")
    exit(1)


def run_gemini(client, messages, config, args):
    from google.genai import types
    
    for iteration in range(20):
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=messages,
            config=config,
        )

        if response.candidates:
            messages.append(response.candidates[0].content)

        if args.verbose:
            print("Prompt tokens:", response.usage_metadata.prompt_token_count)
            print("Response tokens:", response.usage_metadata.candidates_token_count)

        if response.function_calls:
            function_results = []
            for function_call in response.function_calls:
                result = call_function_gemini(function_call, verbose=args.verbose)

                if not result.parts:
                    raise Exception("Function call result has empty parts list")
                if result.parts[0].function_response is None:
                    raise Exception("Function call result has no function_response")
                if result.parts[0].function_response.response is None:
                    raise Exception("Function call result has no response")

                function_results.append(result.parts[0])

                if args.verbose:
                    print(f"-> {result.parts[0].function_response.response}")

            messages.append(types.Content(role="tool", parts=function_results))
        else:
            print(response.text)
            return
    
    print("Max iterations reached without final response.")
    exit(1)


def run_openai(client, messages, args):
    for iteration in range(20):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=available_functions_openai,
        )

        if args.verbose:
            print("Prompt tokens:", response.usage.prompt_tokens)
            print("Response tokens:", response.usage.completion_tokens)

        message = response.choices[0].message
        messages.append(message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                result = call_function_openai(tool_call, verbose=args.verbose)

                if args.verbose:
                    print(f"-> {result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result,
                })
        else:
            print(message.content)
            return
    
    print("Max iterations reached without final response.")
    exit(1)


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Chatbot")
    parser.add_argument("user_prompt", type=str, help="User prompt")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--provider", type=str, default="gemini", choices=["gemini", "openai", "claude"], help="AI provider (gemini, openai, or claude)")
    args = parser.parse_args()

    if args.verbose:
        print("User prompt:", args.user_prompt)
        print("Provider:", args.provider)

    if args.provider == "gemini":
        from google import genai
        from google.genai import types

        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key is None:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")

        client = genai.Client(api_key=api_key)
        messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]
        config = types.GenerateContentConfig(
            tools=[available_functions_gemini],
            system_instruction=system_prompt,
        )
        run_gemini(client, messages, config, args)

    elif args.provider == "openai":
        from openai import OpenAI

        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")

        client = OpenAI(api_key=api_key)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": args.user_prompt}
        ]
        run_openai(client, messages, args)

    elif args.provider == "claude":
        import anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key is None:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables.")

        client = anthropic.Anthropic(api_key=api_key)
        messages = [{"role": "user", "content": args.user_prompt}]
        run_claude(client, messages, args)


if __name__ == "__main__":
    main()