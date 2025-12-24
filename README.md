# 🏠 Chat Arrematador Caixa v2.5

Assistente virtual com IA para páginas de imóveis do site Arrematador Caixa.

---

## 🤖 Modelos de IA

| Modelo | Uso | Custo (1M tokens) |
|--------|-----|-------------------|
| **Gemini 3 Flash** | Principal | $0.50 input / $3.00 output |
| **GPT-5 mini** | Fallback | $0.25 input / $2.00 output |

### 💰 Estimativa de Custos (Gemini 3 Flash)
| Volume | Custo Estimado |
|--------|----------------|
| **Por conversa** | ~R$ 0,012 |
| **1.000 conversas/mês** | ~R$ 12,00 |
| **10.000 conversas/mês** | ~R$ 120,00 |

> **Nota:** Optamos pelo Gemini 3 Flash para máxima qualidade nas respostas, priorizando conversão sobre economia.

---

## 📁 Estrutura

```
├── backend/                          # API FastAPI (Render)
│   ├── main.py                       # Endpoint /chat
│   ├── requirements.txt
│   └── render.yaml
│
├── widget/                           # Widget GTM
│   └── gtm-snippet-es5-v3-mobile.html
│
├── frontend/                         # Landing teste (Vercel)
│   └── index.html
│
├── docs/
│   ├── decisoes-reuniao.md
│   └── FAQ/
│       ├── faq.md                    # Base de conhecimento (400+ linhas)
│       └── imagens/                  # Guia do Arrematante (42 páginas)
```

---

## 🚀 URLs de Produção

- **Backend**: https://chat-arrematador-caixa.onrender.com
- **Frontend**: https://chat-arrematador-caixa.vercel.app
- **GTM**: GTM-TX46NPP5
- **WhatsApp**: 5519982391622

---

## ✨ Funcionalidades v2.5

### 🧠 Base de Conhecimento (FAQ)
- **400+ linhas** de conhecimento sobre arrematação
- IA responde sobre **processo de leilão** (não só dados do imóvel)
- Modalidades de venda (Leilão SFI, Venda Online, Licitação, etc.)
- Regras de FGTS, financiamento, despesas
- Pós-arrematação, documentação, desocupação

### 🏢 CRECI Dinâmico por Estado
- Mapeamento automático de CRECI por UF
- IA informa o CRECI correto para cada imóvel
- Orienta sobre botão "Copiar CRECI"

### 📄 Documentos
- Detecta disponibilidade de Matrícula e Edital
- Orienta "Procure a seção Documentos do Leilão"

### 📅 Datas de Venda
- Exibe data de término para Venda Online
- Data da Licitação Aberta
- Datas de 1º e 2º Leilão

### 🔗 Orientação sobre Botões
- "Consultar imóvel" (botão laranja → site Caixa)
- "Copiar CRECI" (facilitar na proposta)
- "Tenho dúvidas" / WhatsApp

### 📱 Botão WhatsApp Dinâmico
- Aparece **apenas** quando a IA sugere contato humano
- Keywords: especialista, whatsapp, nossa equipe, falar com, etc.
- Link personalizado com CHB e nome do imóvel

### 📲 Widget v3 (Mobile-First)
- ✅ Fullscreen no mobile
- ✅ Safe area (iPhone notch/home bar)
- ✅ Touch otimizado (botões 64px)
- ✅ Auto-open desktop (2s delay)
- ✅ Extração automática de dados da página

---

## 📊 O que a IA Sabe Responder

### Dados Específicos do Imóvel
| Dado | Fonte |
|------|-------|
| Preço, Desconto, Avaliação | API Arrematador |
| Área privativa, terreno, total | API Arrematador |
| Localização, endereço, cidade/UF | API Arrematador |
| Modalidade (Leilão, Venda Online, etc.) | API Arrematador |
| Aceita FGTS, Financiamento | API Arrematador |
| Data da venda/leilão | API Arrematador |
| Documentos disponíveis (Matrícula, Edital) | API Arrematador |
| CRECI do estado | Mapeamento interno |

### Conhecimento Geral (FAQ)
| Tema | Exemplos |
|------|----------|
| Modalidades de Venda | "Como funciona a Venda Online?" |
| Formas de Pagamento | "Quem paga o IPTU atrasado?" |
| Serviço Gratuito | "O serviço de vocês é pago?" |
| Pós-Arrematação | "Qual o prazo do boleto?" |
| Desocupação | "Vocês ajudam a desocupar?" |
| Documentação | "Quais documentos preciso?" |
| Visitação | "Posso visitar o imóvel?" |

---

## ⚙️ Configuração do Widget

No arquivo `widget/gtm-snippet-es5-v3-mobile.html`:

```javascript
var CONFIG = {
    BACKEND_URL: "https://chat-arrematador-caixa.onrender.com",
    WHATSAPP_NUMBER: "5519982391622",
    THEME_COLOR: "#f97316",
    AUTO_OPEN_DESKTOP: true,
    AUTO_OPEN_DELAY: 2000,
    MOBILE_BREAKPOINT: 768,
    WELCOME_MESSAGE: "Olá! 👋 Eu sou a assistente virtual...",
    ERROR_MESSAGE: "Desculpe, tive um problema técnico..."
};
```

---

## 📲 Setup GTM

1. **Tags** → Nova → HTML Personalizado
2. Colar código de `widget/gtm-snippet-es5-v3-mobile.html`
3. **Acionador**: Page Path contém `/imovel/`
4. Publicar

---

## 🔧 Variáveis de Ambiente (Render)

```bash
GEMINI_API_KEY=***
OPENAI_API_KEY=***
WHATSAPP_NUMBER=5519982391622
```

---

## 📝 Changelog

### v2.5 (24/12/2024)
- ⬆️ Upgrade para **Gemini 3 Flash**
- 📚 FAQ expandido para 400+ linhas
- 🏢 CRECI dinâmico por estado (27 estados)
- 📄 Detecção de documentos disponíveis
- 📅 Data de término para Venda Online
- 🔗 Orientação sobre botões da interface
- 🧠 IA responde perguntas sobre processo de leilão

### v2.1 (23/12/2024)
- 📱 Botão WhatsApp dinâmico (aparece quando IA sugere)
- 💬 Welcome message mais autoritativa
- 🔧 Melhorias no prompt da IA

### v2.0 (22/12/2024)
- 🔄 Integração com API Arrematador (dados completos)
- 📊 Desconto calculado automaticamente
- 📋 Data Venda Online no prompt

### v1.0 (20/12/2024)
- 🚀 Versão inicial
- 📲 Widget mobile-first
- 🤖 Gemini 2.0 Flash + GPT-4o-mini fallback

---

## 👨‍💻 Autor

**Tiago Gladstone**  
Arrematador Caixa - Dezembro 2024
