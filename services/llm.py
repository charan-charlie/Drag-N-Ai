import httpx
import json
import re
from typing import Type, TypeVar
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv
import os
load_dotenv()
T = TypeVar('T', bound=BaseModel)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL")



def extract_json_from_markdown(content: str) -> str:
    """
    Extract JSON from markdown code blocks if present.
    Handles patterns like:
    - ```json\n{...}\n```
    - ```\n{...}\n```
    - Just plain JSON without markdown
    """
    content = content.strip()
    
    # First, try to find JSON in markdown code blocks
    # Pattern: ```json or ``` followed by optional whitespace/newline, then content, then closing ```
    # Use greedy matching to get everything between the first ``` and last ```
    markdown_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
    match = re.search(markdown_pattern, content, re.DOTALL)
    
    if match:
        # Extract the content between the code blocks
        json_content = match.group(1).strip()
        # Remove any leading/trailing whitespace or newlines
        json_content = json_content.strip()
        return json_content
    
    # If no markdown code blocks found, try to find JSON object/array directly
    # Look for { or [ at the start
    json_start = re.search(r'[{\[]', content)
    if json_start:
        # Try to extract from the first { or [ to the end
        json_content = content[json_start.start():]
        # Try to find the matching closing bracket
        # This is a simple approach - for complex nested JSON, we rely on JSON parser
        return json_content.strip()
    
    # If no markdown code blocks found, return content as-is
    return content


async def call_llm(
    system_message: str,
    prompt: str,
    response_model: Type[T],
    model: str = "llama-3.3-70b-versatile",  # ✅ default Groq model
    temperature: float = 0.2,
    max_tokens: int = 1000,  # Increased default for structured responses
) -> dict:
    """
    Call Groq's LLM API and validate response using a Pydantic model.
    """

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found. Please add it to your .env file.")

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    messages = []
    if system_message:
        messages.append({"role": "system", "content": system_message})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": max_tokens,  # ✅ correct param for Groq
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(GROQ_API_URL, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()

            content = response_data["choices"][0]["message"]["content"].strip()
            
            # Extract JSON from markdown code blocks if present
            json_content = extract_json_from_markdown(content)
            
            # If extraction didn't change the content, try a more aggressive extraction
            if json_content == content and '```' in content:
                # Try to extract JSON more aggressively
                # Look for content between ```json and ``` or between ``` and ```
                patterns = [
                    r'```json\s*\n(.*?)\n```',  # ```json\n...\n```
                    r'```json\s*(.*?)```',      # ```json...```
                    r'```\s*\n(.*?)\n```',      # ```\n...\n```
                    r'```\s*(.*?)```',          # ```...```
                ]
                for pattern in patterns:
                    match = re.search(pattern, content, re.DOTALL)
                    if match:
                        json_content = match.group(1).strip()
                        break

            # Try direct JSON validation with Pydantic
            try:
                # First validate it's valid JSON
                parsed_json = json.loads(json_content)
                # Then validate with Pydantic
                return response_model.model_validate(parsed_json).model_dump()
            except json.JSONDecodeError as json_err:
                # If JSON parsing fails, try to fix truncated JSON
                # Look for the last complete closing brace
                last_brace = json_content.rfind('}')
                if last_brace > 0:
                    # Try to extract up to the last complete brace
                    try:
                        fixed_json = json_content[:last_brace + 1]
                        parsed_json = json.loads(fixed_json)
                        return response_model.model_validate(parsed_json).model_dump()
                    except (json.JSONDecodeError, ValidationError):
                        pass
                
                # Return error with context
                return {
                    "content": content[:500],  # First 500 chars for debugging
                    "error": f"JSON decode error: {str(json_err)}",
                    "extracted_length": len(json_content),
                    "extracted_preview": json_content[:200]
                }
            except ValidationError as ve:
                # Pydantic validation error
                return {
                    "content": content[:500],
                    "error": f"Validation error: {str(ve)}",
                    "extracted_length": len(json_content),
                    "extracted_preview": json_content[:200]
                }
            except Exception as e:
                # Any other error
                return {
                    "content": content[:500],
                    "error": f"Unexpected error: {str(e)}",
                    "extracted_length": len(json_content),
                    "extracted_preview": json_content[:200]
                }

        except httpx.HTTPStatusError as http_err:
            raise Exception(f"HTTP error: {http_err.response.status_code} - {http_err.response.text}")
        except Exception as e:
            raise Exception(f"Error calling Groq API: {str(e)}")