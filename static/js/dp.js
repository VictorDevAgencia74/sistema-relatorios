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
        const tabela = document.getElementById('tabelaDP');
        tabela.innerHTML = `
            <tr>
                <td colspan="7" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                </td>
            </tr>
        `;
        
        try {
            const response = await fetch('/api/relatorios?status=EM_DP');
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            ocorrencias = data.data || [];
            renderizarOcorrenciasDP();
        } catch (error) {
            console.error('Erro ao carregar ocorrências:', error);
            tabela.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center text-danger">
                        Erro ao carregar ocorrências. Tente novamente.
                    </td>
                </tr>
            `;
        }
    }
    
    // Renderizar ocorrências na tabela
    function renderizarOcorrenciasDP() {
        const tabela = document.getElementById('tabelaDP');
        
        if (ocorrencias.length === 0) {
            tabela.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center">
                        Nenhuma ocorrência para processar.
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
            
            const numeroOS = ocorrencia.numero_os || 'N/A';
            
            return `
                <tr>
                    <td><strong class="text-primary">${numeroOS}</strong></td>
                    <td>${dataFormatada}</td>
                    <td>${porteiroNome}</td>
                    <td>${tipoNome}</td>
                    <td>${ocorrencia.dados ? (typeof ocorrencia.dados === 'string' ? ocorrencia.dados.substring(0, 50) + (ocorrencia.dados.length > 50 ? '...' : '') : JSON.stringify(ocorrencia.dados).substring(0, 50) + '...') : 'Nenhum conteúdo'}</td>
                    <td><span class="badge bg-info status-badge">Em análise</span></td>
                    <td>
                        <button class="btn btn-sm btn-success action-btn" onclick="abrirModalProcessarDP('${ocorrencia.id}')">
                            <i class="bi bi-cash-coin"></i> Processar
                        </button>
                        <button class="btn btn-sm btn-info action-btn" onclick="visualizarOcorrencia('${ocorrencia.id}')">
                            <i class="bi bi-eye"></i> Visualizar
                        </button>
                    </td>
                </tr>
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
            
            const response = await fetch(`/api/relatorios/${ocorrenciaSelecionada.id}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    status: 'EM_TRAFEGO',
                    valor: parseFloat(valor),
                    motorista: motorista,
                    documentos: documentosNomes
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Fechar modal e atualizar tabela
                bootstrap.Modal.getInstance(document.getElementById('modalProcessarDP')).hide();
                await carregarOcorrenciasDP();
                
                alert('Ocorrência processada e enviada para o Tráfego com sucesso!');
            } else {
                alert('Erro ao processar ocorrência: ' + data.message);
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