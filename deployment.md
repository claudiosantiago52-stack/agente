# Guia de Deployment

## Opção 1: Heroku

### Pré-requisitos

- Conta no Heroku
- Heroku CLI instalado

### Steps

1. **Criar aplicação Heroku**

```bash
heroku create seu-app-name
```

2. **Definir variáveis de ambiente**

```bash
heroku config:set ANTHROPIC_API_KEY=sk-ant-...
heroku config:set AGENT_ID=seu_agent_id
heroku config:set ENVIRONMENT_ID=seu_environment_id
```

3. **Criar Procfile**

Crie um arquivo `Procfile` na raiz:

```
web: python app.py
```

4. **Deploy**

```bash
git push heroku main
```

5. **Configurar webhook do Twilio**

```
https://seu-app-name.herokuapp.com/whatsapp
```

## Opção 2: Google Cloud Run

### Pré-requisitos

- Conta no Google Cloud
- Google Cloud CLI instalado
- Docker instalado

### Steps

1. **Criar Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["python", "app.py"]
```

2. **Build e push da imagem**

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/whatsapp-agent
```

3. **Deploy no Cloud Run**

```bash
gcloud run deploy whatsapp-agent \
  --image gcr.io/PROJECT_ID/whatsapp-agent \
  --set-env-vars ANTHROPIC_API_KEY=sk-ant-...,AGENT_ID=...,ENVIRONMENT_ID=... \
  --allow-unauthenticated
```

4. **Configurar webhook do Twilio**

```
https://seu-cloud-run-url.run.app/whatsapp
```

## Opção 3: AWS Lambda + API Gateway

### Pré-requisitos

- Conta na AWS
- AWS CLI configurado
- Serverless Framework ou SAM CLI

### Steps usando Serverless Framework

1. **Instalar Serverless Framework**

```bash
npm install -g serverless
```

2. **Criar template**

```bash
serverless create --template aws-python3 --path whatsapp-agent
cd whatsapp-agent
```

3. **Instalar plugin Flask**

```bash
npm install --save-dev serverless-wsgi serverless-python-requirements
```

4. **Configurar serverless.yml**

```yaml
service: whatsapp-agent

provider:
  name: aws
  runtime: python3.11
  environment:
    ANTHROPIC_API_KEY: ${env:ANTHROPIC_API_KEY}
    AGENT_ID: ${env:AGENT_ID}
    ENVIRONMENT_ID: ${env:ENVIRONMENT_ID}

functions:
  app:
    handler: app.app
    events:
      - http:
          path: whatsapp
          method: post
          cors: true

plugins:
  - serverless-python-requirements
  - serverless-wsgi

custom:
  pythonRequirements:
    dockerizePip: true
  wsgi:
    app: app.app
```

5. **Deploy**

```bash
serverless deploy
```

## Monitoramento

### Logs

**Heroku**:
```bash
heroku logs --tail
```

**Google Cloud Run**:
```bash
gcloud run logs read whatsapp-agent
```

**AWS Lambda**:
```bash
aws logs tail /aws/lambda/whatsapp-agent --follow
```

## Segurança

1. **Nunca commit de `.env`**: Adicione à `.gitignore`
2. **Valide webhooks**: Verifique assinatura Twilio
3. **Rate limiting**: Implemente em produção
4. **HTTPS**: Sempre use HTTPS para webhooks

## Scaling

Para aplicações com alto volume:

- Use fila de mensagens (SQS, Pub/Sub)
- Implemente cache de sessões (Redis)
- Configure auto-scaling
- Monitore latência da API Anthropic
