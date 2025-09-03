document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ dp.js carregado com sucesso!');
    
    let ocorrencias = [];
    let ocorrenciaSelecionada = null;
    let documentosDP = [];
    
    // Inicialização
    async function init() {
        configurarEventos();
        await carregarOcorrenciasDP();
    }
    
    // Configurar eventos
    function configurarEventos() {
        const btnAtualizar = document.getElementById('btnAtualizarDP');
        const btnConfirmar = document.getElementById('btnConfirmarProcessamentoDP');
        
        if (btnAtualizar) {
            btnAtualizar.addEventListener('click', carregarOcorrenciasDP);
        }
        
        if (btnConfirmar) {
            btnConfirmar.addEventListener('click', confirmarProcessamentoDP);
        }
        
        // Logout
        document.getElementById('logoutBtn').addEventListener('click', function(e) {
            e.preventDefault();
            fetch('/api/logout', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                }
            })
            .catch(error => {
                console.error('Erro ao fazer logout:', error);
                window.location.href = '/';
            });
        });
    }
    
    // Carregar ocorrências para o Departamento Pessoal
    async function carregarOcorrenciasDP() {
        const container = document.getElementById('ocorrenciasContainer');
        const loadingState = document.getElementById('loadingState');
        
        // Verificar se os elementos existem
        if (!container) {
            console.error('Elemento ocorrenciasContainer não encontrado');
            return;
        }
        
        if (!loadingState) {
            console.error('Elemento loadingState não encontrado');
            return;
        }
        
        // Mostrar loading
        loadingState.style.display = 'block';
        container.innerHTML = '';
        
        try {
            const response = await fetch('/api/relatorios?status=EM_DP');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            ocorrencias = data.data || [];
            
            // Debug: verificar estrutura dos dados
            if (ocorrencias.length > 0) {
                console.log('Primeira ocorrência:', ocorrencias[0]);
                console.log('Campo motorista:', ocorrencias[0].motorista);
                console.log('Campo dados:', ocorrencias[0].dados);
            }
            
            // Esconder loading
            if (loadingState) {
                loadingState.style.display = 'none';
            }
            renderizarOcorrenciasDP();
        } catch (error) {
            console.error('Erro ao carregar ocorrências:', error);
            if (loadingState) {
                loadingState.style.display = 'none';
            }
            container.innerHTML = `
                <div class="col-12">
                    <div class="error-state">
                        <i class="bi bi-exclamation-triangle"></i>
                        <h4>Erro ao carregar ocorrências</h4>
                        <p>Tente novamente em alguns instantes.</p>
                        <button class="btn btn-modern btn-primary" onclick="carregarOcorrenciasDP()">
                            <i class="bi bi-arrow-clockwise"></i> Tentar Novamente
                        </button>
                    </div>
                </div>
            `;
        }
    }
    
    // Renderizar ocorrências em cards modernos
    function renderizarOcorrenciasDP() {
        const container = document.getElementById('ocorrenciasContainer');
        
        if (ocorrencias.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <i class="bi bi-inbox"></i>
                        <h4>Nenhuma ocorrência encontrada</h4>
                        <p>Não há ocorrências para processar no momento.</p>
                    </div>
                </div>
            `;
            return;
        }

        container.innerHTML = ocorrencias.map(ocorrencia => {
            let dataFormatada = 'N/A';
            try {
                if (ocorrencia.criado_em) {
                    const data = new Date(ocorrencia.criado_em);
                    dataFormatada = data.toLocaleDateString('pt-BR') + ' ' + data.toLocaleTimeString('pt-BR');
                }
            } catch (e) {
                console.error('Erro ao formatar data:', e);
            }
            
            const tipoNome = ocorrencia.tipos_relatorio?.nome || ocorrencia.tipo_nome || ocorrencia.tipo_id || 'N/A';
            
            // Extrair nome do motorista do campo dados ou do campo motorista
            let motoristaNome = 'N/A';
            
            // Primeiro, tentar o campo motorista direto
            if (ocorrencia.motorista) {
                motoristaNome = ocorrencia.motorista;
            }
            // Se não houver, tentar extrair do campo dados
            else if (ocorrencia.dados) {
                try {
                    // Se os dados são uma string, tentar extrair informações
                    if (typeof ocorrencia.dados === 'string') {
                        const motoristaMatch = ocorrencia.dados.match(/motorista[:\s]+([^\n\r,]+)/i);
                        if (motoristaMatch) {
                            motoristaNome = motoristaMatch[1].trim();
                        }
                    }
                    // Se os dados são um objeto, tentar acessar diretamente
                    else if (typeof ocorrencia.dados === 'object') {
                        motoristaNome = ocorrencia.dados.motorista || ocorrencia.dados.motorista_matricula || 'N/A';
                    }
                } catch (e) {
                    console.log('Erro ao extrair dados do motorista:', e);
                }
            }
            const numeroOS = ocorrencia.numero_os || 'N/A';
            
            // Determinar status e cor
            let statusClass = '';
            let statusText = '';
            let statusIcon = '';
            switch(ocorrencia.status) {
                case 'EM_DP':
                    statusClass = 'status-analyzing';
                    statusText = 'Em Análise';
                    statusIcon = 'bi-search';
                    break;
                case 'EM_TRAFEGO':
                    statusClass = 'status-traffic';
                    statusText = 'Em Tráfego';
                    statusIcon = 'bi-truck';
                    break;
                case 'CONCLUIDO':
                    statusClass = 'status-completed';
                    statusText = 'Concluído';
                    statusIcon = 'bi-check-circle';
                    break;
                default:
                    statusClass = 'status-pending';
                    statusText = 'Pendente';
                    statusIcon = 'bi-clock';
            }
            
            return `
                <div class="col-lg-6 col-xl-4 mb-4">
                    <div class="modern-card" data-id="${ocorrencia.id}">
                        <div class="card-header">
                            <div class="os-number">
                                <i class="bi bi-file-text"></i>
                                <span>${numeroOS}</span>
                            </div>
                            <div class="status-badge ${statusClass}">
                                <i class="${statusIcon}"></i>
                                <span>${statusText}</span>
                            </div>
                        </div>
                        
                        <div class="card-body">
                            <div class="info-row">
                                <div class="info-item">
                                    <i class="bi bi-calendar3"></i>
                                    <div>
                                        <label>Data</label>
                                        <span>${dataFormatada}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="info-row">
                                <div class="info-item">
                                    <i class="bi bi-person"></i>
                                    <div>
                                        <label>Motorista</label>
                                        <span>${motoristaNome}</span>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="info-row">
                                <div class="info-item">
                                    <i class="bi bi-tag"></i>
                                    <div>
                                        <label>Tipo de Ocorrência</label>
                                        <span>${tipoNome}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card-footer">
                            <button class="btn btn-modern btn-process" onclick="abrirModalProcessarDP('${ocorrencia.id}')">
                                <i class="bi bi-cash-coin"></i>
                                <span>Processar</span>
                            </button>
                            <button class="btn btn-modern btn-view" onclick="visualizarOcorrencia('${ocorrencia.id}')">
                                <i class="bi bi-eye"></i>
                                <span>Visualizar</span>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // Abrir modal para processar no DP
    function abrirModalProcessarDP(id) {
        ocorrenciaSelecionada = ocorrencias.find(oc => oc.id === id);
        if (!ocorrenciaSelecionada) return;
        
        // Preencher dados da ocorrência
        const numeroOS = ocorrenciaSelecionada.numero_os || 'N/A';
        document.getElementById('dpModalNumeroOS').textContent = numeroOS;
        document.getElementById('dpOcorrenciaId').textContent = ocorrenciaSelecionada.id;
        document.getElementById('dpData').textContent = new Date(ocorrenciaSelecionada.criado_em).toLocaleString('pt-BR');
        document.getElementById('dpPorteiro').textContent = ocorrenciaSelecionada.porteiros?.nome || ocorrenciaSelecionada.porteiro_nome || 'N/A';
        document.getElementById('dpTipo').textContent = ocorrenciaSelecionada.tipos_relatorio?.nome || ocorrenciaSelecionada.tipo_nome || 'N/A';
        document.getElementById('dpDescricao').textContent = ocorrenciaSelecionada.dados || 'Nenhum conteúdo';
        
        // Limpar documentos anteriores
        documentosDP = [];
        document.getElementById('documentListDP').innerHTML = '';
        document.getElementById('valorCobranca').value = '';
        document.getElementById('motorista').value = '';
        
        const modal = new bootstrap.Modal(document.getElementById('modalProcessarDP'));
        modal.show();
    }
    
    // Visualizar arquivos selecionados para upload
    function previewFiles(files, containerId) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            documentosDP.push(file);
            
            const div = document.createElement('div');
            div.className = 'd-flex justify-content-between align-items-center border-bottom py-1';
            div.innerHTML = `
                <div><i class="bi bi-file-earmark"></i> ${file.name}</div>
                <button type="button" class="btn btn-sm btn-danger" onclick="removerDocumento(${i})">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            container.appendChild(div);
        }
    }
    
    // Remover documento da lista
    function removerDocumento(index) {
        documentosDP.splice(index, 1);
        // Recarregar a visualização
        const container = document.getElementById('documentListDP');
        container.innerHTML = '';
        documentosDP.forEach((file, i) => {
            const div = document.createElement('div');
            div.className = 'd-flex justify-content-between align-items-center border-bottom py-1';
            div.innerHTML = `
                <div><i class="bi bi-file-earmark"></i> ${file.name}</div>
                <button type="button" class="btn btn-sm btn-danger" onclick="removerDocumento(${i})">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            container.appendChild(div);
        });
    }
    
    // Confirmar processamento no DP (DP → Tráfego)
    async function confirmarProcessamentoDP() {
        if (!ocorrenciaSelecionada) return;
        
        const valor = document.getElementById('valorCobranca').value;
        const motorista = document.getElementById('motorista').value;
        
        if (!valor || !motorista) {
            alert('Por favor, preencha o valor e o motorista.');
            return;
        }
        
        try {
            // Simular upload de documentos (em produção seria feito para o servidor)
            const documentosNomes = documentosDP.map(file => file.name);
            
            // Validar e converter valor
            const valorNumerico = parseFloat(valor);
            if (isNaN(valorNumerico) || valorNumerico < 0) {
                alert('Por favor, insira um valor válido.');
                return;
            }
            
            const requestData = {
                status: 'EM_TRAFEGO',
                valor: valorNumerico,
                motorista: motorista.trim(),
                documentos: documentosNomes
            };
            
            console.log('Enviando dados:', requestData);
            
            const response = await fetch(`/api/relatorios/${ocorrenciaSelecionada.id}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // Fechar modal
                bootstrap.Modal.getInstance(document.getElementById('modalProcessarDP')).hide();
                
                alert('Ocorrência processada e enviada para o Tráfego com sucesso!');
                
                // Recarregar a página para mostrar as mudanças
                window.location.reload();
            } else {
                alert('Erro ao processar ocorrência: ' + (data.message || 'Erro desconhecido'));
            }
        } catch (error) {
            console.error('Erro ao processar ocorrência:', error);
            alert('Erro ao processar ocorrência. Tente novamente.');
        }
    }
    
    // Visualizar detalhes da ocorrência
    async function visualizarOcorrencia(id) {
        try {
            const response = await fetch(`/api/relatorios/${id}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const ocorrencia = await response.json();
            
            let conteudo = `Detalhes da Ocorrência #${ocorrencia.id}:\n\n`;
            conteudo += `Data: ${new Date(ocorrencia.criado_em).toLocaleString('pt-BR')}\n`;
            conteudo += `Porteiro: ${ocorrencia.porteiros?.nome || ocorrencia.porteiro_nome || 'N/A'}\n`;
            conteudo += `Tipo: ${ocorrencia.tipos_relatorio?.nome || ocorrencia.tipo_nome || 'N/A'}\n`;
            conteudo += `Status: ${ocorrencia.status || 'N/A'}\n\n`;
            conteudo += `Conteúdo:\n${ocorrencia.dados || 'Nenhum conteúdo'}`;
            
            alert(conteudo);
        } catch (error) {
            console.error('Erro ao visualizar ocorrência:', error);
            alert('Erro ao carregar detalhes da ocorrência.');
        }
    }
    
    // Inicializar a aplicação
    init();
    
    // Torna as funções globais para acesso pelo HTML
    window.abrirModalProcessarDP = abrirModalProcessarDP;
    window.previewFiles = previewFiles;
    window.removerDocumento = removerDocumento;
    window.visualizarOcorrencia = visualizarOcorrencia;
});