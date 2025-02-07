from openai import OpenAI
from typing import List, Tuple, Dict
import json
import os
from dotenv import load_dotenv
import time
load_dotenv()


def read_txt_file(file_path: str) -> List[Dict]:
    """
    Read a TXT file and return a list of dictionaries containing
    speaker and text.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    parsed_blocks = []
    
    for line in lines:
        if line.strip():  # Ignore empty lines
            speaker, text = line.split(':', 1)
            parsed_blocks.append({
                'speaker': speaker.strip(),
                'text': text.strip()
            })
    
    return parsed_blocks


def clean_transcript_chunk(chunk: List[Dict], 
                           context: str, 
                           client: OpenAI,
                           system_message: str = "Clean the transcript",
                           ) -> List[Dict]:
    """
    Clean a chunk of transcript text while maintaining context and style.
    
    Args:
        chunk: List of dictionaries with 'speaker' and 'text'
        context: Previous context to maintain consistency
        client: OpenAI client instance
        max_tokens: Maximum tokens to process at once
    """
    prompt = {
        "context": context,
        "chunk": chunk
    }



    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": json.dumps(prompt)}
        ],
        temperature=0.2,
        response_format= { "type": "json_object" }  
    )
  
    cleaned_chunk = json.loads(response.choices[0].message.content)
    return cleaned_chunk

def clean_txt_file(input_file: str, 
                   output_file: str,
                   chunk_size: int = 5,
                   system_message: str = "Clean the transcript") -> None:
    """
    Clean an entire TXT file while maintaining context.
    
    Args:
        input_file: Path to input TXT file
        output_file: Path to save cleaned TXT file
        chunk_size: Number of conversation lines to process at once
        system_message: System message to display to the model
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    txt_blocks = read_txt_file(input_file)
    cleaned_blocks = []
    context = ""
    system_msg = system_message + """\n\nReturn json output without context in the format: {"chunk": [{'speaker': '', 'text':''},...]}."""
    
    # Process in chunks to maintain context
    total_chunks = len(txt_blocks)//chunk_size + 1
    for i in range(0, len(txt_blocks), chunk_size):
        print(f"Processing chunk {i//chunk_size + 1}/{total_chunks}")
        chunk = txt_blocks[i:i+chunk_size]
        
        # Clean the chunk while maintaining context
        max_retries = 5
        retries = 0
        cleaned_chunk = None

        while retries < max_retries:
            try:
                cleaned_chunk = clean_transcript_chunk(chunk, context, client, system_msg)
                if "chunk" in cleaned_chunk:
                    break  # Exit loop if the response is correct
                else:
                    raise KeyError("Missing 'chunk' in response")
            except KeyError as e:
                retries += 1
                time.sleep(5)
                print(f"Error: {e}. Retrying {retries}/{max_retries}...")

        if cleaned_chunk is None or "chunk" not in cleaned_chunk:
            raise RuntimeError("Failed to clean chunk after multiple retries")
        
        response = cleaned_chunk["chunk"]
        # Append cleaned blocks
        cleaned_blocks.extend(response)
        
        # Update context with the cleaned text
        context = ' '.join(block['text'] for block in response)
    
    # Write cleaned TXT file
    with open(output_file, 'w', encoding='utf-8') as file:
        for block in cleaned_blocks:
            file.write(f"{block['speaker']}: {block['text']}\n\n")
    print(f"Cleaned transcript saved to {output_file}")