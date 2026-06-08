# WhatsApp Agent - Anthropic Integration

Um agente inteligente que responde mensagens do WhatsApp usando a API de Agents do Anthropic.

## Requisitos

- Python 3.8+
- Conta no Anthropic com acesso à API de Agents
- Conta no Twilio para integração com WhatsApp
- Flask para o servidor web

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/claudiosantiago52-stack/agente.git
cd agente
```

### 2. Criar ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e preencha as variáveis:

```bash
cp .env.example .env
```

Edite `.env` com suas credenciais:

```env
ANTHROPIC_API_KEY=sk-ant-...
AGENT_ID=seu_agent_id
ENVIRONMENT_ID=seu_environment_id
PORT=5000
```

## Configuração do Anthropic Agent

1. Acesse [console.anthropic.com](https://console.anthropic.com)
2. Crie um novo Agent
3. Configure as instruções do agente conforme necessário
4. Copie o `AGENT_ID` e `ENVIRONMENT_ID`
5. Coloque-os no arquivo `.env`

## Configuração do Twilio

1. Crie uma conta em [twilio.com](https://www.twilio.com)
2. Configure um número de WhatsApp
3. Na configuração do webhook:
   - **Webhook URL**: `https://seu-dominio.com/whatsapp`
   - **Método**: POST
4. Configure o endereço público do seu servidor (use `ngrok` para testes locais)

## Executar o servidor

```bash
python app.py
```

O servidor começará em `http://localhost:5000`

## Exposição pública (para testes)

Use `ngrok` para expor seu servidor local:

```bash
ngrok http 5000
```

Copie a URL fornecida e configure-a no webhook do Twilio.

## Como funciona

1. **Webhook recebe mensagem**: Twilio envia a mensagem para `/whatsapp`
2. **Sessão criada/recuperada**: Cada número de telefone tem uma sessão própria
3. **Agente processa**: O agente Anthropic processa a mensagem
4. **Resposta enviada**: A resposta é retornada em formato TwiML ao Twilio
5. **Entrega no WhatsApp**: Twilio entrega a resposta ao usuário

## Fluxo de execução

```
WhatsApp Message
    ↓
Twilio Webhook
    ↓
get_or_create_session() - Cria sessão por telefone
    ↓
get_agent_reply() - Stream de eventos do agente
    ↓
AnthropicAgent.message()
    ↓
TwiML Response
    ↓
WhatsApp
```

## Tratamento de erros

O agente inclui tratamento básico de erros:

- Mensagem padrão se o agente não responder
- Logging de sessões por número de telefone
- Timeout na coleta de eventos

## Melhorias futuras

- [ ] Persistência de sessões em banco de dados
- [ ] Histórico de conversas
- [ ] Limite de taxa (rate limiting)
- [ ] Logging estruturado
- [ ] Suporte a mídia (imagens, áudio)
- [ ] Métricas e monitoramento
- [ ] Testes automatizados

## Troubleshooting

### "Desculpe, não consegui processar sua mensagem"

- Verifique se `AGENT_ID` e `ENVIRONMENT_ID` estão corretos
- Confirme que a API key do Anthropic é válida
- Verifique os logs para detalhes do erro

### Webhook não recebe mensagens

- Verifique se o servidor está rodando
- Confirme que a URL pública está configurada corretamente no Twilio
- Use `ngrok` para testar localmente

### Timeout nas respostas

- Considere aumentar o timeout do stream
- Verifique se o agente está respondendo no console do Anthropic

## Licença

MIT

## Contato

Para dúvidas ou sugestões, abra uma issue no repositório.
