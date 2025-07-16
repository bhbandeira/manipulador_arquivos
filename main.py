import os
from flask import Flask, render_template, request, redirect, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from models import  get_file_summary, handle_file_action
import time
import threading

# Configurações
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['DOWNLOAD_CONVERT_FOLDER'] = 'converted/downloads'
app.config['DOWNLOAD_COMPRESS_FOLDER'] = 'compresed/downloads'
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024 * 1024  # 1GB
app.config['ALLOWED_EXTENSIONS'] = {'wmv','mp4','avi','mkv','txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx', 'docx'}

# Certifique-se de que as pastas existam
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_CONVERT_FOLDER'], exist_ok=True)
os.makedirs(app.config['DOWNLOAD_COMPRESS_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def agendar_remocao(filepath, delay=10):
    def remover():
        time.sleep(delay)
        try:
            os.remove(filepath)
            app.logger.info(f"Arquivo {filepath} removido após {delay}s.")
        except Exception as e:
            app.logger.error(f"Erro ao remover {filepath}: {str(e)}")
    threading.Thread(target=remover).start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Processa o arquivo e obtém o resumo
        summary = get_file_summary(filepath)
        
        return jsonify({
            'status': 'success',
            'filename': filename,
            'summary': summary
        })
    
    return jsonify({'status': 'error', 'message': 'Tipo de arquivo não permitido'})

@app.route('/process', methods=['POST'])
def process_action():
    try:
        filename = request.form.get('filename')
        action = request.form.get('action')
        
        if not filename or not action:
            return jsonify({
                'status': 'error',
                'message': 'Dados insuficientes',
                'details': 'Nome do arquivo ou ação não fornecidos'
            })
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'status': 'error',
                'message': 'Arquivo não encontrado',
                'details': f'O arquivo {filename} não existe na pasta de uploads'
            })
        
        # Processa a ação selecionada
        if "compress" in action:
            result = handle_file_action(filepath, action, app.config['DOWNLOAD_COMPRESS_FOLDER'])
        else:
            result = handle_file_action(filepath, action, app.config['DOWNLOAD_CONVERT_FOLDER'])
        
        # Log para depuração
        app.logger.info(f"Ação '{action}' executada em {filename}. Resultado: {result}")
        
        if result['status'] == 'success':
            response_data = {
                'status': 'success',
                'message': result['message'],
                'download_url': result.get('download_url')
            }
             
            return jsonify(response_data)
        else:
            return jsonify({
                'status': 'error',
                'message': result['message'],
                'details': result.get('details', '')
            })
            
    except Exception as e:
        app.logger.error(f"Erro no processamento: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Erro interno no processamento',
            'details': str(e),
            'error_type': type(e).__name__
        })

@app.route('/downloads/<filename>')
def download_file(filename):
    try:
        filepath = ""
        
        if "compressed" in filename:
            # Verifica se o arquivo existe
            filepath = os.path.join(app.config['DOWNLOAD_COMPRESS_FOLDER'], filename)

            if not os.path.exists(filepath):
                return jsonify({
                    'status': 'error',
                    'message': 'Arquivo não encontrado'
                }), 404

            # Agendar remoção após envio
            agendar_remocao(filepath)
                        
            return send_from_directory(
                app.config['DOWNLOAD_COMPRESS_FOLDER'],
                filename,
                as_attachment=True,
                mimetype='video/mp4'
            )
        
        else:
            # Verifica se o arquivo existe

            filepath = os.path.join(app.config['DOWNLOAD_CONVERT_FOLDER'], filename)

            if not os.path.exists(filepath):
                return jsonify({
                    'status': 'error',
                    'message': 'Arquivo não encontrado'
                }), 404
            
            # Agendar remoção após envio
            agendar_remocao(filepath)
                        
            return send_from_directory(
                app.config['DOWNLOAD_CONVERT_FOLDER'],
                filename,
                as_attachment=True,
                mimetype='video/mp4'
            )

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)