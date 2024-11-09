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

def get_parse_md(path: str) -> str:
    """Faz o parse de uma imagem de redação."""
    remoteFile = urlopen(Request(path)).read()
    memoryFile = BytesIO(remoteFile)
    
    image = Image.open(memoryFile)
    image.save("./temp/temp_img_essay.png", "PNG")
    
    llamaparse = LlamaParse(premium_mode=True)
    parsed_result = llamaparse.get_json_result("./temp/temp_img_essay.png")
    try:
        return parsed_result[0]['pages'][0]['md']
    except:
        return "Erro ao fazer o parse da imagem."
    
