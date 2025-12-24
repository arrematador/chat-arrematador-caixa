#!/usr/bin/env python3
"""
Arrematador Caixa - Script de Testes Automatizados
Gera relatório em Markdown para documentação
"""

import requests
import json
import time
from datetime import datetime

BACKEND = "https://chat-arrematador-caixa.onrender.com/chat"
CHB = "10137656"
URL = f"https://venda-imoveis.caixa.gov.br/sistema/detalhe-imovel.asp?hdnOrigem=index&hdnimovel={CHB}"

# Dados esperados do imóvel (para validação)
IMOVEL_INFO = {
    "nome": "BRASILIA - SETOR BANCARIO SUL",
    "tipo": "Sala Comercial",
    "preco": "R$ 142.432,29",
    "desconto": "51%",
    "modalidade": "Licitação Aberta",
    "uf": "DF",
    "creci": "33395"
}

TESTES = [
    # BLOCO 1: DADOS DO IMÓVEL
    {"categoria": "Dados do Imóvel", "pergunta": "Qual o preço?", "validar": ["142.432", "51%"]},
    {"categoria": "Dados do Imóvel", "pergunta": "Qual a área?", "validar": ["76"]},
    {"categoria": "Dados do Imóvel", "pergunta": "Onde fica esse imóvel?", "validar": ["Brasília", "Setor Bancário", "DF"]},
    {"categoria": "Dados do Imóvel", "pergunta": "Aceita financiamento?", "validar": ["não", "Não"]},
    {"categoria": "Dados do Imóvel", "pergunta": "Aceita FGTS?", "validar": ["não", "Não"]},
    
    # BLOCO 2: MODALIDADE E DATAS
    {"categoria": "Modalidade", "pergunta": "Qual a modalidade de venda?", "validar": ["Licitação", "aberta"]},
    {"categoria": "Modalidade", "pergunta": "Quando é a licitação?", "validar": ["06/01/2026", "10:00"]},
    {"categoria": "Modalidade", "pergunta": "Como funciona a licitação aberta?", "validar": ["proposta", "maior"]},
    
    # BLOCO 3: DOCUMENTOS
    {"categoria": "Documentos", "pergunta": "Onde baixo a matrícula?", "validar": ["Documentos", "Baixar", "disponível"]},
    {"categoria": "Documentos", "pergunta": "Tem edital disponível?", "validar": ["Sim", "disponível", "edital"]},
    
    # BLOCO 4: CRECI
    {"categoria": "CRECI", "pergunta": "Qual o CRECI para esse imóvel?", "validar": ["33395", "DF"]},
    {"categoria": "CRECI", "pergunta": "Como faço para copiar o CRECI?", "validar": ["Copiar CRECI", "botão"]},
    
    # BLOCO 5: BOTÕES E NAVEGAÇÃO
    {"categoria": "Navegação", "pergunta": "Onde consulto no site da Caixa?", "validar": ["Consultar imóvel", "botão", "laranja"]},
    
    # BLOCO 6: DESPESAS
    {"categoria": "Despesas", "pergunta": "Quem paga o condomínio atrasado?", "validar": ["comprador", "10%"]},
    {"categoria": "Despesas", "pergunta": "E o IPTU?", "validar": ["comprador", "responsabilidade"]},
    
    # BLOCO 7: FAQ - CONHECIMENTO GERAL
    {"categoria": "FAQ", "pergunta": "O serviço de vocês é pago?", "validar": ["gratuito", "100%", "Caixa"]},
    {"categoria": "FAQ", "pergunta": "Qual o prazo para pagar depois de arrematar?", "validar": ["2 dias", "úteis"]},
    {"categoria": "FAQ", "pergunta": "Posso visitar o imóvel?", "validar": ["não", "visita"]},
    {"categoria": "FAQ", "pergunta": "Como funciona a Venda Online?", "validar": ["cronômetro", "5 minutos"]},
    
    # BLOCO 8: CONTATO
    {"categoria": "Contato", "pergunta": "Quero falar com alguém", "validar": ["especialista", "equipe", "WhatsApp", "ajudar"]},
]

def test_pergunta(pergunta, validar):
    """Executa teste e retorna resultado"""
    try:
        response = requests.post(
            BACKEND,
            json={"mensagem": pergunta, "imovel": {"url": URL, "chb": CHB}},
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            resposta = data.get("resposta", "")
            provider = data.get("provider", "N/A")
            whatsapp = data.get("redirect_whatsapp", False)
            
            # Validar se contém keywords esperadas
            validacao_ok = any(v.lower() in resposta.lower() for v in validar)
            
            return {
                "status": "✅" if validacao_ok else "⚠️",
                "resposta": resposta[:200] + "..." if len(resposta) > 200 else resposta,
                "provider": provider,
                "whatsapp": "Sim" if whatsapp else "Não",
                "validado": validacao_ok
            }
        else:
            return {"status": "❌", "resposta": f"Erro HTTP {response.status_code}", "provider": "N/A", "whatsapp": "N/A", "validado": False}
    except Exception as e:
        return {"status": "❌", "resposta": str(e)[:100], "provider": "N/A", "whatsapp": "N/A", "validado": False}

def gerar_relatorio():
    """Gera relatório em Markdown"""
    
    print("🚀 Iniciando testes...")
    
    resultados = []
    categorias = {}
    
    for i, teste in enumerate(TESTES):
        print(f"  [{i+1}/{len(TESTES)}] {teste['pergunta'][:40]}...")
        resultado = test_pergunta(teste["pergunta"], teste["validar"])
        resultado["pergunta"] = teste["pergunta"]
        resultado["categoria"] = teste["categoria"]
        resultados.append(resultado)
        
        # Agrupar por categoria
        cat = teste["categoria"]
        if cat not in categorias:
            categorias[cat] = {"ok": 0, "warn": 0, "fail": 0}
        if resultado["status"] == "✅":
            categorias[cat]["ok"] += 1
        elif resultado["status"] == "⚠️":
            categorias[cat]["warn"] += 1
        else:
            categorias[cat]["fail"] += 1
        
        time.sleep(1.5)  # Rate limiting
    
    # Estatísticas
    total = len(resultados)
    ok = sum(1 for r in resultados if r["status"] == "✅")
    warn = sum(1 for r in resultados if r["status"] == "⚠️")
    fail = sum(1 for r in resultados if r["status"] == "❌")
    
    # Gerar Markdown
    md = f"""# 🧪 Relatório de Testes - Chat Arrematador Caixa

> **Data:** {datetime.now().strftime("%d/%m/%Y %H:%M")}  
> **Imóvel Testado:** {IMOVEL_INFO['nome']} (CHB: {CHB})  
> **Backend:** {BACKEND}

---

## 📊 Resumo

| Métrica | Valor |
|---------|-------|
| **Total de Testes** | {total} |
| **✅ Aprovados** | {ok} ({ok*100//total}%) |
| **⚠️ Atenção** | {warn} ({warn*100//total}%) |
| **❌ Falhas** | {fail} ({fail*100//total}%) |

### Por Categoria

| Categoria | ✅ | ⚠️ | ❌ |
|-----------|----|----|----|\n"""
    
    for cat, stats in categorias.items():
        md += f"| {cat} | {stats['ok']} | {stats['warn']} | {stats['fail']} |\n"
    
    md += """
---

## 📋 Resultados Detalhados

"""
    
    current_cat = ""
    for r in resultados:
        if r["categoria"] != current_cat:
            current_cat = r["categoria"]
            md += f"\n### {current_cat}\n\n"
        
        md += f"""**{r['status']} {r['pergunta']}**
> {r['resposta']}
> 
> `Provider: {r['provider']} | WhatsApp: {r['whatsapp']}`

"""
    
    md += f"""---

## 🔧 Configuração do Teste

- **CHB:** {CHB}
- **Modalidade:** {IMOVEL_INFO['modalidade']}
- **UF:** {IMOVEL_INFO['uf']}
- **CRECI Esperado:** {IMOVEL_INFO['creci']}

---

> Gerado automaticamente em {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
"""
    
    return md, ok, total

if __name__ == "__main__":
    md, ok, total = gerar_relatorio()
    
    # Salvar arquivo
    with open("/Users/tiagogladstone/Desktop/Arrematador caixa/docs/TESTES.md", "w") as f:
        f.write(md)
    
    print(f"\n✅ Relatório gerado: docs/TESTES.md")
    print(f"📊 Resultado: {ok}/{total} testes aprovados ({ok*100//total}%)")
