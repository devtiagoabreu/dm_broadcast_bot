# 🚀 Slack DM Manager Pro

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-0.80.1-purple.svg)](https://flet.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Slack API](https://img.shields.io/badge/Slack-API-red.svg)](https://api.slack.com/)

**Sistema profissional de automação de envio de mensagens diretas no Slack** com interface gráfica moderna, múltiplas listas de usuários e suporte a arquivos multimídia.
![alt text](image.png)
---

## ✨ Funcionalidades Principais

### 📊 **Dashboard Inteligente**
- Monitoramento em tempo real de estatísticas
- Contagem de listas e usuários carregados
- Visão geral de arquivos disponíveis e selecionados

### 👥 **Gerenciamento de Listas**
- Carregamento automático de listas de usuários (arquivos .txt)
- Seleção múltipla de listas para envio
- Editor integrado para modificação de listas
- Normalização inteligente de nomes

### 📎 **Sistema de Arquivos**
- **Seleção múltipla** de arquivos para envio
- Suporte a diversos formatos:
  - 🖼️ **Imagens**: JPG, PNG, GIF, BMP, WebP, SVG, TIFF
  - 🎬 **Vídeos**: MP4, AVI, MOV, WMV, FLV, MKV, WebM
  - 📄 **Documentos**: PDF, DOC, XLS, PPT, CSV, TXT
  - 📦 **Arquivos**: ZIP, RAR
- Botões rápidos: "Selecionar Todos" e "Limpar Seleção"

### ✉️ **Sistema de Mensagens**
- Editor de mensagens com visualização expandida
- Personalização com `{{nome}}` para cada usuário
- Contador de caracteres em tempo real
- Salvamento automático da última mensagem

### ⚙️ **Configurações Avançadas**
- Controle de delay entre mensagens (1-5 segundos)
- Modo de teste (simulação) para desenvolvimento
- Modo real com API do Slack
- Logs detalhados em CSV

### 📜 **Sistema de Logs**
- Log em tempo real com emojis e cores
- Exportação para CSV com timestamp
- Limpeza fácil da área de logs
- Registro completo de sucessos e erros

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Python** | 3.8+ | Linguagem principal |
| **Flet** | 0.80.1 | Interface gráfica |
| **Slack SDK** | Latest | Integração com API do Slack |
| **python-dotenv** | Latest | Gerenciamento de variáveis de ambiente |
| **Pathlib** | Native | Manipulação de arquivos |

---

## 🚀 Instalação Rápida

### 1. 📋 Pré-requisitos
```bash
# Python 3.8 ou superior
python --version

# Gerenciador de pacotes pip
pip --version
```

### 2. 📥 Clonar o Repositório
```bash
git clone https://github.com/devtiagoabreu/slack-dm-manager-pro.git
cd slack-dm-manager-pro
```

### 3. 🔧 Configurar Ambiente Virtual
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar no Windows
venv\Scripts\activate

# Ativar no Linux/Mac
source venv/bin/activate
```

### 4. 📦 Instalar Dependências
```bash
pip install -r requirements.txt
```

### 5. 🔑 Configurar Slack App
1. Acesse [api.slack.com/apps](https://api.slack.com/apps)
2. Crie um novo app ou use um existente
3. Adicione os seguintes scopes:
   - `chat:write`
   - `files:write`
   - `im:write`
   - `users:read`
4. Instale o app no seu workspace
5. Copie o **Bot User OAuth Token**

### 6. ⚙️ Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edite o arquivo `.env`:
```env
SLACK_BOT_TOKEN=xoxb-seu-token-aqui
```

### 7. 📁 Estrutura de Diretórios
```
slack-dm-manager-pro/
├── listas/          # Arquivos .txt com listas de usuários
├── imagens/         # Arquivos de imagem para envio
├── arquivos/        # Outros arquivos para envio
├── logs/            # Logs de execução em CSV
├── app.py           # Aplicação principal
├── requirements.txt # Dependências
└── .env             # Configurações (não versionado)
```

---

## 🎮 Como Usar

### 1. 🏁 Iniciar a Aplicação
```bash
python app.py
```

### 2. 📋 Preparar Listas de Usuários
1. Crie arquivos `.txt` na pasta `listas/`
2. Adicione um nome por linha
3. Exemplo `lista_clientes.txt`:
```
João Silva
Maria Santos
Carlos Oliveira
```

### 3. 📎 Adicionar Arquivos
1. Coloque arquivos nas pastas `imagens/` ou `arquivos/`
2. Use o botão "🔄 Atualizar" para carregar
3. Clique nos arquivos para selecionar/deselecionar

### 4. ✉️ Criar Mensagem
1. Digite sua mensagem na área de texto
2. Use `{{nome}}` para personalizar para cada usuário
3. Exemplo: `Olá {{nome}}, como vai?`

### 5. ⚙️ Configurar Envio
1. Selecione as listas desejadas (múltipla escolha)
2. Selecione os arquivos para anexar (opcional)
3. Ajuste o delay entre mensagens (recomendado: 1.5s)

### 6. 🚀 Executar Envio
1. Clique em "📤 INICIAR ENVIO"
2. Acompanhe o progresso no log em tempo real
3. Verifique os logs em `logs/` para detalhes

---

## 📊 Funcionalidades do Dashboard

| Ícone | Métrica | Descrição |
|-------|---------|-----------|
| 📊 | Total de Listas | Quantidade de arquivos .txt carregados |
| 👥 | Total de Usuários | Soma de todos os usuários em todas as listas |
| 📎 | Arquivos Disponíveis | Total de arquivos nas pastas imagens/ e arquivos/ |
| ✅ | Arquivos Selecionados | Quantos arquivos estão selecionados para envio |
| 📁 | Por Lista | Número de usuários em cada lista específica |

---

## ⚠️ Modos de Operação

### 🔄 **Modo de Teste (Simulação)**
- Ativado automaticamente sem token do Slack
- Simula envios para teste e desenvolvimento
- Delay reduzido para testes rápidos
- Gera logs de simulação

### 🎯 **Modo Real (Slack API)**
- Requer token do Slack configurado
- Envia mensagens reais via API
- Respeita delays configurados
- Detecta usuários não encontrados

---

## 🛡️ Medidas de Segurança

### ⏱️ **Delay Anti-Ban**
- Delay mínimo recomendado: 1.0 segundos
- Previne bloqueio por rate limiting
- Configurável de 1.0 a 5.0 segundos

### 🔍 **Validações**
- Verificação de listas selecionadas
- Validação de mensagem não vazia
- Confirmação de delay válido
- Detecção de token Slack

### 💾 **Backup Automático**
- Logs detalhados em CSV
- Salvamento da última mensagem
- Registro de erros e sucessos
- Timestamp em todas as operações

---

## 🐛 Solução de Problemas

### ❌ Erro: "Token Slack não encontrado"
```bash
# Verifique se o arquivo .env existe
# Confirme se SLACK_BOT_TOKEN está configurado
# Reinicie a aplicação após modificar .env
```

### ❌ Erro: "Selecione pelo menos uma lista"
```bash
# Verifique se há arquivos .txt na pasta listas/
# Clique nas checkboxes ao lado das listas
# Use o botão "🔄 Atualizar" para recarregar
```

### ❌ Erro: "Nenhum arquivo encontrado"
```bash
# Adicione arquivos nas pastas imagens/ ou arquivos/
# Use formatos suportados (ver lista acima)
# Clique em "🔄 Atualizar" após adicionar arquivos
```

### ⚡ Performance Lenta
```bash
# Aumente o delay entre mensagens
# Reduza o número de arquivos anexados
# Divida listas grandes em múltiplos arquivos
```

---

## 📈 Dicas de Uso Avançado

### 🎯 **Segmentação de Usuários**
```txt
# Exemplo: lista_vip.txt
CEO Empresa
Diretor Marketing
Gerente Vendas

# Exemplo: lista_colaboradores.txt
Analista Junior
Designer Sênior
Desenvolvedor Pleno
```

### 📊 **Análise de Resultados**
```bash
# Os logs CSV incluem:
# - Data e hora do envio
# - Nome do usuário
# - Status (ENVIADO/SIMULADO)
# - Lista utilizada
# - Trecho da mensagem
# - Arquivos anexados
```

### 🔄 **Automação com Scripts**
```python
# Exemplo: gerar lista de usuários
import csv

with open('listas/nova_lista.txt', 'w') as f:
    f.write('Usuario1\nUsuario2\nUsuario3')
```

---

## 🤝 Contribuindo

1. 🍴 Faça um fork do projeto
2. 🌿 Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. 💾 Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. 📤 Push para a branch (`git push origin feature/AmazingFeature`)
5. 🔀 Abra um Pull Request

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

---

## 👨‍💻 Autor

**Tiago de Abreu** - [@devtiagoabreu](https://github.com/devtiagoabreu)

### 🌐 Redes Sociais

[![GitHub](https://img.shields.io/badge/GitHub-devtiagoabreu-181717?style=for-the-badge&logo=github)](https://github.com/devtiagoabreu)
[![Twitter](https://img.shields.io/badge/Twitter-@devtiagoabreu-1DA1F2?style=for-the-badge&logo=twitter)](https://twitter.com/devtiagoabreu)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Tiago%20de%20Abreu-0077B5?style=for-the-badge&logo=linkedin)](https://linkedin.com/in/devtiagoabreu)
[![Instagram](https://img.shields.io/badge/Instagram-@devtiagoabreu-E4405F?style=for-the-badge&logo=instagram)](https://instagram.com/devtiagoabreu)

### 💬 Suporte

- 📧 Email: [hello@tiagoabreu.dev](mailto:hello@tiagoabreu.dev)
- 🐛 Issues: [GitHub Issues](https://github.com/devtiagoabreu/slack-dm-manager-pro/issues)
- 💡 Sugestões: [GitHub Discussions](https://github.com/devtiagoabreu/slack-dm-manager-pro/discussions)

---

## ⭐ Apoie o Projeto

Se este projeto foi útil para você, considere:

1. ⭐ **Dar uma estrela** no GitHub
2. 🔄 **Compartilhar** com sua rede
3. 🐛 **Reportar issues** encontrados
4. 💡 **Sugerir melhorias**

**"Automatize sua comunicação, amplie seu alcance!"** 🚀

# 📋 Guia Completo: Criando o App Slack - Passo a Passo

## 🎯 Visão Geral do Processo

**Tempo estimado:** 10-15 minutos  
**Nível de dificuldade:** Fácil ⭐  
**Pré-requisitos:** Conta no Slack, workspace de administrador

---

## 🚀 Passo 1: Acessar o Slack API Dashboard

1. **Acesse:** [api.slack.com/apps](https://api.slack.com/apps)
   ```
   https://api.slack.com/apps
   ```

2. **Faça login** com sua conta do Slack
   - Use as credenciais da sua conta principal
   - É necessário ter permissões de administrador no workspace

3. **Verifique se está no workspace correto**
   - No canto superior direito, confirme o workspace
   - Clique para mudar se necessário

---

## 🆕 Passo 2: Criar Novo App

### Opção A: Criar do Zero (Recomendado)
1. Clique no botão verde **"Create New App"**
   
2. Escolha **"From scratch"**
   ```
   ⚙️ From scratch → Build something new
   ```

3. Configure o app:
   - **App Name:** `DM Manager Pro` (ou nome personalizado)
   - **Pick a workspace:** Selecione seu workspace de desenvolvimento
   
4. Clique em **"Create App"**

### Opção B: Usar Configuração Existente
Se já tem um app configurado:
1. Clique em **"Your Apps"** no menu
2. Selecione o app existente
3. Pule para o **Passo 4**

---

## ⚙️ Passo 3: Configurações Básicas

### Na aba "Basic Information":
1. **App Name:** Mantenha ou personalize
2. **Display Name:** Nome que aparece no Slack
3. **Description:** Adicione uma descrição clara
   ```
   Ex: "Sistema de envio automatizado de mensagens diretas"
   ```

4. **App Icon (Opcional):** 
   - Clique em **"Upload Image"**
   - Use uma imagem 512x512px PNG ou JPG
   - Recomendo: ícone profissional relacionado a mensagens

---

## 🔑 Passo 4: Configurar OAuth & Permissions (CRÍTICO)

### 4.1 Acessar Permissões
1. No menu lateral esquerdo, clique em **"OAuth & Permissions"**
2. Role até a seção **"Scopes"**

### 4.2 Adicionar Bot Token Scopes
Clique em **"Add an OAuth Scope"** e adicione **UM POR UM**:

#### 🔐 Scopes ESSENCIAIS:
| Scope | Por que é necessário |
|-------|---------------------|
| **`chat:write`** | Enviar mensagens como seu bot |
| **`files:write`** | Upload e envio de arquivos/imagens |
| **`im:write`** | Iniciar mensagens diretas com usuários |
| **`users:read`** | Ler informações dos usuários do workspace |

#### 📋 Como adicionar:
1. Clique em **"Add an OAuth Scope"**
2. Digite `chat:write` na caixa de busca
3. Selecione `chat:write` da lista
4. Repita para cada scope da lista acima

#### ✅ Lista final deve ter:
```
Bot Token Scopes:
- chat:write
- files:write
- im:write
- users:read
```

---

## 🏗️ Passo 5: Instalar no Workspace

### 5.1 Localizar Botão de Instalação
1. Na mesma página "OAuth & Permissions"
2. Role até a seção **"OAuth Tokens for Your Workspace"**

### 5.2 Instalar
1. Clique no botão verde **"Install to Workspace"**
2. **Atenção:** Se já instalou antes, aparecerá **"Reinstall App"**

### 5.3 Autorizar Permissões
1. Será redirecionado para página de autorização
2. Revise as permissões solicitadas
3. Clique em **"Allow"**

---

## 🎫 Passo 6: Copiar o Token (MUITO IMPORTANTE)

### 6.1 Localizar o Token
Após instalação, volte para "OAuth & Permissions"
Na seção **"OAuth Tokens for Your Workspace"** você verá:

```
Bot User OAuth Token
xoxb-*********-*********-*****************
```

### 6.2 Copiar o Token
1. Clique no botão **"Copy"** ao lado do token
2. **IMPORTANTE:** Nunca compartilhe este token!
3. Formato: `xoxb-` seguido de números e letras

---

## 💾 Passo 7: Configurar no Seu Sistema

### 7.1 Criar/Copiar Arquivo .env
Na pasta do seu projeto:

**Windows:**
```cmd
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

### 7.2 Editar o .env
Abra o arquivo `.env` e cole seu token:

```env
# Slack Bot Token
SLACK_BOT_TOKEN=xoxb-seu-token-aqui-copiado-do-slack

# ⚠️ IMPORTANTE:
# - Nunca versionar este arquivo no Git
# - Manter em local seguro
# - Não compartilhar publicamente
```

---

## 🧪 Passo 8: Testar a Configuração

### 8.1 Teste Rápido com Python
Crie um arquivo `test_slack.py`:

```python
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("SLACK_BOT_TOKEN")

if token:
    client = WebClient(token=token)
    
    try:
        # Testar conexão básica
        response = client.auth_test()
        print("✅ Conexão com Slack OK!")
        print(f"Workspace: {response['team']}")
        print(f"Usuário: {response['user']}")
        
        # Testar listar usuários
        users = client.users_list()
        print(f"✅ {len(users['members'])} usuários no workspace")
        
    except SlackApiError as e:
        print(f"❌ Erro: {e.response['error']}")
else:
    print("❌ Token não encontrado. Verifique seu .env")
```

### 8.2 Executar Teste
```bash
python test_slack.py
```

**Saída esperada:**
```
✅ Conexão com Slack OK!
Workspace: Nome do Seu Workspace
Usuário: dm_manager_pro
✅ 150 usuários no workspace
```

---

## 🔄 Passo 9: Reinstalar Quando Modificar Scopes

**IMPORTANTE:** Sempre que adicionar/remover scopes:

1. Volte ao Slack API
2. Vá em **"OAuth & Permissions"**
3. Clique em **"Reinstall App"**
4. Autorize novamente
5. **Não precisa gerar novo token** (o mesmo continua funcionando)

---

## 🛡️ Passo 10: Segurança e Boas Práticas

### 🔒 Proteger seu Token
```bash
# ADICIONE ao .gitignore:
.env
*.env
config/credentials.json
```

### 📁 Estrutura Segura Recomendada
```
seu-projeto/
├── .gitignore          # Ignorar .env
├── .env               # Token (NÃO VERSIONAR)
├── .env.example       # Template (VERSIONAR)
├── app.py
└── requirements.txt
```

### 🚨 O que NÃO fazer:
- ❌ Nunca commitar `.env` no Git
- ❌ Nunca postar token em fóruns públicos
- ❌ Nunca deixar token em código público
- ❌ Nunca usar o mesmo token em múltiplos lugares

---

## 🐛 Passo 11: Solução de Problemas Comuns

### ❌ Erro: "not_allowed_token_type"
```
Solução: Verifique se está usando Bot Token (xoxb-)
NÃO use: xoxp- (User Token) ou xoxa- (App Token)
```

### ❌ Erro: "missing_scope"
```
Solução: 
1. Verifique se adicionou TODOS os scopes necessários
2. Reinstale o app após adicionar novos scopes
3. Confirme na interface do Slack
```

### ❌ Erro: "invalid_auth"
```
Solução:
1. Token expirado ou revogado
2. Copie novamente do Slack API
3. Verifique espaços no início/fim do token
```

### ❌ Erro: "account_inactive"
```
Solução:
1. Bot foi desativado no workspace
2. Reinstale o app
3. Contate administrador do workspace
```

---

## 📈 Passo 12: Monitoramento e Manutenção

### Verificar Estatísticas do App
1. Acesse [api.slack.com/apps](https://api.slack.com/apps)
2. Selecione seu app
3. Menu: **"Analytics"**
   - Métricas de uso
   - Erros comuns
   - Performance

### Revogar Token Comprometido
Se suspeitar que seu token vazou:
1. Vá em **"OAuth & Permissions"**
2. Clique em **"Revoke Token"**
3. Gere novo token reinstalando

---

## 🎉 Passo 13: Pronto para Usar!

### Teste Final com Seu App
```bash
python app.py
```

**Saída esperada:**
```
🚀 Iniciando Slack DM Manager Pro v1.4.0...
📁 Diretório de listas: /caminho/listas
📁 Diretório de logs: /caminho/logs
📱 Iniciando interface gráfica...
✅ Slack conectado com sucesso!
```

### 🎯 Checklist de Verificação Final
- [ ] App criado no Slack API
- [ ] Scopes adicionados: chat:write, files:write, im:write, users:read
- [ ] App instalado no workspace
- [ ] Token copiado (xoxb-...)
- [ ] Token configurado no .env
- [ ] .env adicionado ao .gitignore
- [ ] Teste de conexão bem-sucedido
- [ ] App iniciando sem erros

---

## 📞 Suporte Adicional

### Recursos Oficiais Slack
- [Slack API Documentation](https://api.slack.com/docs)
- [Slack Community](https://slackcommunity.com/)
- [API Support](https://api.slack.com/support)

### Minhas Redes para Dúvidas
[![GitHub](https://img.shields.io/badge/GitHub-@devtiagoabreu-181717?style=flat-square&logo=github)](https://github.com/devtiagoabreu)
[![Twitter](https://img.shields.io/badge/Twitter-@devtiagoabreu-1DA1F2?style=flat-square&logo=twitter)](https://twitter.com/devtiagoabreu)

---

## 📝 Notas Finais

### ⏱️ Tempos Importantes
- **Token expiração:** Normalmente não expira
- **Reinstalação:** Necessária após mudar scopes
- **Cache:** Slack pode levar alguns minutos para atualizar permissões

### 🔄 Fluxo de Atualização
```
Mudar Scopes → Reinstalar App → Mesmo Token → Pronto!
```

### 🎯 Dica Pro
Crie um workspace de teste separado para desenvolvimento antes de usar em produção!

---

**🎊 Parabéns! Seu Slack DM Manager Pro está configurado e pronto para revolucionar sua comunicação no Slack!** 🚀

*Dúvidas? Me marque no GitHub: @devtiagoabreu*

---

*Última atualização: Janeiro 2024*
*Versão: 1.4.0*