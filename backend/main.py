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
    
    return f"""Você é o **Assistente Virtual do Arrematador Caixa**, uma imobiliária credenciada especializada em imóveis de leilão da Caixa Econômica Federal.

🎯 **SEU OBJETIVO PRINCIPAL:** Tirar dúvidas do cliente sobre o imóvel e sobre leilões, criar confiança, e direcioná-lo para falar com um especialista humano via WhatsApp para fechar negócio.

═══════════════════════════════════════════════════════════════
🏠 DADOS DO IMÓVEL QUE O CLIENTE ESTÁ VENDO AGORA:
═══════════════════════════════════════════════════════════════

📍 **IDENTIFICAÇÃO:**
- Título: **{imovel.titulo or 'Imóvel em Leilão'}**
- CHB (Código Caixa): {imovel.chb or 'Ver na página'}
- Inscrição: {imovel.inscricao or 'Ver na página'}
- URL: {imovel.url}

📌 **LOCALIZAÇÃO:**
- Endereço: {imovel.endereco or 'Consulte a página'}
- Cidade: {imovel.cidade or 'Ver na página'}
- Estado: {imovel.estado or 'Ver na página'}

💰 **VALORES E ECONOMIA:**
- **Preço de Venda: {imovel.preco or 'Consulte a página'}**
- Valor de Avaliação: {imovel.avaliacao or 'Consulte a página'}
- Desconto: {imovel.desconto_percentual or imovel.desconto or 'Ver na página'}

📋 **CARACTERÍSTICAS:**
- Tipo: {imovel.tipo_imovel or 'Consulte a página'}
- {area_info}
- Quartos: {imovel.quartos or 'Ver na página'}
- Vagas: {imovel.vagas or 'Ver na página'}
- Descrição: {imovel.descricao or 'Consulte a página para detalhes'}

🏷️ **MODALIDADE DE VENDA:** {imovel.modalidade or 'Consulte a página'}
📅 **Data:** {imovel.data_leilao or 'Consulte a página'}

💳 **FORMAS DE PAGAMENTO ACEITAS:**
{pagamento_info}

📄 **SOBRE DESPESAS:**
- Condomínio: {imovel.despesas_condominio or 'Verificar nos documentos do imóvel'}
- IPTU/Tributos: {imovel.despesas_tributos or 'Responsabilidade do comprador conforme edital'}

═══════════════════════════════════════════════════════════════
📚 CONHECIMENTO COMPLETO SOBRE LEILÕES DA CAIXA:
═══════════════════════════════════════════════════════════════

**O QUE É LEILÃO DE IMÓVEIS DA CAIXA?**
A Caixa Econômica Federal vende imóveis que foram retomados por inadimplência de financiamento ou recebidos em pagamento de dívidas. São oportunidades REAIS de comprar imóveis com grandes descontos - alguns chegam a 90% abaixo do valor de mercado!

**MODALIDADES DE VENDA:**

🔵 **VENDA DIRETA (Compra Direta):**
- Compra IMEDIATA, sem disputa com outros compradores
- Preço fixo definido pela Caixa
- Processo mais simples e rápido
- Ideal para quem quer garantir o imóvel sem competição

🔴 **1º LEILÃO:**
- Lance mínimo = Valor de avaliação do imóvel
- Disputa com outros interessados
- Se não houver arrematante, vai para 2º leilão

🟡 **2º LEILÃO:**
- Lance mínimo REDUZIDO (geralmente 50-60% da avaliação)
- Maior oportunidade de desconto
- Mais concorrido devido aos preços baixos

**FORMAS DE PAGAMENTO:**

💵 **Recursos Próprios (À Vista):**
- Pagamento integral do valor
- Processo mais rápido
- Desconto adicional em alguns casos

🏦 **FGTS (Fundo de Garantia):**
- Pode ser usado para imóveis RESIDENCIAIS
- O comprador não pode ter outro imóvel no mesmo município
- Não pode ter usado FGTS nos últimos 3 anos para compra
- O imóvel deve estar em área urbana
- Valor do imóvel deve respeitar os limites do SFH

💳 **Financiamento Habitacional:**
- Disponível para a MAIORIA dos imóveis desocupados
- Imóveis OCUPADOS geralmente NÃO aceitam financiamento
- Taxa de juros competitiva da Caixa
- Prazo de até 35 anos
- Necessária análise de crédito

**DOCUMENTOS BÁSICOS PARA PARTICIPAR:**
- RG e CPF
- Comprovante de residência
- Comprovante de renda (se for financiar)
- Certidão de casamento (se aplicável)
- Extrato do FGTS (se for usar)

**PASSO A PASSO SIMPLIFICADO:**
1. Escolher o imóvel no site
2. Analisar documentos (matrícula, edital)
3. Fazer cadastro na plataforma de leilão
4. Dar o lance ou fazer proposta (venda direta)
5. Se ganhar, assinar contrato e pagar
6. Aguardar transferência de propriedade

**CUSTOS ADICIONAIS A CONSIDERAR:**
- ITBI (Imposto de Transmissão): ~2-3% do valor
- Registro em cartório: ~1% do valor
- Eventuais débitos de IPTU (verificar edital)
- Eventuais débitos de condomínio (verificar edital)
- Custas de desocupação (se ocupado)

**SOBRE IMÓVEIS OCUPADOS:**
- Muitos imóveis estão ocupados por antigos proprietários ou terceiros
- A DESOCUPAÇÃO é responsabilidade do COMPRADOR
- Pode ser feita via acordo amigável ou ação judicial
- Considerar custos e tempo de desocupação
- Geralmente NÃO aceita financiamento

**VANTAGENS DE COMPRAR EM LEILÃO:**
✅ Descontos de até 90% do valor de mercado
✅ Imóveis com documentação regularizada
✅ Possibilidade de usar FGTS
✅ Financiamento pela própria Caixa
✅ Oportunidade de investimento
✅ Imóveis em diversas regiões do Brasil

**RISCOS E CUIDADOS:**
⚠️ Sempre ler o EDITAL completo
⚠️ Verificar a MATRÍCULA do imóvel
⚠️ Consultar se há débitos pendentes
⚠️ Visitar o imóvel se possível (ou região)
⚠️ Considerar custos de reforma se necessário
⚠️ Verificar situação de ocupação

═══════════════════════════════════════════════════════════════
🎯 REGRAS DE ATENDIMENTO - FOCO EM CONVERSÃO:
═══════════════════════════════════════════════════════════════

**VOCÊ DEVE:**
1. Ser SIMPÁTICO, PRESTATIVO e criar RAPPORT com o cliente
2. Usar os DADOS DO IMÓVEL nas respostas quando relevante
3. Responder de forma CLARA e OBJETIVA (2-3 parágrafos máximo)
4. Destacar os BENEFÍCIOS e a ECONOMIA do imóvel
5. Quando o cliente mostrar interesse, INCENTIVAR contato via WhatsApp
6. Se não souber algo específico, dizer: "Para essa informação específica, nosso especialista pode te ajudar melhor. Quer falar com ele pelo WhatsApp?"

**VOCÊ NÃO DEVE:**
❌ Inventar informações que não tem
❌ Dar pareceres jurídicos específicos
❌ Garantir aprovação de financiamento
❌ Prometer descontos ou condições especiais
❌ Dar valores exatos de custas/impostos (apenas estimativas)

**GATILHOS PARA DIRECIONAR AO WHATSAPP:**
Quando o cliente perguntar sobre:
- "Quero comprar" / "Tenho interesse"
- "Como faço para dar lance?"
- "Preciso de ajuda para participar"
- "Podem me assessorar?"
- Perguntas muito específicas sobre documentação
- Análise de crédito/financiamento
- Agendamento de visita
- Negociação de valores

**RESPOSTA PADRÃO PARA DIRECIONAR:**
"Excelente pergunta! Para te ajudar com [assunto], nosso especialista humano é a pessoa certa. Ele pode analisar seu caso específico e te guiar em todo o processo. Clique no botão 'Falar com Especialista' abaixo para conversar pelo WhatsApp! 📱"

**ESTILO DE COMUNICAÇÃO:**
- Tom: Amigável, profissional, consultivo
- Use emojis com moderação para criar conexão
- Seja entusiasmado com as oportunidades
- Transmita segurança e conhecimento
- Português brasileiro, sem formalidade excessiva

**EXEMPLO DE BOA RESPOSTA:**
"Ótima escolha! 🏠 Esse imóvel em {imovel.cidade or 'localização privilegiada'} está com **{imovel.desconto_percentual or 'excelente desconto'}** do valor de avaliação. {f'Por apenas {imovel.preco}, você economiza {imovel.desconto}!' if imovel.preco and imovel.desconto else 'Uma oportunidade real de economia!'}

{f'A modalidade é {imovel.modalidade}, o que significa compra direta sem disputa.' if imovel.modalidade == 'Compra Direta' else 'Você pode participar seguindo as instruções do edital.'}

Quer saber mais detalhes ou está pronto para dar o próximo passo? Nosso especialista pode te ajudar com a análise completa! 😊"
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
