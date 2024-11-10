# bring in our LLAMA_CLOUD_API_KEY
from dotenv import load_dotenv
load_dotenv()

import nest_asyncio
nest_asyncio.apply()

from urllib.request import Request, urlopen
from io import BytesIO
from PIL import Image
from llama_parse import LlamaParse 
import json
import asyncio

async def get_parse_md(path: str) -> str:
    """Asynchronously parses an essay image."""
    # Download and save image
    remoteFile = urlopen(Request(path)).read()
    memoryFile = BytesIO(remoteFile)
    image = Image.open(memoryFile)
    image.save("./temp/temp_img_essay.png", "PNG")
    
    # Initialize LlamaParse
    llamaparse = LlamaParse(premium_mode=True)
    
    try:
        # Use the async method directly
        parsed_result = await llamaparse.aget_json("./temp/temp_img_essay.png")
        print(parsed_result[0]['pages'][0]['md'])
        return parsed_result[0]['pages'][0]['md']
    except Exception as e:
        print("ERROR:", e)
        return "Error parsing the image."

    
