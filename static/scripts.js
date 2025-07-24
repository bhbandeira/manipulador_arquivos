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
    // Funções auxiliares
    const showWarning = (message, details = '') => {
        const warningDiv = document.createElement('div');
        warningDiv.className = 'warning-message';
        warningDiv.innerHTML = `
            <strong>Aviso:</strong> ${message}
            ${details ? `<br><small>Detalhes: ${details}</small>` : ''}
        `;
        
        const oldErrors = document.querySelectorAll('.warning-message');
        oldErrors.forEach(e => e.remove());
        
        uploadForm.parentNode.insertBefore(warningDiv, uploadForm.nextSibling);
        warningDiv.scrollIntoView({ behavior: 'smooth' });
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

    const createActionButton = (action, label, color = '#4CAF50' , isSubButton = false) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.dataset.action = action;
        button.dataset.isSub = isSubButton.toString();
        button.textContent = label;
        button.style.backgroundColor = color;
        
        if (isSubButton) {
            button.classList.add('sub-button');
            button.style.marginLeft = '20px';
            button.style.marginTop = '5px';
            button.style.fontSize = '0.9em';
        }
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Verifica se é sub-botão pelo atributo dataset
            const isSub = this.dataset.isSub === 'true';
            
            if (isSub) {
                console.log('Sub-botão clicado:', action);
                processAction(action);
            } else {
                console.log('Botão principal clicado:', action);
                showSubOptions(action);
            }
        });
        
        return button;
    };

    const showSubOptions = (mainAction) => {
        // Remove os sub-botões anteriores
        const subButtonsContainer = document.querySelector('.sub-buttons-container');
        if (subButtonsContainer) {
            subButtonsContainer.remove();
        }

        // Cria novo container para sub-botões
        const newSubContainer = document.createElement('div');
        newSubContainer.className = 'sub-buttons-container';
        
        // Adiciona os sub-botões específicos
        switch (mainAction) {
            case 'compress_pdf':
                newSubContainer.appendChild(createActionButton(
                    'compress_pdf_low', 'Baixa Qualidade', '#f44336', true
                ));
                newSubContainer.appendChild(createActionButton(
                    'compress_pdf_medium', 'Média Qualidade', '#ff9800', true
                ));
                newSubContainer.appendChild(createActionButton(
                    'compress_pdf_high', 'Alta Qualidade', '#4CAF50', true
                ));
                break;
                
            case 'split_pdf':
                newSubContainer.appendChild(createActionButton(
                    'split_pdf_range', 'Por intervalo', '#2196F3', true
                ));
                newSubContainer.appendChild(createActionButton(
                    'split_pdf_single', 'Separar páginas', '#2196F3', true
                ));
                break;
                
            case 'convert_to_mp4':
                // Exemplo para vídeos - pode adicionar opções de qualidade
                newSubContainer.appendChild(createActionButton(
                    'convert_to_mp4_fast', 'Conversão Rápida', '#FF9800', true
                ));
                newSubContainer.appendChild(createActionButton(
                    'convert_to_mp4_hq', 'Alta Qualidade', '#FF5722', true
                ));
                break;
            case 'convert_to_mp3':
                // Exemplo para vídeos - pode adicionar opções de qualidade
                newSubContainer.appendChild(createActionButton(
                    'convert_to_mp3_fast', 'Conversão Rápida', '#FF9800', true
                ));
                newSubContainer.appendChild(createActionButton(
                    'convert_to_mp3_hq', 'Alta Qualidade', '#FF5722', true
                ));
                break;
        }

        // Insere o container se houver sub-botões
        if (newSubContainer.children.length > 0) {
            const actionButtons = document.querySelector('.action-buttons');
            actionButtons.parentNode.insertBefore(newSubContainer, actionButtons.nextSibling);
        }
    };





    // Fecha os submenus quando clicar fora
    document.addEventListener('click', (e) => {
        // Só fecha se não estiver clicando em um botão de ação
        if (!e.target.closest('.action-buttons') && !e.target.closest('.sub-buttons-container')) {
            const subContainer = document.querySelector('.sub-buttons-container');
            if (subContainer) {
                subContainer.remove();
            }
        }
    });

    const updateActionButtons = (summary) => {
        try {
            const actionButtons = document.querySelector('.action-buttons');
            if (!actionButtons) return;
            
            actionButtons.innerHTML = '';
            
            // Ações para PDF
            if (summary?.type === 'pdf') {
                actionButtons.appendChild(createActionButton(
                    'compress_pdf', 'Comprimir PDF', '#4CAF50'
                ));
                actionButtons.appendChild(createActionButton(
                    'split_pdf', 'Dividir PDF', '#2196F3'
                ));
                actionButtons.appendChild(createActionButton(
                    'merge_pdf', 'Juntar PDFs', '#9C27B0'
                ));
            }
            // Ações para MP4
            else if (summary?.type === 'mp4') {
                actionButtons.appendChild(createActionButton(
                    'compress_mp4_28', 'Comprimir (Boa qualidade)', '#4CAF50'
                ));
                actionButtons.appendChild(createActionButton(
                    'compress_mp4_24', 'Comprimir (Melhor qualidade)', '#2196F3'
                ));
            }
            // Ações para WAV
            else if (summary?.type === 'wav') {
                actionButtons.appendChild(createActionButton(
                    'convert_to_mp3', 'Converter para MP3', '#ff9800'
                ));
            }
            // Ações para vídeos conversíveis (incluindo ASF)
            else if (summary?.convertible || summary?.type === 'asf') {
                actionButtons.appendChild(createActionButton(
                    'convert_to_mp4', 'Converter para MP4', '#FF9800'
                ));
            }

            // Ações padrão
            defaultActions.forEach(item => {
                actionButtons.appendChild(createActionButton(item.action, item.label));
            });

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

        fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `filename=${encodeURIComponent(currentFile.filename)}&action=${encodeURIComponent(action)}`
        })
        .then(handleResponse)
        .then(data => {
            // Limpa classes anteriores
            actionResult.className = '';
            actionResult.classList.remove('hidden', 'success', 'error', 'warning');

            // Aplica a classe com base no status retornado
            if (data.status === 'success') {
                actionResult.classList.add('success');
            } else if (data.status === 'warning') {
                actionResult.classList.add('warning');
            } else {
                actionResult.classList.add('error');
            }

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

    const resetFileInfo = () => {
        fileInfo.classList.add('hidden');
        fileSummary.innerHTML = '';
        document.querySelector('.action-buttons').innerHTML = '';
        actionResult.className = '';  // remove classes como success, error, etc.
        actionResult.innerHTML = '';
    };

    // Event Listener principal
    uploadForm.addEventListener('submit', function(e) {
        // limpa tudo antes de processar um novo arquivo
        resetFileInfo();

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
            
            } else if (data.status === 'warning') {
                actionResult.classList.remove('hidden', 'success', 'error');
                actionResult.classList.add('warning');
                actionResult.textContent = data.message;
            } else {
                showError(data.message, data.details);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const msg = error.message || '';
            if (msg.includes('excede o tamanho máximo')) {
                showWarning('O arquivo é muito grande', msg);
            } else {
                showError('Falha na comunicação com o servidor', msg);
            }
        })
        .finally(() => {
            submitButton.textContent = originalButtonText;
            submitButton.disabled = false;
        });
    });
});