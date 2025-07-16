document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileSummary = document.getElementById('fileSummary');
    const filenameInput = document.getElementById('filename');
    const actionResult = document.getElementById('actionResult');
    const defaultActions = [];
    
    // Estado da aplicação
    let currentFile = null;

    // Funções auxiliares
    const showError = (message, details = '') => {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `
            <strong>Erro:</strong> ${message}
            ${details ? `<br><small>Detalhes: ${details}</small>` : ''}
        `;
        
        const oldErrors = document.querySelectorAll('.error-message');
        oldErrors.forEach(e => e.remove());
        
        uploadForm.parentNode.insertBefore(errorDiv, uploadForm.nextSibling);
        errorDiv.scrollIntoView({ behavior: 'smooth' });
    };

    const handleResponse = (response) => {
        if (!response.ok) {
            return response.json().then(errData => {
                throw new Error(errData.message || `HTTP error! status: ${response.status}`);
            });
        }
        return response.json();
    };

    const updateFileInfo = () => {
        if (!currentFile) return;
        
        filenameInput.value = currentFile.filename;
        fileSummary.innerHTML = `
            <p><strong>Nome:</strong> ${currentFile.summary.filename}</p>
            <p><strong>Tamanho:</strong> ${currentFile.summary.size}</p>
            <p><strong>Tipo:</strong> ${currentFile.summary.type}</p>
            <p><strong>Criado em:</strong> ${currentFile.summary.created}</p>
            <p><strong>Modificado em:</strong> ${currentFile.summary.modified}</p>
        `;
    };

    const createActionButton = (action, label, color = '#4CAF50') => {
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.action = action;
        button.textContent = label;
        button.style.backgroundColor = color;
        
        button.addEventListener('click', () => processAction(action));
        return button;
    };

    const updateActionButtons = (summary) => {
        try {
            const actionButtons = document.querySelector('.action-buttons');
            if (!actionButtons) {
                console.error('Elemento .action-buttons não encontrado');
                return;
            }
            
            actionButtons.innerHTML = '';
            
            // Adiciona ações padrão
            defaultActions.forEach(item => {
                const button = createActionButton(item.action, item.label);
                if (button) {
                    actionButtons.appendChild(button);
                }
            });
            
            /// Verifica se é um arquivo MP4 (compressível)
            if (summary?.type === 'mp4') {
                const compressButton1 = createActionButton(
                    'compress_mp4_28', 
                    'Comprimir (Boa qualidade)', 
                    '#4CAF50'
                );
                actionButtons.appendChild(compressButton1);
                
                const compressButton2 = createActionButton(
                    'compress_mp4_24', 
                    'Comprimir (Melhor qualidade)', 
                    '#2196F3'
                );
                actionButtons.appendChild(compressButton2);
            }
            /// Verifica se é um arquivo wav
            else if (summary?.type === 'wav') {
                const convertButton = createActionButton(
                    'convert_to_mp3',
                    'converter para MP3',
                    '#ff9800'
                );
                actionButtons.appendChild(convertButton);
            }
            // Verifica se é um arquivo conversível (MKV, AVI, WMV)
            else if (summary?.convertible) {
                const convertButton = createActionButton(
                    'convert_to_mp4', 
                    'Converter para MP4', 
                    '#FF9800'
                );
                actionButtons.appendChild(convertButton);
            }


        } catch (error) {
            console.error('Erro em updateActionButtons:', error);
        }
    };

    const processAction = (action) => {
        if (!currentFile?.filename) {
            showError('Nenhum arquivo selecionado para processamento');
            return;
        }

        actionResult.textContent = 'Processando...';
        actionResult.className = 'processing';
        actionResult.classList.remove('hidden');

        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `filename=${encodeURIComponent(currentFile.filename)}&action=${encodeURIComponent(action)}`
        })
        .then(handleResponse)
        .then(data => {
            actionResult.className = data.status === 'success' ? 'success' : 'error';
            actionResult.innerHTML = data.message;
            
            if (data.status === 'success' && data.download_url) {
                const downloadLink = document.createElement('a');
                downloadLink.href = data.download_url;
                downloadLink.textContent = ' Baixar arquivo';
                downloadLink.className = 'download-link';
                actionResult.appendChild(document.createElement('br'));
                actionResult.appendChild(downloadLink);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            actionResult.className = 'error';
            actionResult.textContent = 'Erro na comunicação com o servidor';
        });
    };

    // Event Listener principal
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        currentFile = null;
        
        const file = fileInput.files[0];
        if (!file) {
            showError('Nenhum arquivo selecionado');
            return;
        }

        const submitButton = uploadForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        submitButton.textContent = 'Processando...';
        submitButton.disabled = true;

        fetch('/upload', {
            method: 'POST',
            body: new FormData(uploadForm)
        })
        .then(handleResponse)
        .then(data => {
            if (data.status === 'success') {
                currentFile = {
                    filename: data.filename,
                    summary: data.summary
                };
                updateFileInfo();
                updateActionButtons(data.summary);
                fileInfo.classList.remove('hidden');
            } else {
                showError(data.message, data.details);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Falha na comunicação com o servidor', error.message);
        })
        .finally(() => {
            submitButton.textContent = originalButtonText;
            submitButton.disabled = false;
        });
    });
});