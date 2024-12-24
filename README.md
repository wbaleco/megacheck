# Conferidor Mega Sena

Uma aplicação web para conferir resultados da Mega Sena.

## Funcionalidades

- Conferir apostas da Mega Sena
- Verificar resultados do último concurso
- Consultar resultados de concursos anteriores
- Interface amigável e responsiva

## Requisitos

- Python 3.8+
- Flask
- Requests

## Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Como usar

1. Execute o aplicativo:
```bash
python app.py
```

2. Abra o navegador e acesse:
```
http://localhost:5000
```

3. Digite 6 números entre 1 e 60
4. Opcionalmente, especifique um número de concurso
5. Clique em "Conferir" para ver o resultado

## API

O aplicativo utiliza a API pública da Loteria Federal para obter os resultados dos sorteios.
