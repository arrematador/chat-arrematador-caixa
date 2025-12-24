/**
 * =====================================================
 * ARREMATADOR CAIXA - CHAT AGENT WIDGET
 * =====================================================
 * Widget modular para injeção via Google Tag Manager
 * 
 * COMO USAR:
 * 1. Faça deploy do backend no Render
 * 2. Substitua BACKEND_URL abaixo pela URL do seu backend
 * 3. Cole este script no GTM como Custom HTML Tag
 * 4. Configure trigger para páginas: /imovel/*
 * 
 * Autor: Tiago Gladstone
 * Data: Dezembro 2025
 * =====================================================
 */
(function() {
    'use strict';

    // ==========================================
    // CONFIGURAÇÃO - EDITAR AQUI
    // ==========================================
    const CONFIG = {
        // URL do backend (Render/Cloud Run)
        BACKEND_URL: "https://SEU-BACKEND.onrender.com", // <-- ALTERAR!
        
        // WhatsApp de fallback
        WHATSAPP_NUMBER: "5511999999999", // <-- ALTERAR!
        
        // Aparência
        THEME_COLOR: "#f97316", // Laranja Arrematador
        
        // Comportamento
        AUTO_OPEN_DESKTOP: true,
        AUTO_OPEN_DELAY: 2000,
        MOBILE_BREAKPOINT: 768,
        
        // Mensagens
        WELCOME_MESSAGE: "Olá! 👋 Sou o assistente virtual do Arrematador Caixa. Como posso ajudar você com este imóvel?",
        ERROR_MESSAGE: "Desculpe, tive um problema técnico. Por favor, tente novamente ou fale conosco pelo WhatsApp.",
        TYPING_MESSAGE: "Digitando...",
    };

    // ==========================================
    // ESTADO DO WIDGET
    // ==========================================
    let state = {
        isOpen: false,
        isMobile: window.innerWidth <= CONFIG.MOBILE_BREAKPOINT,
        isLoading: false,
        imovelData: null,
        historico: [],
        shadow: null
    };

    // ==========================================
    // EXTRAÇÃO DE DADOS DA PÁGINA
    // ==========================================
    function extractImovelData() {
        const url = window.location.href;
        const data = {
            url: url,
            chb: null,
            titulo: null,
            endereco: null,
            cidade: null,
            estado: null,
            preco: null,
            avaliacao: null,
            desconto: null,
            tipo_imovel: null,
            area: null,
            quartos: null,
            vagas: null,
            modalidade: null,
            data_leilao: null,
            aceita_financiamento: false,
            aceita_fgts: false,
            ocupado: false,
            matricula: null,
            observacoes: null
        };

        // CHB da URL
        const chbMatch = url.match(/\/imovel\/(\d+)/);
        if (chbMatch) data.chb = chbMatch[1];

        // Título - tenta várias fontes
        const h1 = document.querySelector('h1');
        const ogTitle = document.querySelector('meta[property="og:title"]');
        if (h1) data.titulo = h1.textContent.trim();
        else if (ogTitle) data.titulo = ogTitle.content.replace('Arrematador Caixa - ', '');

        // Busca dados estruturados na página
        const pageText = document.body.innerText;

        // Preço - busca padrões comuns
        const precoPatterns = [
            /Valor de Venda[:\s]*R\$\s*([\d.,]+)/i,
            /Preço[:\s]*R\$\s*([\d.,]+)/i,
            /Lance Mínimo[:\s]*R\$\s*([\d.,]+)/i,
            /R\$\s*([\d]{1,3}(?:\.[\d]{3})*(?:,[\d]{2})?)/
        ];
        for (const pattern of precoPatterns) {
            const match = pageText.match(pattern);
            if (match) {
                data.preco = 'R$ ' + match[1];
                break;
            }
        }

        // Avaliação
        const avaliacaoMatch = pageText.match(/Avaliação[:\s]*R\$\s*([\d.,]+)/i);
        if (avaliacaoMatch) data.avaliacao = 'R$ ' + avaliacaoMatch[1];

        // Desconto
        const descontoMatch = pageText.match(/(\d+(?:,\d+)?)\s*%\s*(?:de\s*)?desconto/i);
        if (descontoMatch) data.desconto = descontoMatch[1] + '%';

        // Endereço - busca elementos comuns
        const enderecoSelectors = [
            '[data-testid="endereco"]',
            '.endereco',
            '.address',
            'p:contains("Rua")',
            'p:contains("Av")'
        ];
        for (const selector of enderecoSelectors) {
            try {
                const el = document.querySelector(selector);
                if (el) {
                    data.endereco = el.textContent.trim();
                    break;
                }
            } catch(e) {}
        }

        // Cidade/Estado - padrão comum
        const cidadeEstadoMatch = pageText.match(/([A-Za-záàâãéêíóôõúç\s]+)\s*[-\/]\s*([A-Z]{2})/);
        if (cidadeEstadoMatch) {
            data.cidade = cidadeEstadoMatch[1].trim();
            data.estado = cidadeEstadoMatch[2];
        }

        // Tipo de imóvel
        const tiposImovel = ['Casa', 'Apartamento', 'Terreno', 'Sala Comercial', 'Galpão', 'Loja', 'Prédio'];
        for (const tipo of tiposImovel) {
            if (pageText.includes(tipo)) {
                data.tipo_imovel = tipo;
                break;
            }
        }

        // Área
        const areaMatch = pageText.match(/(\d+(?:,\d+)?)\s*m²/);
        if (areaMatch) data.area = areaMatch[1] + ' m²';

        // Quartos
        const quartosMatch = pageText.match(/(\d+)\s*(?:quarto|dormitório|suíte)/i);
        if (quartosMatch) data.quartos = quartosMatch[1];

        // Vagas
        const vagasMatch = pageText.match(/(\d+)\s*vaga/i);
        if (vagasMatch) data.vagas = vagasMatch[1];

        // Modalidade
        if (pageText.includes('1º Leilão')) data.modalidade = '1º Leilão';
        else if (pageText.includes('2º Leilão')) data.modalidade = '2º Leilão';
        else if (pageText.includes('Venda Direta')) data.modalidade = 'Venda Direta';

        // Financiamento/FGTS
        data.aceita_financiamento = /aceita\s*financiamento|financiável|financ\./i.test(pageText);
        data.aceita_fgts = /aceita\s*fgts|fgts/i.test(pageText);

        // Ocupação
        data.ocupado = /ocupado|com\s*morador/i.test(pageText);

        // Data do leilão
        const dataMatch = pageText.match(/(\d{2}\/\d{2}\/\d{4})/);
        if (dataMatch) data.data_leilao = dataMatch[1];

        console.log('[Arrematador Chat] Dados extraídos:', data);
        return data;
    }

    // ==========================================
    // VERIFICAR SE É PÁGINA DE IMÓVEL
    // ==========================================
    function isImovelPage() {
        return /\/imovel\/\d+/.test(window.location.pathname);
    }

    // ==========================================
    // COMUNICAÇÃO COM BACKEND
    // ==========================================
    async function sendMessage(mensagem) {
        if (!state.imovelData) {
            state.imovelData = extractImovelData();
        }

        const payload = {
            mensagem: mensagem,
            imovel: state.imovelData,
            historico: state.historico
        };

        try {
            const response = await fetch(`${CONFIG.BACKEND_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            
            // Atualiza histórico
            state.historico.push({ role: 'user', content: mensagem });
            state.historico.push({ role: 'assistant', content: data.resposta });

            return data;
        } catch (error) {
            console.error('[Arrematador Chat] Erro:', error);
            throw error;
        }
    }

    // ==========================================
    // UI - CRIAR WIDGET
    // ==========================================
    function createWidget() {
        // Não cria se não for página de imóvel
        if (!isImovelPage()) {
            console.log('[Arrematador Chat] Não é página de imóvel, widget não carregado');
            return;
        }

        // Extrai dados do imóvel
        state.imovelData = extractImovelData();

        const widget = document.createElement('div');
        widget.id = 'arrematador-chat-agent';
        state.shadow = widget.attachShadow({ mode: 'open' });

        const styles = `
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
            
            :host {
                --primary: ${CONFIG.THEME_COLOR};
                --primary-dark: #ea580c;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            }

            * { box-sizing: border-box; margin: 0; padding: 0; }

            .container {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 2147483647;
                font-size: 14px;
            }

            /* Toggle Button */
            .toggle-btn {
                width: 60px;
                height: 60px;
                border-radius: 50%;
                background: var(--primary);
                border: none;
                cursor: pointer;
                box-shadow: 0 4px 20px rgba(0,0,0,0.25);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            }

            .toggle-btn:hover {
                transform: scale(1.1);
                box-shadow: 0 6px 25px rgba(0,0,0,0.3);
            }

            .toggle-btn svg {
                width: 28px;
                height: 28px;
                fill: white;
            }

            .toggle-btn.open svg.chat-icon { display: none; }
            .toggle-btn.open svg.close-icon { display: block; }
            .toggle-btn:not(.open) svg.chat-icon { display: block; }
            .toggle-btn:not(.open) svg.close-icon { display: none; }

            /* Chat Window */
            .chat-window {
                position: absolute;
                bottom: 75px;
                right: 0;
                width: 380px;
                max-width: calc(100vw - 40px);
                height: 550px;
                max-height: calc(100vh - 120px);
                background: white;
                border-radius: 16px;
                box-shadow: 0 10px 50px rgba(0,0,0,0.2);
                display: none;
                flex-direction: column;
                overflow: hidden;
                animation: slideUp 0.3s ease-out;
            }

            .chat-window.open { display: flex; }

            @keyframes slideUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            /* Header */
            .chat-header {
                background: var(--primary);
                color: white;
                padding: 16px 20px;
                display: flex;
                align-items: center;
                gap: 12px;
            }

            .chat-header-info {
                flex: 1;
            }

            .chat-header-title {
                font-weight: 600;
                font-size: 16px;
            }

            .chat-header-subtitle {
                font-size: 12px;
                opacity: 0.9;
            }

            .close-btn {
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                padding: 4px;
                opacity: 0.8;
                transition: opacity 0.2s;
            }

            .close-btn:hover { opacity: 1; }

            /* Messages Area */
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8fafc;
                display: flex;
                flex-direction: column;
                gap: 16px;
            }

            .message {
                max-width: 85%;
                padding: 12px 16px;
                border-radius: 16px;
                line-height: 1.5;
                animation: fadeIn 0.3s ease;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .message.bot {
                background: white;
                align-self: flex-start;
                border: 1px solid #e2e8f0;
                border-bottom-left-radius: 4px;
                color: #1e293b;
            }

            .message.user {
                background: var(--primary);
                color: white;
                align-self: flex-end;
                border-bottom-right-radius: 4px;
            }

            .message.typing {
                background: white;
                border: 1px solid #e2e8f0;
                align-self: flex-start;
                padding: 16px;
            }

            .typing-dots {
                display: flex;
                gap: 4px;
            }

            .typing-dots span {
                width: 8px;
                height: 8px;
                background: #94a3b8;
                border-radius: 50%;
                animation: bounce 1.4s infinite ease-in-out;
            }

            .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
            .typing-dots span:nth-child(2) { animation-delay: -0.16s; }

            @keyframes bounce {
                0%, 80%, 100% { transform: scale(0); }
                40% { transform: scale(1); }
            }

            /* Input Area */
            .chat-input-area {
                padding: 16px;
                background: white;
                border-top: 1px solid #e2e8f0;
            }

            .input-wrapper {
                display: flex;
                gap: 8px;
            }

            .chat-input {
                flex: 1;
                padding: 12px 16px;
                border: 1px solid #e2e8f0;
                border-radius: 24px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.2s;
            }

            .chat-input:focus {
                border-color: var(--primary);
            }

            .send-btn {
                width: 44px;
                height: 44px;
                border-radius: 50%;
                background: var(--primary);
                border: none;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s;
            }

            .send-btn:hover { background: var(--primary-dark); }
            .send-btn:disabled { background: #cbd5e1; cursor: not-allowed; }

            .send-btn svg {
                width: 20px;
                height: 20px;
                fill: white;
            }

            /* WhatsApp Button */
            .whatsapp-btn {
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                width: 100%;
                padding: 12px;
                margin-top: 12px;
                background: #25D366;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: 600;
                font-size: 14px;
                cursor: pointer;
                text-decoration: none;
                transition: background 0.2s;
            }

            .whatsapp-btn:hover { background: #1da851; }

            .whatsapp-btn svg {
                width: 20px;
                height: 20px;
                fill: currentColor;
            }

            /* Property Info Card */
            .property-card {
                background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
                border: 1px solid #fed7aa;
                border-radius: 12px;
                padding: 12px;
                margin-bottom: 8px;
                font-size: 13px;
            }

            .property-card-title {
                font-weight: 600;
                color: #c2410c;
                margin-bottom: 4px;
            }

            .property-card-price {
                color: #ea580c;
                font-weight: 700;
                font-size: 16px;
            }

            /* Mobile Styles */
            @media (max-width: 768px) {
                .chat-window {
                    width: 100vw;
                    height: calc(100vh - 80px);
                    max-width: 100vw;
                    max-height: calc(100vh - 80px);
                    bottom: 70px;
                    right: -20px;
                    border-radius: 16px 16px 0 0;
                }
            }
        `;

        const html = `
            <style>${styles}</style>
            <div class="container">
                <div class="chat-window" id="chat-window">
                    <div class="chat-header">
                        <div class="chat-header-info">
                            <div class="chat-header-title">Assistente Arrematador</div>
                            <div class="chat-header-subtitle">Especialista em Leilões</div>
                        </div>
                        <button class="close-btn" id="close-btn">
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M18 6L6 18M6 6l12 12"/>
                            </svg>
                        </button>
                    </div>
                    <div class="chat-messages" id="chat-messages"></div>
                    <div class="chat-input-area">
                        <div class="input-wrapper">
                            <input type="text" class="chat-input" id="chat-input" placeholder="Digite sua dúvida..." />
                            <button class="send-btn" id="send-btn">
                                <svg viewBox="0 0 24 24">
                                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                                </svg>
                            </button>
                        </div>
                        <a href="#" class="whatsapp-btn" id="whatsapp-btn" target="_blank">
                            <svg viewBox="0 0 24 24">
                                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                            </svg>
                            Falar com Especialista
                        </a>
                    </div>
                </div>
                <button class="toggle-btn" id="toggle-btn">
                    <svg class="chat-icon" viewBox="0 0 24 24">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                    </svg>
                    <svg class="close-icon" viewBox="0 0 24 24">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z"/>
                    </svg>
                </button>
            </div>
        `;

        state.shadow.innerHTML = html;
        document.body.appendChild(widget);

        // Setup event listeners
        setupEventListeners();

        // Auto-open on desktop
        if (CONFIG.AUTO_OPEN_DESKTOP && !state.isMobile) {
            setTimeout(() => toggleChat(true), CONFIG.AUTO_OPEN_DELAY);
        }
    }

    // ==========================================
    // EVENT LISTENERS
    // ==========================================
    function setupEventListeners() {
        const toggleBtn = state.shadow.getElementById('toggle-btn');
        const closeBtn = state.shadow.getElementById('close-btn');
        const sendBtn = state.shadow.getElementById('send-btn');
        const input = state.shadow.getElementById('chat-input');

        toggleBtn.addEventListener('click', () => toggleChat());
        closeBtn.addEventListener('click', () => toggleChat(false));
        
        sendBtn.addEventListener('click', () => handleSendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
            }
        });

        // Update WhatsApp link
        updateWhatsAppLink();

        // SPA Navigation
        let lastUrl = location.href;
        const observer = new MutationObserver(() => {
            if (location.href !== lastUrl) {
                lastUrl = location.href;
                handleNavigation();
            }
        });
        observer.observe(document, { subtree: true, childList: true });
    }

    // ==========================================
    // UI HANDLERS
    // ==========================================
    function toggleChat(force) {
        state.isOpen = force !== undefined ? force : !state.isOpen;
        
        const chatWindow = state.shadow.getElementById('chat-window');
        const toggleBtn = state.shadow.getElementById('toggle-btn');
        
        if (state.isOpen) {
            chatWindow.classList.add('open');
            toggleBtn.classList.add('open');
            
            // Show welcome message if empty
            const messages = state.shadow.getElementById('chat-messages');
            if (messages.children.length === 0) {
                showPropertyCard();
                addMessage(CONFIG.WELCOME_MESSAGE, 'bot');
            }
            
            // Focus input
            setTimeout(() => {
                state.shadow.getElementById('chat-input').focus();
            }, 300);
        } else {
            chatWindow.classList.remove('open');
            toggleBtn.classList.remove('open');
        }
    }

    function showPropertyCard() {
        const messages = state.shadow.getElementById('chat-messages');
        const data = state.imovelData;
        
        if (!data.titulo && !data.preco) return;

        const card = document.createElement('div');
        card.className = 'property-card';
        card.innerHTML = `
            <div class="property-card-title">${data.titulo || 'Imóvel ' + (data.chb || '')}</div>
            ${data.preco ? `<div class="property-card-price">${data.preco}</div>` : ''}
        `;
        messages.appendChild(card);
    }

    function addMessage(text, type) {
        const messages = state.shadow.getElementById('chat-messages');
        const msg = document.createElement('div');
        msg.className = `message ${type}`;
        msg.innerHTML = text.replace(/\n/g, '<br>');
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;
    }

    function showTyping() {
        const messages = state.shadow.getElementById('chat-messages');
        const typing = document.createElement('div');
        typing.className = 'message typing';
        typing.id = 'typing-indicator';
        typing.innerHTML = `
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        `;
        messages.appendChild(typing);
        messages.scrollTop = messages.scrollHeight;
    }

    function hideTyping() {
        const typing = state.shadow.getElementById('typing-indicator');
        if (typing) typing.remove();
    }

    async function handleSendMessage() {
        const input = state.shadow.getElementById('chat-input');
        const sendBtn = state.shadow.getElementById('send-btn');
        const mensagem = input.value.trim();

        if (!mensagem || state.isLoading) return;

        // Clear input and disable
        input.value = '';
        state.isLoading = true;
        sendBtn.disabled = true;

        // Show user message
        addMessage(mensagem, 'user');
        showTyping();

        try {
            const response = await sendMessage(mensagem);
            hideTyping();
            addMessage(response.resposta, 'bot');

            // Update WhatsApp link if provided
            if (response.whatsapp_link) {
                const waBtn = state.shadow.getElementById('whatsapp-btn');
                waBtn.href = response.whatsapp_link;
            }
        } catch (error) {
            hideTyping();
            addMessage(CONFIG.ERROR_MESSAGE, 'bot');
        }

        state.isLoading = false;
        sendBtn.disabled = false;
        input.focus();
    }

    function updateWhatsAppLink() {
        const data = state.imovelData;
        const text = data.chb 
            ? `Olá! Tenho interesse no imóvel ${data.titulo || ''} (CHB: ${data.chb}). Link: ${data.url}`
            : `Olá! Vim do site Arrematador Caixa e tenho uma dúvida.`;
        
        const link = `https://wa.me/${CONFIG.WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`;
        const waBtn = state.shadow.getElementById('whatsapp-btn');
        if (waBtn) waBtn.href = link;
    }

    function handleNavigation() {
        if (isImovelPage()) {
            state.imovelData = extractImovelData();
            state.historico = [];
            updateWhatsAppLink();
            
            // Clear messages
            const messages = state.shadow.getElementById('chat-messages');
            if (messages) messages.innerHTML = '';
            
            if (state.isOpen) {
                showPropertyCard();
                addMessage(CONFIG.WELCOME_MESSAGE, 'bot');
            }
        }
    }

    // ==========================================
    // INICIALIZAÇÃO
    // ==========================================
    function init() {
        // Aguarda DOM estar pronto
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', createWidget);
        } else {
            createWidget();
        }
    }

    // Evita duplicação
    if (!document.getElementById('arrematador-chat-agent')) {
        init();
    }

})();
