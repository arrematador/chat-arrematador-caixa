"""
Arrematador Caixa - Chat Agent Backend v2.0
Autor: Tiago Gladstone
Data: Dezembro 2025

Fluxo:
1. Widget manda CHB (extraído da URL)
2. Backend busca dados COMPLETOS na API do Arrematador
3. Constrói prompt rico com todos os dados
4. Envia para Gemini (ou OpenAI como fallback)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import httpx
import json
from datetime import datetime

app = FastAPI(title="Arrematador Chat Agent", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# CONFIGURAÇÕES
# ============================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "5519982391622")

GEMINI_MODEL = "gemini-2.0-flash"
OPENAI_MODEL = "gpt-4o-mini"

# API do Arrematador - dados completos dos imóveis
ARREMATADOR_API_URL = "https://arrematador.cxd.dev:3443/api/properties"

# ============================================
# MODELOS
# ============================================
class ImovelData(BaseModel):
    """Dados do widget (só precisamos do CHB e URL)"""
    url: str
    chb: Optional[str] = None
    # Campos mantidos para compatibilidade
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
    area: Optional[str] = None
    quartos: Optional[str] = None
    vagas: Optional[str] = None
    descricao: Optional[str] = None
    inscricao: Optional[str] = None
    modalidade: Optional[str] = None
    data_leilao: Optional[str] = None
    data_venda_online: Optional[str] = None
    aceita_financiamento: Optional[bool] = None
    aceita_fgts: Optional[bool] = None
    aceita_recursos_proprios: Optional[bool] = None
    ocupado: Optional[bool] = None
    matricula: Optional[str] = None
    observacoes: Optional[str] = None
    despesas_condominio: Optional[str] = None
    despesas_tributos: Optional[str] = None


class ChatRequest(BaseModel):
    mensagem: str
    imovel: ImovelData
    historico: Optional[list] = []

class ChatResponse(BaseModel):
    resposta: str
    provider: str
    redirect_whatsapp: bool = False
    whatsapp_link: Optional[str] = None


# ============================================
# BUSCAR DADOS COMPLETOS DA API
# ============================================
async def fetch_imovel_from_api(chb: str) -> dict:
    """Busca dados completos do imóvel na API do Arrematador"""
    if not chb:
        return None
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{ARREMATADOR_API_URL}/{chb}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("data"):
                    print(f"[{datetime.now()}] ✅ API retornou dados para CHB {chb}")
                    return data["data"]
            
            print(f"[{datetime.now()}] ⚠️ API não encontrou CHB {chb}")
            return None
            
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Erro ao buscar API: {e}")
        return None


# ============================================
# FORMATADORES
# ============================================
def format_price(value) -> str:
    """Formata valor para Real brasileiro"""
    if value is None:
        return "Não informado"
    try:
        num = float(value)
        return f"R$ {num:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(value)


def format_area(value) -> str:
    """Formata área em m²"""
    if value is None or value == 0:
        return None
    try:
        return f"{float(value):.2f} m²"
    except:
        return str(value)


def format_date(date_str) -> str:
    """Formata data ISO para BR"""
    if not date_str:
        return "Não informado"
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y às %H:%M")
    except:
        return str(date_str)


def get_modalidade(mode: str) -> str:
    """Traduz modalidade"""
    modos = {
        "auction": "Leilão",
        "bid": "Licitação Aberta",
        "direct": "Venda Direta",
        "online": "Venda Online"
    }
    return modos.get(mode, mode or "Não informado")


def get_condominio_info(cond: str) -> str:
    """Traduz info de condomínio"""
    if cond == "full":
        return "Caixa paga até 10% do valor de avaliação"
    elif cond == "limited":
        return "Sob responsabilidade do comprador"
    return "Verificar no edital"


# ============================================
# CONSTRUIR PROMPT COM DADOS DA API
# ============================================
def build_prompt_from_api(data: dict) -> str:
    """Constrói prompt rico com dados completos da API"""
    
    # Áreas
    areas = []
    if data.get("private_area") and float(data.get("private_area", 0)) > 0:
        areas.append(f"Área Privativa: {format_area(data['private_area'])}")
    if data.get("total_area") and float(data.get("total_area", 0)) > 0:
        areas.append(f"Área Total: {format_area(data['total_area'])}")
    if data.get("land_area") and float(data.get("land_area", 0)) > 0:
        areas.append(f"Área do Terreno: {format_area(data['land_area'])}")
    area_info = " | ".join(areas) if areas else "Não informado"
    
    # Formas de pagamento
    pagamento = []
    pagamento.append("✅ Recursos Próprios (à vista)")
    if data.get("accepts_fgts"):
        pagamento.append("✅ FGTS")
    else:
        pagamento.append("❌ Não aceita FGTS")
    if data.get("accepts_financing"):
        pagamento.append("✅ Financiamento")
    else:
        pagamento.append("❌ Não aceita Financiamento")
    
    # Datas de leilão
    datas_leilao = ""
    if data.get("first_auction_date"):
        datas_leilao += f"\n  - 1º Leilão: {format_date(data['first_auction_date'])} - {format_price(data.get('first_auction_price'))}"
    if data.get("second_auction_date"):
        datas_leilao += f"\n  - 2º Leilão: {format_date(data['second_auction_date'])} - {format_price(data.get('second_auction_price'))}"
    if data.get("open_bidding_date"):
        datas_leilao += f"\n  - Licitação: {format_date(data['open_bidding_date'])} - Lance mínimo: {format_price(data.get('min_sale_price'))}"
    
    # Tratamento para Data Venda Online e Proposta
    if data.get("proposal_date"):
        datas_leilao += f"\n  - Data Venda Online: {format_date(data['proposal_date'])}"
    if data.get("online_sale_date"):
         datas_leilao += f"\n  - Data Venda Online: {format_date(data['online_sale_date'])}"
    if not datas_leilao:
        datas_leilao = "Verificar no edital"
    
    # Desconto
    desconto = data.get("discount", 0)
    try:
        desconto_float = float(desconto)
        desconto_str = f"{desconto_float:.1f}% OFF" if desconto_float > 0 else "Sem desconto adicional"
    except:
        desconto_str = "Verificar"
    
    # Calcula desconto real (avaliação vs preço)
    try:
        avaliacao = float(data.get("evaluation_price", 0))
        preco = float(data.get("price", 0))
        if avaliacao > 0 and preco > 0 and avaliacao > preco:
            desconto_real = ((avaliacao - preco) / avaliacao) * 100
            desconto_str = f"{desconto_real:.0f}% de desconto"
    except:
        pass

    return f"""Você é o assistente virtual do Arrematador Caixa. Responda sobre este imóvel de forma DIRETA e INFORMATIVA.

═══════════════════════════════════════════════════════════════
DADOS COMPLETOS DO IMÓVEL:
═══════════════════════════════════════════════════════════════

📍 LOCALIZAÇÃO:
• Nome: {data.get('name', 'Não informado')}
• Tipo: {data.get('type', 'Não informado')}
• Endereço: {data.get('address', 'Não informado')}
• Bairro: {data.get('neighborhood', 'Não informado')}
• Cidade/UF: {data.get('city', '')}/{data.get('uf', '')}
• CHB: {data.get('property_id', 'Não informado')}

💰 VALORES:
• Preço de Venda: {format_price(data.get('price'))}
• Valor de Avaliação: {format_price(data.get('evaluation_price'))}
• Desconto: {desconto_str}
• Entrada Mínima (50%): {format_price(data.get('initial_payment'))}

📐 CARACTERÍSTICAS:
• {area_info}
• Quartos: {data.get('rooms', 0) if data.get('rooms') else 'Não informado'}
• Vagas de Garagem: {data.get('garage', 0) if data.get('garage') else 'Não informado'}
• Descrição: {data.get('description') or 'Sem descrição adicional'}

📅 MODALIDADE E DATAS:
• Modalidade: {get_modalidade(data.get('mode'))}
• Datas:{datas_leilao}

💳 FORMAS DE PAGAMENTO:
{chr(10).join(pagamento)}

📋 DESPESAS:
• Condomínio: {get_condominio_info(data.get('condominium'))}
• IPTU/Tributos: Sob responsabilidade do comprador

═══════════════════════════════════════════════════════════════
REGRAS OBRIGATÓRIAS:
═══════════════════════════════════════════════════════════════

1. Use APENAS os dados acima. NUNCA invente informações.
2. NUNCA gere links - o cliente já está na página.
3. Respostas CURTAS e DIRETAS (máximo 3 linhas).
4. Para dúvidas sobre processo de compra, documentação, ou dúvidas complexas → "Fale com nosso especialista!"
5. Use no máximo 1 emoji por resposta.
6. Se perguntarem algo que não está nos dados → "Essa informação está no edital. Nosso especialista pode ajudar!"

EXEMPLOS DE RESPOSTAS:
- Pergunta: "Qual o preço?" → "Este imóvel custa {format_price(data.get('price'))}, com {desconto_str} sobre a avaliação de {format_price(data.get('evaluation_price'))}. 🏠"
- Pergunta: "Aceita financiamento?" → "{'Sim, este imóvel aceita financiamento!' if data.get('accepts_financing') else 'Não, este imóvel não aceita financiamento. Apenas recursos próprios' + (' e FGTS.' if data.get('accepts_fgts') else '.')}"
- Pergunta: "Qual o tamanho?" → Informe as áreas disponíveis nos dados.
- Pergunta: "Como funciona o leilão?" → "Para te explicar todo o processo, clique em 'Falar com Especialista'! Nosso time vai te orientar. 📱"
"""


def build_prompt_fallback(imovel: ImovelData) -> str:
    """Fallback: prompt com dados limitados do widget"""
    return f"""Você é o assistente virtual do Arrematador Caixa.

ATENÇÃO: Os dados completos não puderam ser carregados. Responda de forma limitada.

DADOS DISPONÍVEIS:
• CHB: {imovel.chb or 'Não informado'}
• Título: {imovel.titulo or 'Não informado'}  
• Cidade: {imovel.cidade or 'Não informado'}
• Preço: {imovel.preco or 'Ver na página'}
• Data Venda Online: {imovel.data_venda_online or 'Não informado'}

REGRAS:
1. Respostas curtas (máx 2 linhas)
2. NUNCA invente dados
3. Peça ao cliente ver a página ou falar com especialista para detalhes
"""


# ============================================
# PROVIDERS DE IA
# ============================================
async def call_gemini(messages: list, system_prompt: str) -> tuple[str, bool]:
    """Chama a API do Gemini"""
    if not GEMINI_API_KEY:
        raise Exception("GEMINI_API_KEY não configurada")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    contents = []
    contents.append({"role": "user", "parts": [{"text": f"INSTRUÇÕES:\n{system_prompt}"}]})
    contents.append({"role": "model", "parts": [{"text": "Entendido! Vou responder sobre o imóvel de forma direta."}]})
    
    for msg in messages:
        role = "user" if msg.get("role") == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg.get("content", "")}]})
    
    payload = {
        "contents": contents,
        "generationConfig": {
            "temperature": 0.3,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 512,
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Gemini error: {response.status_code} - {response.text}")
        
        data = response.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text.strip(), True


async def call_openai(messages: list, system_prompt: str) -> tuple[str, bool]:
    """Chama a API da OpenAI (fallback)"""
    if not OPENAI_API_KEY:
        raise Exception("OPENAI_API_KEY não configurada")
    
    url = "https://api.openai.com/v1/chat/completions"
    
    openai_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        openai_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    
    payload = {
        "model": OPENAI_MODEL,
        "messages": openai_messages,
        "temperature": 0.3,
        "max_tokens": 512
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"OpenAI error: {response.status_code} - {response.text}")
        
        data = response.json()
        text = data["choices"][0]["message"]["content"]
        return text.strip(), True


# ============================================
# ENDPOINTS
# ============================================
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Arrematador Chat Agent",
        "version": "2.0.0",
        "features": ["API data fetch", "Gemini AI", "OpenAI fallback"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal do chat:
    1. Busca dados completos da API usando CHB
    2. Constrói prompt rico
    3. Envia para Gemini (ou OpenAI como fallback)
    """
    
    chb = request.imovel.chb
    print(f"\n{'='*60}")
    print(f"[{datetime.now()}] 📩 NOVA MENSAGEM")
    print(f"CHB: {chb}")
    print(f"Mensagem: {request.mensagem}")
    
    # 1. Buscar dados completos da API
    api_data = await fetch_imovel_from_api(chb)
    
    # 2. Construir prompt
    if api_data:
        system_prompt = build_prompt_from_api(api_data)
        print(f"[{datetime.now()}] ✅ Dados da API carregados: {api_data.get('name', 'N/A')}")
    else:
        system_prompt = build_prompt_fallback(request.imovel)
        print(f"[{datetime.now()}] ⚠️ API falhou, usando fallback")
    
    # 3. Preparar mensagens
    messages = request.historico.copy() if request.historico else []
    messages.append({"role": "user", "content": request.mensagem})
    
    # 4. Chamar IA
    resposta = ""
    provider = ""
    
    try:
        resposta, _ = await call_gemini(messages, system_prompt)
        provider = "gemini"
        print(f"[{datetime.now()}] ✅ Gemini respondeu")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Gemini erro: {e}")
        try:
            resposta, _ = await call_openai(messages, system_prompt)
            provider = "openai"
            print(f"[{datetime.now()}] ✅ OpenAI respondeu")
        except Exception as e2:
            print(f"[{datetime.now()}] ❌ OpenAI erro: {e2}")
            resposta = "Desculpe, estou com dificuldades técnicas. Clique em 'Falar com Especialista' para atendimento! 📱"
            provider = "fallback"
    
    print(f"[{datetime.now()}] 💬 Resposta ({provider}): {resposta[:80]}...")
    print(f"{'='*60}\n")
    
    # 5. Montar link WhatsApp
    titulo = api_data.get("name", request.imovel.titulo) if api_data else request.imovel.titulo
    whatsapp_text = f"Olá! Tenho interesse no imóvel {titulo or ''} (CHB: {chb or 'N/A'})"
    whatsapp_link = f"https://wa.me/{WHATSAPP_NUMBER}?text={httpx.QueryParams({'': whatsapp_text}).get('')}"
    
    return ChatResponse(
        resposta=resposta,
        provider=provider,
        redirect_whatsapp=False,
        whatsapp_link=whatsapp_link.replace("?=", "?text=")
    )


# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
