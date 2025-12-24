# Decisões da Reunião - Chat Agent Arrematador Caixa

**Data:** 23 de Dezembro de 2025  
**Participantes:** Tiago Gladstone, Guilherme Berbigier

## Contexto do Projeto

O Arrematador Caixa é uma plataforma especializada em leilões de imóveis da Caixa Econômica Federal. O objetivo é criar um assistente virtual (chat agent) que ajude os visitantes do site a tirar dúvidas sobre os imóveis.

## Decisões Técnicas

### 1. Arquitetura do Chat Agent
- **Widget**: Bolinha flutuante no canto inferior direito
- **Backend**: API REST com FastAPI (Python)
- **Deploy**: Backend no Render, Frontend no Vercel

### 2. Inteligência Artificial
- **Primário**: Google Gemini 2.5 Flash (gratuito)
- **Fallback**: OpenAI GPT-4o-mini (pago, backup)
- **Estratégia**: Usar Gemini primeiro por ser gratuito, OpenAI como fallback

### 3. Fonte de Dados
- **Decisão**: Extrair dados da própria página (scraping do DOM)
- **Motivo**: Simplicidade - não precisa integrar com banco de dados
- **Dados extraídos**: CHB, preço, título, endereço, área, quartos, etc.

### 4. Integração
- **Google Tag Manager (GTM)**: Widget carregado via tag
- **ID do GTM**: GTM-M8R5DQDJ
- **WhatsApp**: Botão de fallback para falar com especialista

### 5. Funcionalidades do Chat
- Responder dúvidas sobre o imóvel específico
- Informar sobre financiamento, FGTS, ocupação
- Direcionar para WhatsApp quando necessário
- Funcionar apenas em páginas de imóvel (/imovel/*)

## Fluxo de Funcionamento

1. Usuário acessa página de imóvel
2. Widget carrega via GTM
3. Widget extrai dados do imóvel da página
4. Usuário envia pergunta
5. Backend processa com Gemini (ou OpenAI se Gemini falhar)
6. IA responde baseada no contexto do imóvel
7. Se necessário, direciona para WhatsApp

## Audios do Bruno(Gestor)

**Áudio 1**
"Sobre o chat, cara, pô, achei que ficou ótimo e quero fazer um teste com você aqui. Quero fazer só um ajuste na hora de fazer a pergunta, porque tem um botão ali embaixo chamado 'Falar com especialista'. Eu tiraria esse botão 'Falar com especialista', tá? Porque senão o cara vai ficar clicando no botão... chamar... é... chamar especialista.

E eu trataria o... o... o... quando abrir ali, o que que eu colocaria [de] mensagem? Eu vou te falar mais ou menos, mas aí a IA vai... vai aperfeiçoar minha fala. Vou até mandar no outro áudio aqui, até se você quiser colocar pra IA ouvir e... e trazer a fala."

**Áudio 2**
"'Oi, eu sou a IA X e eu estou aqui pra te ajudar. Eu sei muito sobre esse imóvel e eu posso te ajudar com muitas dúvidas. Caso alguma coisa eu não... caso tenha alguma coisa que eu não saiba, pode ficar tranquilo que eu vou te direcionar pra um... pra um ser humano da equipe.'

Alguma coisa nessa linha, entendeu? Dá autoridade pra IA, pra ela poder fazer o filtro inicial, e... e aí a pessoa só chama caso realmente ela precise ou se a IA não tenha a resposta."


## Próximos Passos

1. ✅ Desenvolver backend com Gemini + OpenAI fallback
2. ✅ Criar widget JavaScript
3. ✅ Configurar GTM
4. ⏳ Deploy no Render (backend)
5. ⏳ Deploy no Vercel (frontend)
6. ⏳ Testar em produção
7. ⏳ Adicionar tag no site real via GTM


