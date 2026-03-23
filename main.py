import uuid6
import os
from dotenv import load_dotenv  
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from datetime import datetime, timezone, timedelta
from starlette import status

# Carrega as variáveis do arquivo .env
load_dotenv()

app = FastAPI()

# Busca a chave do sistema operacional (se não achar, usa None)
API_KEY = os.getenv("MY_API_KEY")
API_KEY_NAME = "X-API-KEY"


# Configura o FastAPI para procurar a chave no cabeçalho 'X-API-KEY'
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(header_value: str = Security(api_key_header)):
    # Valida se a chave enviada é igual à que está no .env
    if header_value == API_KEY:
        return header_value
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Chave de API inválida"
    )

# 2. Aplique a dependência GLOBALMENTE aqui
app = FastAPI(dependencies=[Depends(get_api_key)])


@app.get("/")
def read_root():
    return {"id": str(uuid6.uuid7()).upper()}


@app.get("/V/{uuid_completo}")
def versão(uuid_completo: str):
    # 1. Remove os hífens do UUID
    limpo = uuid_completo.replace("-", "")
    
    # 2. Pega os primeiros 12 caracteres (que contêm o timestamp de 48 bits)
    timestamp_hex = limpo[:12]
    
    # 3. Converte de Hexadecimal para Inteiro (milissegundos)
    ms = int(timestamp_hex, 16)

    # 4. Converte para UTC e ajusta para Brasília (UTC-3)
    fuso_br = timezone(timedelta(hours=-3))
    data_br = datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc).astimezone(fuso_br)

    return {
        "uuid": uuid_completo,
        "data_hora_brasilia": data_br.strftime('%d/%m/%Y %H:%M:%S')
    }

