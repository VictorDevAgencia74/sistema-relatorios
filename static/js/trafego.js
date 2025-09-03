document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ trafego.js carregado com sucesso!');
    
    let ocorrencias = [];
    let ocorrenciaSelecionada = null;
    
    // Inicialização
    async function init() {
        configurarEventos();
        await carregarOcorrenciasTrafego();
    }
    
    // Configurar eventos
    function configurarEventos() {
        const btnAtualizar = document.getElementById('btnAtualizarTrafego');
        const btnMarcarComoCobrado = document.getElementById('btnMarcarComoCobrado');
        
        if (btnAtualizar) {
            btnAtualizar.addEventListener('click', carregarOcorrenciasTrafego);
        }
        
        if (btnMarcarComoCobrado) {
            btnMarcarComoCobrado.addEventListener('click', marcarComoCobrado);
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
    
    // Carregar ocorrências para o Tráfego
    async function carregarOcorrenciasTrafego() {
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
            const response = await fetch('/api/relatorios?status=EM_TRAFEGO');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            ocorrencias = data.data || [];
            
            // Esconder loading
            if (loadingState) {
                loadingState.style.display = 'none';
            }
            renderizarOcorrenciasTrafego();
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
                        <button class="btn btn-modern btn-primary" onclick="carregarOcorrenciasTrafego()">
                            <i class="bi bi-arrow-clockwise"></i> Tentar Novamente
                        </button>
                    </div>
                </div>
            `;
        }
    }
    
    // Renderizar ocorrências em cards modernos
    function renderizarOcorrenciasTrafego() {
        const container = document.getElementById('ocorrenciasContainer');
        
        if (ocorrencias.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="empty-state">
                        <i class="bi bi-inbox"></i>
                        <h4>Nenhuma ocorrência encontrada</h4>
                        <p>Não há ocorrências para cobrança no momento.</p>
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
            const porteiroNome = ocorrencia.porteiros?.nome || ocorrencia.porteiro_nome || ocorrencia.porteiro_id || 'N/A';
            
            // Extrair nome do motorista
            let motoristaNome = 'N/A';
            if (ocorrencia.motorista) {
                motoristaNome = ocorrencia.motorista;
            } else if (ocorrencia.dados) {
                try {
                    if (typeof ocorrencia.dados === 'string') {
                        const motoristaMatch = ocorrencia.dados.match(/motorista[:\s]+([^\n\r,]+)/i);
                        if (motoristaMatch) {
                            motoristaNome = motoristaMatch[1].trim();
                        }
                    } else if (typeof ocorrencia.dados === 'object') {
                        motoristaNome = ocorrencia.dados.motorista || ocorrencia.dados.motorista_matricula || 'N/A';
                    }
                } catch (e) {
                    console.log('Erro ao extrair dados do motorista:', e);
                }
            }
            
            const valor = ocorrencia.valor ? `R$ ${ocorrencia.valor.toFixed(2)}` : 'R$ 0,00';
            const numeroOS = ocorrencia.numero_os || 'N/A';
            
            return `
                <div class="col-lg-6 col-xl-4 mb-4">
                    <div class="modern-card trafego-card" data-id="${ocorrencia.id}">
                        <div class="card-header">
                            <div class="os-number">
                                <i class="bi bi-file-text"></i>
                                <span>${numeroOS}</span>
                            </div>
                            <div class="status-badge status-traffic">
                                <i class="bi bi-truck"></i>
                                <span>Para Cobrança</span>
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
                                    <i class="bi bi-person-badge"></i>
                                    <div>
                                        <label>Porteiro</label>
                                        <span>${porteiroNome}</span>
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
                            
                            <div class="info-row">
                                <div class="info-item">
                                    <i class="bi bi-currency-dollar"></i>
                                    <div>
                                        <label>Valor</label>
                                        <span class="valor-destaque">${valor}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card-footer">
                            <button class="btn btn-modern btn-view" onclick="abrirModalVisualizarTrafego('${ocorrencia.id}')">
                                <i class="bi bi-eye"></i>
                                <span>Visualizar</span>
                            </button>
                            <button class="btn btn-modern btn-cobrado" onclick="marcarComoCobrado('${ocorrencia.id}')">
                                <i class="bi bi-check-circle"></i>
                                <span>Marcar Cobrado</span>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // Abrir modal para visualizar no Tráfego
    function abrirModalVisualizarTrafego(id) {
        ocorrenciaSelecionada = ocorrencias.find(oc => oc.id === id);
        if (!ocorrenciaSelecionada) return;
        
        // Preencher dados da ocorrência
        const numeroOS = ocorrenciaSelecionada.numero_os || 'N/A';
        document.getElementById('trafegoModalNumeroOS').textContent = numeroOS;
        document.getElementById('trafegoOcorrenciaId').textContent = ocorrenciaSelecionada.id;
        document.getElementById('trafegoData').textContent = new Date(ocorrenciaSelecionada.criado_em).toLocaleString('pt-BR');
        document.getElementById('trafegoPorteiro').textContent = ocorrenciaSelecionada.porteiros?.nome || ocorrenciaSelecionada.porteiro_nome || 'N/A';
        document.getElementById('trafegoMotorista').textContent = ocorrenciaSelecionada.motorista || 'N/A';
        document.getElementById('trafegoValor').textContent = ocorrenciaSelecionada.valor ? ocorrenciaSelecionada.valor.toFixed(2) : '0,00';
        
        // Listar documentos
        const container = document.getElementById('documentosTrafego');
        container.innerHTML = '';
        
        if (ocorrenciaSelecionada.documentos && ocorrenciaSelecionada.documentos.length > 0) {
            ocorrenciaSelecionada.documentos.forEach(doc => {
                const div = document.createElement('div');
                div.className = 'd-flex justify-content-between align-items-center border-bottom py-1';
                div.innerHTML = `
                    <div><i class="bi bi-file-earmark"></i> ${doc}</div>
                    <button type="button" class="btn btn-sm btn-primary">
                        <i class="bi bi-download"></i> Baixar
                    </button>
                `;
                container.appendChild(div);
            });
        } else {
            container.innerHTML = '<p class="text-muted">Nenhum documento anexado</p>';
        }
        
        const modal = new bootstrap.Modal(document.getElementById('modalVisualizarTrafego'));
        modal.show();
    }
    
    // Marcar como cobrado (Tráfego)
    async function marcarComoCobrado(id) {
        const ocorrencia = ocorrencias.find(oc => oc.id === id);
        if (!ocorrencia) return;
        
        if (!confirm('Tem certeza que deseja marcar esta cobrança como realizada?')) {
            return;
        }
        
        try {
            const requestData = {
                status: 'COBRADO'
            };
            
            console.log('Enviando dados:', requestData);
            
            const response = await fetch(`/api/relatorios/${id}/status`, {
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
                alert('Cobrança marcada como realizada com sucesso!');
                
                // Recarregar a página para mostrar as mudanças
                window.location.reload();
            } else {
                alert('Erro ao marcar como cobrado: ' + (data.message || 'Erro desconhecido'));
            }
        } catch (error) {
            console.error('Erro ao marcar como cobrado:', error);
            alert('Erro ao marcar como cobrado. Tente novamente.');
        }
    }
    
    // Inicializar a aplicação
    init();
    
    // Torna as funções globais para acesso pelo HTML
    window.abrirModalVisualizarTrafego = abrirModalVisualizarTrafego;
    window.marcarComoCobrado = marcarComoCobrado;
});