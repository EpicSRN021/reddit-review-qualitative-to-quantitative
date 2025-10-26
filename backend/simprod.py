"""Helper script for requesting three similar products from an LLM."""

from __future__ import annotations

import asyncio
import json
import os
import sys
from typing import List

from Classification import MODEL, client

DEBUG = os.getenv("SIMPROD_DEBUG") == "1"


def _parse_response(raw_response: str) -> List[str]:
    """Parse the LLM response, aiming for a JSON payload."""
    try:
        payload = json.loads(raw_response)
        similar = payload.get("similar_products")
        if isinstance(similar, list):
            return [str(item).strip() for item in similar if item]
    except json.JSONDecodeError:
        pass

    # Fall back to splitting on newlines when the model ignores the JSON instruction.
    return [line.strip("-• ").strip() for line in raw_response.splitlines() if line.strip()]


async def fetch_similar_products(product_name: str) -> List[str]:
    """Ask the LLM for three similar products."""
    prompt = f"""
    You are a helpful retail assistant.
    The user is considering the product "{product_name}".
    Recommend exactly three similar consumer products that they might also like.
    Reply ONLY in strict JSON using this schema:
    {{
        "similar_products": ["name 1", "name 2", "name 3"]
    }}
    """

    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1000,  # Increased for reasoning models that use tokens internally
        )
        if DEBUG:
            print(f"DEBUG - Full response object: {response}")
            print(f"DEBUG - Response choices: {response.choices}")
        
        content = response.choices[0].message.content
        if DEBUG:
            print("LLM raw response:", repr(content))
        
        if content is None or content.strip() == "":
            print(f"WARNING: LLM returned empty content. Model: {MODEL}")
            return []
            
        return _parse_response(content)
    except Exception as e:
        print(f"ERROR calling Azure OpenAI API: {type(e).__name__}: {e}")
        if DEBUG:
            import traceback
            traceback.print_exc()
        return []


async def _amain(product_name: str) -> None:
    products = await fetch_similar_products(product_name)
    payload = {"similar_products": products[:3]}
    if DEBUG:
        print("Parsed similar products:", products)
    print(json.dumps(payload, indent=2))


def main() -> None:
    if len(sys.argv) > 1:
        product_name = " ".join(sys.argv[1:]).strip()
    else:
        product_name = input("Enter a product: ").strip()

    if not product_name:
        print("Please provide a product name.")
        raise SystemExit(1)

    asyncio.run(_amain(product_name))


if __name__ == "__main__":
    main()
