# 🏠 Chat Arrematador Caixa

Assistente virtual com IA para páginas de imóveis do site Arrematador Caixa.

## 🤖 Modelos de IA

| Modelo | Uso | Custo (1M tokens) |
|--------|-----|-------------------|
| **Gemini 2.0 Flash** | Principal | $0.10 input / $0.40 output |
| **GPT-4o-mini** | Fallback | $0.15 input / $0.60 output |

### 💰 Estimativa de Custos
- **Por conversa**: ~R$ 0,003
- **1.000 conversas/mês**: ~R$ 3,00
- **10.000 conversas/mês**: ~R$ 30,00

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
└── docs/
    └── decisoes-reuniao.md
```

---

## 🚀 URLs de Produção

- **Backend**: https://chat-arrematador-caixa.onrender.com
- **GTM**: GTM-TX46NPP5
- **WhatsApp**: 5519982391622

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
    MOBILE_BREAKPOINT: 768
};
```

---

## 📲 Setup GTM

1. **Tags** → Nova → HTML Personalizado
2. Colar código de `widget/gtm-snippet-es5-v3-mobile.html`
3. **Acionador**: Page Path contém `/imovel/`
4. Publicar

---

## ✨ Funcionalidades

### Widget v3
- ✅ Fullscreen no mobile
- ✅ Safe area (iPhone notch/home bar)
- ✅ Touch otimizado (botões 64px)
- ✅ Auto-open desktop (2s delay)
- ✅ Extração automática de dados da página

### IA (temperatura 0.3)
- ✅ Respostas curtas e diretas
- ✅ Usa apenas dados da página
- ✅ Nunca gera links
- ✅ Direciona para WhatsApp quando necessário

### Dados Extraídos
- CHB, título, endereço, cidade, estado
- Preço, avaliação, desconto
- Área, quartos, modalidade
- Aceita FGTS/financiamento

---

## 🔧 Variáveis de Ambiente (Render)

```
GEMINI_API_KEY=sua_chave
OPENAI_API_KEY=sua_chave
WHATSAPP_NUMBER=5519982391622
```

---

## 📊 Logs

Console do navegador:
```
[Arrematador Chat] Dados extraídos: {...}
[Arrematador Chat] Enviando: {...}
```

---

## 📝 Versões

| Versão | Data | Mudanças |
|--------|------|----------|
| 1.3 | 23/12/2024 | Prompt direto, temperatura 0.3, sem links |
| 1.2 | 23/12/2024 | Widget v3 mobile otimizado |
| 1.1 | 23/12/2024 | Extração expandida de dados |
| 1.0 | 22/12/2024 | Versão inicial |

---

**Contato**: 5519982391622 | arrematadorcaixa.com.br
