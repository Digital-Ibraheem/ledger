import os
import json
import base64
from anthropic import Anthropic

# Initialize the Anthropic client
# Assumes ANTHROPIC_API_KEY is set in the environment
client = Anthropic()

def parse_receipt(file_content: bytes, mime_type: str) -> dict:
    """
    Sends the receipt image/PDF to Claude for standard information extraction.
    Returns a dictionary matching the required schema.
    """
    
    # We use a base64 encoded string for the image/pdf
    encoded_file = base64.b64encode(file_content).decode('utf-8')
    
    # Handle PDF slightly differently in Claude API vs Images, but for now we'll
    # assume standard vision passing logic. If it's a PDF we'd normally extract text 
    # or pass it as a document if supported, but assuming standard image base64 here.
    # Note: If PDF parsing fails with standard vision approach, we might need pdf-specific handling.
    
    media_type = mime_type
    if not media_type.startswith("image/") and media_type != "application/pdf":
        raise ValueError("Unsupported file type. Please upload an image or PDF.")
        
    # Standardize PDF mime type for Claude if needed or raise if specific handling is required
    # For now, let's treat it generically or assume the user uploads images mostly. 
    # claude-3-5-sonnet-20241022 supports PDF documents via the document block type.
    
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
        model="claude-3-5-sonnet-20241022",
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
        # Clean up in case claude wrapped it in code blocks despite instructions
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
            
        return json.loads(result_text.strip())
    except Exception as e:
        print(f"Failed to parse Claude response: {e}")
        # Return a safe fallback rather than failing completely
        return {
            "merchant": "Unknown",
            "date": None,
            "amount": 0.0,
            "currency": "CAD",
            "suggested_category": "other",
            "is_deductible": False,
            "error": "Failed to parse receipt correctly"
        }
