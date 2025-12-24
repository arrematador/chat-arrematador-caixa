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
GEMINI_MODEL = "gemini-2.0-flash"  # Gratuito, muito inteligente, foco em conversão
OPENAI_MODEL = "gpt-4o-mini"  # Fallback barato e confiável

# ============================================
# MODELOS EXPANDIDOS
# ============================================
class ImovelData(BaseModel):
    """Dados extraídos da página do imóvel - EXPANDIDO"""
    url: str
    chb: Optional[str] = None
    titulo: Optional[str] = None
    endereco: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    preco: Optional[str] = None
    avaliacao: Optional[str] = None
    desconto: Optional[str] = None
    desconto_percentual: Optional[str] = None
    tipo_imovel: Optional[str] = None
    area_privativa: Optional[str] = None
    area_terreno: Optional[str] = None
    area: Optional[str] = None  # Legacy
    quartos: Optional[str] = None
    vagas: Optional[str] = None
    descricao: Optional[str] = None
    inscricao: Optional[str] = None
    modalidade: Optional[str] = None
    data_leilao: Optional[str] = None
    aceita_financiamento: Optional[bool] = None
    aceita_fgts: Optional[bool] = None
    aceita_recursos_proprios: Optional[bool] = None
    ocupado: Optional[bool] = None
    matricula: Optional[str] = None
    observacoes: Optional[str] = None
    despesas_condominio: Optional[str] = None
    despesas_tributos: Optional[str] = None


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
# PROMPT DO SISTEMA - SUPER ROBUSTO PARA VENDAS
# ============================================
def build_system_prompt(imovel: ImovelData) -> str:
    """Constrói o prompt do sistema com os dados do imóvel - FOCO EM CONVERSÃO"""
    
    # Formata áreas
    areas = []
    if imovel.area_privativa:
        areas.append(f"Área Privativa: {imovel.area_privativa}")
    if imovel.area_terreno:
        areas.append(f"Área do Terreno: {imovel.area_terreno}")
    if imovel.area and not areas:
        areas.append(f"Área: {imovel.area}")
    area_info = " | ".join(areas) if areas else "Consulte a página"
    
    # Formata formas de pagamento
    pagamento_lista = []
    if imovel.aceita_recursos_proprios:
        pagamento_lista.append("✅ Recursos Próprios (à vista)")
    if imovel.aceita_fgts:
        pagamento_lista.append("✅ FGTS")
    if imovel.aceita_financiamento:
        pagamento_lista.append("✅ Financiamento Habitacional")
    elif imovel.aceita_financiamento == False:
        pagamento_lista.append("❌ Não aceita Financiamento")
    pagamento_info = "\n".join(pagamento_lista) if pagamento_lista else "Consulte a página do imóvel"
    
    return f"""Você é o assistente virtual do Arrematador Caixa. Seu papel é INFORMAR sobre os dados do imóvel que o cliente está vendo.

═══════════════════════════════════════════════════════════════
DADOS DO IMÓVEL (USE APENAS ESTAS INFORMAÇÕES):
═══════════════════════════════════════════════════════════════

• Título: {imovel.titulo or 'Não informado'}
• CHB: {imovel.chb or 'Não informado'}
• Cidade/Estado: {imovel.cidade or ''} {('- ' + imovel.estado) if imovel.estado else ''}
• Endereço: {imovel.endereco or 'Não informado'}

• Preço de Venda: {imovel.preco or 'Não informado'}
• Valor de Avaliação: {imovel.avaliacao or 'Não informado'}
• Desconto: {imovel.desconto_percentual or imovel.desconto or 'Não informado'}

• Tipo: {imovel.tipo_imovel or 'Não informado'}
• {area_info}
• Quartos: {imovel.quartos or 'Não informado'}

• Modalidade: {imovel.modalidade or 'Não informado'}
• Data: {imovel.data_leilao or 'Não informado'}

• Formas de Pagamento:
{pagamento_info}

• Condomínio: {imovel.despesas_condominio or 'Verificar no edital'}
• Tributos: {imovel.despesas_tributos or 'Verificar no edital'}

═══════════════════════════════════════════════════════════════
REGRAS OBRIGATÓRIAS:
═══════════════════════════════════════════════════════════════

1. NUNCA invente informações. Use APENAS os dados acima.
2. NUNCA gere links. O cliente já está na página do imóvel.
3. Se uma informação está como "Não informado", diga que o cliente pode ver na página ou falar com especialista.
4. Respostas CURTAS e DIRETAS (máximo 3 linhas).
5. Se a pergunta for complexa ou sobre processo de compra, direcione para o especialista.

FORMATO DE RESPOSTA:

Para perguntas sobre dados do imóvel:
- Responda diretamente com a informação disponível.
- Exemplo: "Este imóvel custa {imovel.preco or 'valor na página'}, com desconto de {imovel.desconto_percentual or 'ver na página'}."

Para perguntas que você NÃO tem a informação:
- "Essa informação está disponível no edital do imóvel. Nosso especialista pode te ajudar - clique em 'Falar com Especialista'."

Para perguntas sobre compra/processo/documentos:
- "Para te orientar sobre isso, clique em 'Falar com Especialista' e nosso time vai te ajudar! 📱"

TOM: Direto, prestativo, sem enrolação. Use no máximo 1 emoji por resposta.
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
            "temperature": 0.3,
            "maxOutputTokens": 512,
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
        "model": OPENAI_MODEL,
        "messages": formatted_messages,
        "temperature": 0.3,
        "max_tokens": 512,
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
