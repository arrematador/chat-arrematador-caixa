"""
Arrematador Caixa - Chat Agent Backend
Autor: Tiago Gladstone
Data: Dezembro 2025

Backend simples para o chat agent com fallback de IAs:
1º Gemini (Google) - Gratuito
2º OpenAI - Fallback pago
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import httpx
import json
from datetime import datetime

app = FastAPI(title="Arrematador Chat Agent", version="1.0.0")

# CORS - permite requisições do site
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, restringir para o domínio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# CONFIGURAÇÕES - Definir via variáveis de ambiente
# ============================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "5511999999999")

# Modelos de IA
GEMINI_MODEL = "gemini-2.5-flash-preview-05-20"  # Gratuito, rápido e inteligente
OPENAI_MODEL = "gpt-4o-mini"  # Fallback barato e confiável

# ============================================
# MODELOS
# ============================================
class ImovelData(BaseModel):
    """Dados extraídos da página do imóvel"""
    url: str
    chb: Optional[str] = None
    titulo: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    preco: Optional[str] = None
    avaliacao: Optional[str] = None
    desconto: Optional[str] = None
    tipo_imovel: Optional[str] = None
    area: Optional[str] = None
    quartos: Optional[str] = None
    vagas: Optional[str] = None
    modalidade: Optional[str] = None
    data_leilao: Optional[str] = None
    aceita_financiamento: Optional[bool] = None
    aceita_fgts: Optional[bool] = None
    ocupado: Optional[bool] = None
    matricula: Optional[str] = None
    observacoes: Optional[str] = None

class ChatRequest(BaseModel):
    """Requisição do chat"""
    mensagem: str
    imovel: ImovelData
    historico: Optional[list] = []

class ChatResponse(BaseModel):
    """Resposta do chat"""
    resposta: str
    provider: str  # "gemini" ou "openai"
    redirect_whatsapp: bool = False
    whatsapp_link: Optional[str] = None

# ============================================
# PROMPT DO SISTEMA
# ============================================
def build_system_prompt(imovel: ImovelData) -> str:
    """Constrói o prompt do sistema com os dados do imóvel"""
    
    return f"""Você é um assistente especializado em leilões de imóveis da Caixa Econômica Federal, trabalhando para o Arrematador Caixa.

DADOS DO IMÓVEL QUE O CLIENTE ESTÁ VISUALIZANDO:
================================================
- CHB (Código): {imovel.chb or 'Não identificado'}
- Título: {imovel.titulo or 'Não disponível'}
- Endereço: {imovel.endereco or 'Não disponível'}
- Cidade/Estado: {imovel.cidade or ''} - {imovel.estado or ''}
- Preço de Venda: {imovel.preco or 'Não informado'}
- Valor de Avaliação: {imovel.avaliacao or 'Não informado'}
- Desconto: {imovel.desconto or 'Não informado'}
- Tipo: {imovel.tipo_imovel or 'Não especificado'}
- Área: {imovel.area or 'Não informada'}
- Quartos: {imovel.quartos or 'Não informado'}
- Vagas: {imovel.vagas or 'Não informado'}
- Modalidade: {imovel.modalidade or 'Não especificada'}
- Data do Leilão: {imovel.data_leilao or 'Verificar no site'}
- Aceita Financiamento: {'Sim' if imovel.aceita_financiamento else 'Verificar'}
- Aceita FGTS: {'Sim' if imovel.aceita_fgts else 'Verificar'}
- Ocupado: {'Sim' if imovel.ocupado else 'Não/Verificar'}
- Matrícula: {imovel.matricula or 'Não informada'}
- Observações: {imovel.observacoes or 'Nenhuma'}
- URL: {imovel.url}

SUAS DIRETRIZES:
================
1. Responda APENAS sobre este imóvel específico e sobre o processo de leilão da Caixa
2. Seja cordial, objetivo e profissional
3. Se não souber a resposta com certeza, oriente a falar com um especialista humano
4. Informações que você NÃO SABE e deve direcionar para humano:
   - Detalhes jurídicos específicos do imóvel
   - Situação atual de ocupação detalhada
   - Documentos específicos necessários para ESTE imóvel
   - Dúvidas sobre financiamento personalizado
   - Agendamento de visitas
5. Sempre que o cliente demonstrar interesse real em comprar, direcione para WhatsApp
6. Responda em português brasileiro, de forma clara e acessível
7. Mantenha respostas concisas (máximo 3-4 parágrafos)

INFORMAÇÕES GERAIS SOBRE LEILÕES DA CAIXA (use quando apropriado):
==================================================================
- Imóveis podem ter desconto de até 50% do valor de avaliação
- É possível usar FGTS em alguns casos (verificar elegibilidade)
- Financiamento disponível para imóveis não ocupados
- Importante verificar matrícula e certidões antes de arrematar
- O arrematante é responsável por eventuais débitos de IPTU/condomínio
- Há prazo para pagamento após arremate (verificar edital)
"""

# ============================================
# PROVIDERS DE IA
# ============================================
async def call_gemini(messages: list, system_prompt: str) -> tuple[str, bool]:
    """Chama a API do Gemini"""
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY não configurada")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    # Formata mensagens para Gemini
    contents = []
    
    # Adiciona system prompt como primeira mensagem
    contents.append({
        "role": "user",
        "parts": [{"text": f"[INSTRUÇÕES DO SISTEMA]\n{system_prompt}\n[FIM DAS INSTRUÇÕES]"}]
    })
    contents.append({
        "role": "model", 
        "parts": [{"text": "Entendido. Estou pronto para ajudar o cliente com informações sobre este imóvel."}]
    })
    
    # Adiciona histórico
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}]
        })
    
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1024,
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text, True

async def call_openai(messages: list, system_prompt: str) -> tuple[str, bool]:
    """Chama a API da OpenAI (fallback)"""
    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY não configurada")
    
    url = "https://api.openai.com/v1/chat/completions"
    
    # Formata mensagens para OpenAI
    formatted_messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    for msg in messages:
        formatted_messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    payload = {
        "model": OPENAI_MODEL,  # Modelo configurável
        "messages": formatted_messages,
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        text = data["choices"][0]["message"]["content"]
        return text, True

# ============================================
# ENDPOINTS
# ============================================
@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "service": "Arrematador Chat Agent",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check para Render/Cloud Run"""
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal do chat
    Tenta Gemini primeiro, fallback para OpenAI
    """
    
    # Constrói o prompt do sistema com dados do imóvel
    system_prompt = build_system_prompt(request.imovel)
    
    # Prepara mensagens
    messages = request.historico.copy() if request.historico else []
    messages.append({"role": "user", "content": request.mensagem})
    
    resposta = ""
    provider = ""
    
    # 1º Tentativa: Gemini
    try:
        resposta, success = await call_gemini(messages, system_prompt)
        provider = "gemini"
        print(f"[{datetime.now()}] Gemini respondeu com sucesso")
    except Exception as e:
        print(f"[{datetime.now()}] Erro no Gemini: {e}")
        
        # 2º Tentativa: OpenAI (fallback)
        try:
            resposta, success = await call_openai(messages, system_prompt)
            provider = "openai"
            print(f"[{datetime.now()}] OpenAI (fallback) respondeu com sucesso")
        except Exception as e2:
            print(f"[{datetime.now()}] Erro no OpenAI: {e2}")
            # Se ambos falharem, retorna mensagem padrão
            resposta = f"""Desculpe, estou com dificuldades técnicas no momento. 

Para falar sobre o imóvel **{request.imovel.titulo or request.imovel.chb or 'selecionado'}**, entre em contato diretamente com nossa equipe pelo WhatsApp.

Eles poderão te ajudar com todas as informações! 🏠"""
            provider = "fallback"
    
    # Verifica se deve redirecionar para WhatsApp
    redirect_keywords = ["comprar", "interesse", "visita", "agendar", "proposta", "documentos", "certidões"]
    redirect_whatsapp = any(kw in request.mensagem.lower() for kw in redirect_keywords)
    
    # Monta link do WhatsApp
    whatsapp_text = f"Olá! Tenho interesse no imóvel {request.imovel.titulo or ''} (CHB: {request.imovel.chb or 'N/A'}). Link: {request.imovel.url}"
    whatsapp_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={httpx.QueryParams({'': whatsapp_text}).get('')}"
    
    return ChatResponse(
        resposta=resposta,
        provider=provider,
        redirect_whatsapp=redirect_whatsapp,
        whatsapp_link=whatsapp_link.replace("?=", "?text=")
    )

@app.post("/extract-test")
async def extract_test(data: ImovelData):
    """Endpoint para testar extração de dados"""
    return {
        "received": data.dict(),
        "prompt_preview": build_system_prompt(data)[:500] + "..."
    }

# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
