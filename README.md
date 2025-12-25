# 🏠 Chat Arrematador Caixa v2.5

Assistente virtual com IA para páginas de imóveis do site Arrematador Caixa.

---

## 🚀 Deploy

| Serviço | Plataforma | URL |
|---------|------------|-----|
| **Backend** | Render | https://chat-arrematador-caixa.onrender.com |
| **Frontend** | Vercel | https://chat-arrematador-caixa.vercel.app |
| **GTM** | Google Tag Manager | GTM-TX46NPP5 |

---

## 🤖 Modelos de IA

| Modelo | Uso | Custo (1M tokens) |
|--------|-----|-------------------|
| **Gemini 3 Flash Preview** | Principal | $0.50 input / $3.00 output |
| **GPT-5 mini** | Fallback | $0.25 input / $2.00 output |

### 💰 Estimativa de Custos
| Volume | Custo Estimado |
|--------|----------------|
| **Por conversa** | ~R$ 0,012 |
| **1.000 conversas/mês** | ~R$ 12,00 |
| **10.000 conversas/mês** | ~R$ 120,00 |

---

## 📁 Estrutura

```
├── backend/                    # API FastAPI → Render
│   ├── main.py                 # Endpoint /chat + lógica IA
│   ├── Dockerfile              # Gunicorn + 3 workers
│   ├── requirements.txt
│   └── render.yaml
│
├── frontend/                   # Site teste → Vercel
│
├── widget/                     # Widget GTM
│   └── gtm-snippet-es5-v3-mobile.html
│
├── docs/
│   ├── FAQ/faq.md              # Base de conhecimento (400+ linhas)
│   ├── TESTES.md               # Relatório de testes (20/20 ✅)
│   └── MENSAGEM-GRUPO.md       # Mensagem de entrega
│
└── scripts/
    └── test_chat.py            # Script de testes automatizados
```

---

## ⚙️ Variáveis de Ambiente (Render)

No dashboard do Render → Environment:

| Variável | Valor |
|----------|-------|
| `GEMINI_API_KEY` | sua_chave_gemini |
| `OPENAI_API_KEY` | sua_chave_openai |
| `WHATSAPP_NUMBER` | 5519982391622 |
| `GEMINI_MODEL` | gemini-3-flash-preview |
| `OPENAI_MODEL` | gpt-5-mini |

> **Nota:** Os modelos podem ser trocados sem alterar código!

---

## 📲 Setup GTM (Site Real)

### 1. Adicionar no `<head>`:

```html
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','GTM-TX46NPP5');</script>
<!-- End Google Tag Manager -->
```

### 2. Adicionar após `<body>`:

```html
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-TX46NPP5"
height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
```

O chat aparece apenas em páginas `/imovel/*`.

---

## ✨ Funcionalidades

### 🧠 Base de Conhecimento
- **400+ linhas** de FAQ sobre arrematação
- Modalidades de venda, FGTS, financiamento, despesas
- Pós-arrematação, documentação, desocupação

### 🏢 CRECI Dinâmico
- CRECI correto por estado (27 estados)
- Orienta sobre botão "Copiar CRECI"

### 📄 Documentos
- Detecta matrícula e edital disponíveis
- Orienta download na seção "Documentos do Leilão"

### 📱 WhatsApp Dinâmico
- Botão aparece quando IA sugere especialista
- Link personalizado com CHB e nome do imóvel

---

## 🧪 Testes

**Resultado: 20/20 aprovados (100%)**

Ver relatório completo: [docs/TESTES.md](docs/TESTES.md)

---

## 📝 Changelog

### v2.5 (24/12/2025)
- ⬆️ **Gemini 3 Flash Preview** + **GPT-5 mini**
- 📚 FAQ expandido (400+ linhas)
- 🏢 CRECI dinâmico por estado
- 📄 Detecção de documentos
- ⚙️ Modelos configuráveis via env vars
- 🧪 Script de testes automatizados
- 🐳 Gunicorn com 3 workers (~30 chats simultâneos)

### v2.0 (22/12/2025)
- 🔄 Integração com API Arrematador
- 📊 Desconto calculado automaticamente

### v1.0 (20/12/2025)
- 🚀 Versão inicial
- 📲 Widget mobile-first

---

## 👨‍💻 Autor

**Tiago Gladstone**  
Arrematador Caixa - Dezembro 2025
