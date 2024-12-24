from flask import Flask, render_template, request, jsonify
import requests
from collections import Counter
import json
import os

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Arquivo para armazenar o cache dos resultados
CACHE_FILE = 'resultados_cache.json'

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {'numeros': [], 'timestamp': 0}

def save_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)

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

@app.route('/ranking')
def get_ranking():
    try:
        # Usar API alternativa
        url = "https://loteriascaixa-api.herokuapp.com/api/mega-sena"
        response = requests.get(url, timeout=10)
        
        all_numbers = []
        if response.status_code == 200:
            concursos = response.json()
            for concurso in concursos:
                dezenas = concurso.get('dezenas', [])
                for dezena in dezenas:
                    all_numbers.append(int(dezena))
            
            # Salvar no cache
            save_cache({'numeros': all_numbers})
        else:
            # Usar cache se a API falhar
            cache = load_cache()
            all_numbers = cache.get('numeros', [])
        
        if not all_numbers:
            return jsonify({
                'success': False,
                'error': 'Não foi possível obter os números'
            })
        
        # Calcular frequências
        number_count = Counter(all_numbers)
        ranking = []
        
        # Criar ranking completo (1 a 60)
        total_jogos = len(all_numbers) / 6
        for num in range(1, 61):
            freq = number_count.get(num, 0)
            ranking.append({
                "numero": num,
                "frequencia": freq,
                "porcentagem": round((freq / total_jogos) * 100, 2)
            })
        
        # Ordenar por frequência
        ranking.sort(key=lambda x: x['frequencia'], reverse=True)
        
        return jsonify({
            'success': True,
            'ranking': ranking,
            'total_jogos': int(total_jogos)
        })
        
    except Exception as e:
        print(f"Erro no ranking: {str(e)}")  # Debug
        # Tentar usar cache em caso de erro
        try:
            cache = load_cache()
            all_numbers = cache.get('numeros', [])
            if all_numbers:
                number_count = Counter(all_numbers)
                ranking = []
                total_jogos = len(all_numbers) / 6
                
                for num in range(1, 61):
                    freq = number_count.get(num, 0)
                    ranking.append({
                        "numero": num,
                        "frequencia": freq,
                        "porcentagem": round((freq / total_jogos) * 100, 2)
                    })
                
                ranking.sort(key=lambda x: x['frequencia'], reverse=True)
                
                return jsonify({
                    'success': True,
                    'ranking': ranking,
                    'total_jogos': int(total_jogos),
                    'from_cache': True
                })
        except Exception as cache_error:
            print(f"Erro ao usar cache: {str(cache_error)}")  # Debug
            
        return jsonify({
            'success': False,
            'error': f'Erro ao processar ranking: {str(e)}'
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    if os.environ.get('FLASK_ENV') == 'development':
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=port)
