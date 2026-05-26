# Programa Essência — v3 (Streamlit)

## Arquivos do projeto

| Arquivo | Função |
|---|---|
| `app.py` | App principal Streamlit |
| `dados.py` | Toda lógica de leitura/escrita no Excel |
| `criar_banco.py` | Gera o Excel inicial com todas as abas |
| `essencia_banco.xlsx` | Banco de dados (criado pelo criar_banco.py) |
| `requirements.txt` | Dependências Python |

---

## Rodar localmente (primeira vez)

```
pip install -r requirements.txt
python criar_banco.py
streamlit run app.py
```

---

## Subir no Streamlit Cloud

1. Crie conta em https://streamlit.io (grátis)
2. Suba os arquivos no GitHub (exceto o .xlsx)
3. No Streamlit Cloud: "New app" → selecione o repositório → `app.py`
4. Em "Secrets" adicione o caminho do Excel:
   ```
   EXCEL_PATH = "//servidor/pasta/essencia_banco.xlsx"
   ```

---

## Abas do Excel (editáveis diretamente)

| Aba | O que contém |
|---|---|
| `Oportunidades` | Banco principal de ideias |
| `Usuários` | Logins, nomes e perfis (craque/lider/adm) |
| `Craques` | Login, filial, área e frente de cada craque |
| `Líderes` | Login e frente de cada líder |
| `Plano de Contas` | Grupos, contas orçamento e contábeis |
| `Orçado` | Valores orçados por frente/ano para o relatório gerencial |

---

## Perfis e permissões

| Ação | Craque | Líder | Adm |
|---|---|---|---|
| Cadastrar ideia | ✅ | ✅ | ✅ |
| Ver próprias ideias | ✅ | — | — |
| Ver frente | — | ✅ | — |
| Ver tudo | — | — | ✅ |
| Mover N1→N2 | ❌ | ❌ | ✅ |
| Mover N2→N3 | ❌ | ✅ | ✅ |
| Mover N3→N4 | ❌ | ❌ | ✅ |
| Cancelar (N0) | ❌ | ✅ | ✅ |
| Editar campos | ❌ | ✅ | ✅ (com confirmação) |
| Comentar | ✅ | ✅ | ✅ |
| Relatório Gerencial | ❌ | ❌ | ✅ |

---

## Adicionar usuários

Abra o Excel → aba `Usuários` → adicione uma linha com:
- Login, Nome Completo, Perfil (craque/lider/adm), Ativo (Sim)

Para craques, adicione também na aba `Craques` com filial, área e frente.
Para líderes, adicione na aba `Líderes` com a frente.
