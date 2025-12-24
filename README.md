# Chat Arrematador Caixa

Assistente virtual com IA para o site Arrematador Caixa.

## 📁 Estrutura

```
├── frontend/          # Site (deploy no Vercel)
│   ├── index.html
│   ├── vercel.json
│   └── assets/
│
├── backend/           # API do Chat (deploy no Render)
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── render.yaml
│
├── widget/            # Código do widget para GTM
│   ├── chat-widget.js
│   └── gtm-snippet.html
│
└── docs/              # Documentação
```

## 🚀 Deploy

### Frontend (Vercel)
1. Conectar repositório ao Vercel
2. Root Directory: `frontend`
3. Framework: Other
4. Deploy!

### Backend (Render)
1. Conectar repositório ao Render
2. Usar Blueprint (render.yaml) ou configurar manualmente:
   - Root Directory: `backend`
   - Build: `pip install -r requirements.txt`
   - Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Configurar variáveis de ambiente:
   - `GEMINI_API_KEY`: Chave da API do Google Gemini
   - `OPENAI_API_KEY`: Chave da API da OpenAI (fallback)
   - `WHATSAPP_NUMBER`: Número do WhatsApp (ex: 5511999999999)

### Widget (GTM)
1. Copiar conteúdo de `widget/gtm-snippet.html`
2. Atualizar `BACKEND_URL` com a URL do Render
3. Colar no Google Tag Manager como Custom HTML
4. Disparar em páginas `/imovel/*`

## 🔧 Configuração

### GTM ID
Container: `GTM-M8R5DQDJ`

### IAs Utilizadas
- **Primário**: Google Gemini 2.5 Flash (gratuito)
- **Fallback**: OpenAI GPT-4o-mini (pago)

## 📝 Variáveis de Ambiente (Backend)

```env
GEMINI_API_KEY=sua_chave_gemini
OPENAI_API_KEY=sua_chave_openai
WHATSAPP_NUMBER=5511999999999
```
