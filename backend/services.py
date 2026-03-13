import os
import json
import base64
from anthropic import Anthropic

# Initialize the Anthropic client
client = Anthropic()

def parse_receipt(file_content: bytes, mime_type: str) -> dict:
    """
    Sends the receipt image/PDF to Claude for standard information extraction.
    Returns a dictionary matching the required schema.
    """
    
    encoded_file = base64.b64encode(file_content).decode('utf-8')
    media_type = mime_type
    
    if not media_type.startswith("image/") and media_type != "application/pdf":
        raise ValueError("Unsupported file type. Please upload an image or PDF.")
    
    if media_type == "application/pdf":
        document_block = {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": encoded_file
            }
        }
        content_blocks = [
            document_block,
            {"type": "text", "text": "Extract metadata from this receipt."}
        ]
    else:
        image_block = {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": encoded_file
            }
        }
        content_blocks = [
            image_block,
            {"type": "text", "text": "Extract metadata from this receipt."}
        ]


    prompt = """
You are an expert accountant and data extraction system.
Analyze the provided receipt/invoice and output a pure JSON object containing the exact following fields:
- "merchant" (string)
- "date" (string, YYYY-MM-DD format)
- "amount" (float)
- "currency" (string, preferably "CAD" or "USD")
- "suggested_category" (string, one of: "business", "donation", "medical", "personal", "other")
- "is_deductible" (boolean)

If any field cannot be confidently determined, provide a best guess or null if impossible to deduce.
Do not output any markdown formatting, preamble, or text other than the JSON object itself.
"""

    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1024,
        system=prompt,
        messages=[
            {
                "role": "user",
                "content": content_blocks
            }
        ]
    )

    try:
        # The response content should be a raw JSON string
        result_text = response.content[0].text.strip()
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        return json.loads(result_text.strip())
    except Exception as e:
        print(f"Failed to parse Claude response: {e}")
        return {
            "merchant": "Unknown",
            "date": None,
            "amount": 0.0,
            "currency": "CAD",
            "suggested_category": "other",
            "is_deductible": False,
            "error": "Failed to parse receipt correctly"
        }
