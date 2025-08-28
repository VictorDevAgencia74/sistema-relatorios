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
        const tabela = document.getElementById('tabelaTrafego');
        tabela.innerHTML = `
            <tr>
                <td colspan="8" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                </td>
            </tr>
        `;
        
        try {
            const response = await fetch('/api/relatorios?status=EM_TRAFEGO');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            ocorrencias = data.data || [];
            renderizarOcorrenciasTrafego();
        } catch (error) {
            console.error('Erro ao carregar ocorrências:', error);
            tabela.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center text-danger">
                        Erro ao carregar ocorrências. Tente novamente.
                    </td>
                </tr>
            `;
        }
    }
    
    // Renderizar ocorrências na tabela
    function renderizarOcorrenciasTrafego() {
        const tabela = document.getElementById('tabelaTrafego');
        
        if (ocorrencias.length === 0) {
            tabela.innerHTML = `
                <tr>
                    <td colspan="8" class="text-center">
                        Nenhuma ocorrência para cobrança.
                    </td>
                </tr>
            `;
            return;
        }

        tabela.innerHTML = ocorrencias.map(ocorrencia => {
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
            const motorista = ocorrencia.motorista || 'N/A';
            const valor = ocorrencia.valor ? `R$ ${ocorrencia.valor.toFixed(2)}` : 'R$ 0,00';
            
            return `
                <tr>
                    <td>${ocorrencia.id}</td>
                    <td>${dataFormatada}</td>
                    <td>${porteiroNome}</td>
                    <td>${motorista}</td>
                    <td>${tipoNome}</td>
                    <td>${valor}</td>
                    <td><span class="badge bg-primary status-badge">Para cobrança</span></td>
                    <td>
                        <button class="btn btn-sm btn-info action-btn" onclick="abrirModalVisualizarTrafego('${ocorrencia.id}')">
                            <i class="bi bi-eye"></i> Visualizar
                        </button>
                    </td>
                </tr>
            `;
        }).join('');
    }
    
    // Abrir modal para visualizar no Tráfego
    function abrirModalVisualizarTrafego(id) {
        ocorrenciaSelecionada = ocorrencias.find(oc => oc.id === id);
        if (!ocorrenciaSelecionada) return;
        
        // Preencher dados da ocorrência
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
    async function marcarComoCobrado() {
        if (!ocorrenciaSelecionada) return;
        
        try {
            const response = await fetch(`/api/relatorios/${ocorrenciaSelecionada.id}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    status: 'COBRADO'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Fechar modal e atualizar tabela
                bootstrap.Modal.getInstance(document.getElementById('modalVisualizarTrafego')).hide();
                await carregarOcorrenciasTrafego();
                
                alert('Cobrança marcada como realizada com sucesso!');
            } else {
                alert('Erro ao marcar como cobrado: ' + data.message);
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
});