from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

def check_result(numbers, contest=None):
    # Nova URL da API da Caixa
    if contest:
        url = f"https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/{contest}"
    else:
        url = "https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena/latest"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Tentando acessar URL: {url}")  # Debug
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status code: {response.status_code}")  # Debug
        
        if response.status_code == 200:
            data = response.json()
            # Para API da Caixa, os números estão em 'listaDezenas'
            winning_numbers = data.get('listaDezenas', [])
            contest_number = data.get('numero')
            
            # Converter strings para inteiros para comparação
            user_numbers = [int(n) for n in numbers]
            winning_numbers = [int(n) for n in winning_numbers]
            
            # Verificar números acertados
            matches = set(user_numbers) & set(winning_numbers)
            
            # Determinar o tipo de prêmio
            prize_category = {
                6: "Sena",
                5: "Quina",
                4: "Quadra",
            }.get(len(matches), "Sem premiação")
            
            return {
                'success': True,
                'matches': len(matches),
                'matching_numbers': list(matches),
                'winning_numbers': winning_numbers,
                'contest': contest_number,
                'prize_category': prize_category,
                'date': data.get('dataApuracao')
            }
        
        print(f"Erro na resposta: {response.text}")  # Debug
        return {'success': False, 'error': 'Não foi possível obter os resultados'}
        
    except requests.Timeout:
        return {'success': False, 'error': 'Tempo limite excedido ao consultar a API'}
    except requests.RequestException as e:
        print(f"Erro na requisição: {str(e)}")  # Debug
        return {'success': False, 'error': f'Erro na conexão com a API: {str(e)}'}
    except Exception as e:
        print(f"Erro geral: {str(e)}")  # Debug
        return {'success': False, 'error': str(e)}

@app.route('/')
def home():
    print("Acessando a rota principal...")  # Log para debug
    try:
        return render_template('index.html')
    except Exception as e:
        print(f"Erro ao renderizar template: {e}")  # Log para debug
        return str(e), 500

@app.route('/check', methods=['POST'])
def check():
    print("Recebendo requisição POST...")  # Log para debug
    try:
        numbers = request.form.getlist('numbers[]')
        print(f"Números recebidos: {numbers}")  # Log para debug
        
        contest = request.form.get('contest')
        print(f"Concurso: {contest}")  # Log para debug
        
        if len(numbers) != 6:
            return jsonify({'success': False, 'error': 'Por favor, insira 6 números'})
        
        try:
            numbers = [int(n) for n in numbers]
            if not all(1 <= n <= 60 for n in numbers):
                return jsonify({'success': False, 'error': 'Os números devem estar entre 1 e 60'})
            if len(set(numbers)) != 6:
                return jsonify({'success': False, 'error': 'Não pode haver números repetidos'})
        except ValueError:
            return jsonify({'success': False, 'error': 'Por favor, insira apenas números válidos'})
        
        result = check_result(numbers, contest)
        return jsonify(result)
    except Exception as e:
        print(f"Erro no /check: {e}")  # Log para debug
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Iniciando o servidor Flask...")  # Log para debug
    app.run(port=8080, debug=True)
