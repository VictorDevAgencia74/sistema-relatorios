// ==================================================
// FUNÇÕES GLOBAIS PARA O LIGHTBOX
// ==================================================

let fotosArray = [];
let currentPhotoIndex = 0;

function ampliarFoto(urlFoto, index = 0) {
    // console.log('🔍 ampliarFoto chamada:', urlFoto, index);
    
    // Coletar todas as fotos disponíveis
    const photoElements = document.querySelectorAll('#galeria-fotos img');
    fotosArray = Array.from(photoElements).map(img => img.src);
    
    currentPhotoIndex = index;

    // Criar ou reutilizar modal de lightbox
    let lightboxModal = document.getElementById('lightboxModal');
    if (!lightboxModal) {
        lightboxModal = document.createElement('div');
        lightboxModal.id = 'lightboxModal';
        lightboxModal.className = 'modal fade';
        lightboxModal.tabIndex = -1;
        lightboxModal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered modal-lg">
                <div class="modal-content bg-transparent border-0">
                    <div class="modal-header border-0 position-absolute top-0 end-0 z-3">
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center position-relative">
                        <button class="btn btn-light lightbox-nav-btn position-absolute start-0 top-50 translate-middle-y ms-3" 
                                onclick="navegarFoto(-1)" ${fotosArray.length <= 1 ? 'style="display:none;"' : ''}>
                            <i class="bi bi-chevron-left"></i>
                        </button>
                        
                        <img id="lightboxImage" src="" class="img-fluid" style="max-height: 70vh;" onerror="this.onerror=null; this.src='/placeholder-image.jpg'; this.alt='Imagem não disponível'">
                        
                        <button class="btn btn-light lightbox-nav-btn position-absolute end-0 top-50 translate-middle-y me-3" 
                                onclick="navegarFoto(1)" ${fotosArray.length <= 1 ? 'style="display:none;"' : ''}>
                            <i class="bi bi-chevron-right"></i>
                        </button>
                        
                        <div class="mt-3 position-absolute bottom-0 start-50 translate-middle-x mb-3">
                            <span class="photo-counter text-white bg-dark px-3 py-2 rounded-pill">${currentPhotoIndex + 1} / ${fotosArray.length}</span>
                            <button class="btn btn-sm btn-outline-light ms-2 px-3 py-2" onclick="downloadFotoAtual()">
                                <i class="bi bi-download"></i> Baixar
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(lightboxModal);
    }

    mostrarFotoAtual();
    const modal = new bootstrap.Modal(lightboxModal);
    modal.show();
}

function navegarFoto(direction) {
    currentPhotoIndex = (currentPhotoIndex + direction + fotosArray.length) % fotosArray.length;
    mostrarFotoAtual();
}

function mostrarFotoAtual() {
    if (fotosArray.length > 0 && currentPhotoIndex >= 0 && currentPhotoIndex < fotosArray.length) {
        const lightboxImage = document.getElementById('lightboxImage');
        if (lightboxImage) {
            lightboxImage.src = fotosArray[currentPhotoIndex];
            lightboxImage.alt = `Foto ${currentPhotoIndex + 1} do relatório`;
        }
        
        const photoCounter = document.querySelector('.photo-counter');
        if (photoCounter) {
            photoCounter.textContent = `${currentPhotoIndex + 1} / ${fotosArray.length}`;
        }
    }
}

function downloadFotoAtual() {
    if (fotosArray.length > 0 && currentPhotoIndex >= 0 && currentPhotoIndex < fotosArray.length) {
        const url = fotosArray[currentPhotoIndex];
        const nomeArquivo = `foto_relatorio_${currentPhotoIndex + 1}_${new Date().toISOString().split('T')[0]}.jpg`;
        downloadFoto(url, nomeArquivo);
    }
}

function downloadFoto(urlFoto, nomeArquivo = 'foto_relatorio.jpg') {
    fetch(urlFoto)
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = nomeArquivo;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => console.error('Erro ao baixar foto:', error));
}

// Função para verificar se uma URL de imagem é válida
function isValidImageUrl(url) {
    if (!url || typeof url !== 'string') return false;
    
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'];
    const urlLower = url.toLowerCase();
    
    return imageExtensions.some(ext => urlLower.includes(ext)) && 
           (urlLower.startsWith('http://') || urlLower.startsWith('https://'));
}

// Função para corrigir URL se necessário
function corrigirUrlFoto(url) {
    if (!url) return '';
    
    let urlCorrigida = url.trim();
    
    // Adiciona https:// se não tiver protocolo
    if (!urlCorrigida.startsWith('http')) {
        urlCorrigida = 'https://' + urlCorrigida;
    }
    
    // Corrige possíveis erros comuns no Supabase
    if (urlCorrigida.includes('supabase') && !urlCorrigida.includes('/object/public/')) {
        urlCorrigida = urlCorrigida.replace('/storage/v1/', '/storage/v1/object/public/');
    }
    
    return urlCorrigida;
}

// ==================================================
// CÓDIGO PRINCIPAL DO ADMIN
// ==================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ admin.js carregado com sucesso!');
    
    // Variáveis globais
    let currentPage = 1;
    const itemsPerPage = 10;
    let totalRelatorios = 0;
    let filtrosAtivos = {
        tipo: null,
        porteiro: null,
        dataInicio: null,
        dataFim: null,
        status: null,
        numeroOS: null,
        matricula: null,
        carro: null
    };
    let relatorioSelecionado = null;
    
    // Função para mostrar alertas
    function mostrarAlerta(mensagem, tipo = 'info') {
        const alertasExistentes = document.querySelectorAll('.alert');
        alertasExistentes.forEach(alerta => alerta.remove());
        
        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show mt-3`;
        alerta.role = 'alert';
        alerta.innerHTML = `
            ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container-fluid');
        container.prepend(alerta);
        
        setTimeout(() => {
            if (alerta.parentNode) {
                alerta.remove();
            }
        }, 5000);
    }
    
    // Inicialização
    async function init() {
        await carregarFiltros();
        configurarFiltroStatus();
        await carregarRelatorios();
        await carregarEstatisticas();
        configurarDatePicker();
        configurarEventos();
        configurarEventosExportacao();
    }
    
    // Configurar o filtro de status
    function configurarFiltroStatus() {
        const selectStatus = document.getElementById('filtroStatus');
        if (selectStatus) {
            selectStatus.innerHTML = `
                <option value="">Todos</option>
                <option value="PENDENTE">Pendente</option>
                <option value="EM_DP">Em DP</option>
                <option value="EM_TRAFEGO">Em Tráfego</option>
                <option value="COBRADO">Cobrado</option>
            `;
            
            selectStatus.addEventListener('change', async () => {
                filtrosAtivos.status = selectStatus.value || null;
                await aplicarFiltros();
            });
        }
    }
    
    // Configurar datepicker
    function configurarDatePicker() {
        const flatpickr = window.flatpickr;
        if (flatpickr) {
            flatpickr("#filtroData", {
                mode: "range",
                locale: "pt",
                dateFormat: "d/m/Y",
                onChange: function(selectedDates) {
                    if (selectedDates.length === 2) {
                        filtrosAtivos.dataInicio = selectedDates[0];
                        filtrosAtivos.dataFim = selectedDates[1];
                    } else {
                        filtrosAtivos.dataInicio = null;
                        filtrosAtivos.dataFim = null;
                    }
                }
            });
        }
    }
    
    // Configurar eventos
    function configurarEventos() {
        const btnFiltrar = document.getElementById('btnFiltrar');
        const btnLimpar = document.getElementById('btnLimpar');
        const btnFinalizarParaDP = document.getElementById('btnFinalizarParaDP');
        
        if (btnFiltrar) {
            btnFiltrar.addEventListener('click', async () => {
                currentPage = 1;
                await aplicarFiltros();
            });
        }
        
        if (btnLimpar) {
            btnLimpar.addEventListener('click', limparFiltros);
        }
        
        if (btnFinalizarParaDP) {
            btnFinalizarParaDP.addEventListener('click', finalizarParaDP);
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
    
    // Configurar eventos de exportação
    function configurarEventosExportacao() {
        const btnExportarHTML = document.getElementById('btnExportarHTML');
        const btnExportarPDF = document.getElementById('btnExportarPDF');
        
        if (btnExportarHTML) {
            btnExportarHTML.addEventListener('click', async (e) => {
                e.preventDefault();
                await exportarRelatorios();
            });
        }
        
        if (btnExportarPDF) {
            btnExportarPDF.addEventListener('click', async (e) => {
                e.preventDefault();
                await exportarParaPDF();
            });
        }
    }
    
    // Carregar opções de filtro
    async function carregarFiltros() {
        try {
            // Carregar tipos de relatório
            const responseTipos = await fetch('/api/tipos-relatorio');
            if (!responseTipos.ok) throw new Error(`HTTP error! status: ${responseTipos.status}`);
            const tipos = await responseTipos.json();
            
            if (tipos) {
                const selectTipo = document.getElementById('filtroTipo');
                selectTipo.innerHTML = '<option value="">Todos</option>';
                tipos.forEach(tipo => {
                    const option = document.createElement('option');
                    option.value = tipo.id;
                    option.textContent = tipo.nome;
                    selectTipo.appendChild(option);
                });
            }
            
            // Carregar porteiros
            const responsePorteiros = await fetch('/api/porteiros');
            if (!responsePorteiros.ok) throw new Error(`HTTP error! status: ${responsePorteiros.status}`);
            const porteiros = await responsePorteiros.json();
            
            if (porteiros) {
                const selectPorteiro = document.getElementById('filtroPorteiro');
                selectPorteiro.innerHTML = '<option value="">Todos</option>';
                porteiros.forEach(porteiro => {
                    const option = document.createElement('option');
                    option.value = porteiro.id;
                    option.textContent = porteiro.nome;
                    selectPorteiro.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Erro ao carregar filtros:', error);
            mostrarAlerta('Erro ao carregar opções de filtro', 'danger');
        }
    }
    
        // Aplicar filtros
    async function aplicarFiltros() {
        const tipoSelecionado = document.getElementById('filtroTipo').value;
        const porteiroSelecionado = document.getElementById('filtroPorteiro').value;
        const statusSelecionado = document.getElementById('filtroStatus').value;
        const numeroOSSelecionado = document.getElementById('filtroNumeroOS').value;
        const matriculaSelecionada = document.getElementById('filtroMatricula').value;
        const carroSelecionado = document.getElementById('filtroCarro').value;
        
        filtrosAtivos.tipo = tipoSelecionado || null;
        filtrosAtivos.porteiro = porteiroSelecionado || null;
        filtrosAtivos.status = statusSelecionado || null;
        filtrosAtivos.numeroOS = numeroOSSelecionado || null;
        filtrosAtivos.matricula = matriculaSelecionada || null;
        filtrosAtivos.carro = carroSelecionado || null;
        
        await carregarRelatorios();
        await carregarEstatisticas();
    }
    
    // Limpar filtros
    async function limparFiltros() {
        document.getElementById('filtroTipo').value = '';
        document.getElementById('filtroPorteiro').value = '';
        document.getElementById('filtroStatus').value = '';
        document.getElementById('filtroNumeroOS').value = '';
        document.getElementById('filtroMatricula').value = '';
        document.getElementById('filtroCarro').value = '';
        
        const datepicker = document.getElementById('filtroData');
        if (datepicker._flatpickr) {
            datepicker._flatpickr.clear();
        }
        
        filtrosAtivos = {
            tipo: null,
            porteiro: null,
            dataInicio: null,
            dataFim: null,
            status: null,
            numeroOS: null,
            matricula: null,
            carro: null
        };

        currentPage = 1;
        await carregarRelatorios();
        await carregarEstatisticas();
    }
    
    // Carregar relatórios
    async function carregarRelatorios() {
        const tabela = document.getElementById('tabelaRelatorios');
        tabela.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                </td>
            </tr>
        `;
        
        try {
            const params = new URLSearchParams({
                page: currentPage,
                per_page: itemsPerPage
            });
            
            if (filtrosAtivos.tipo) params.append('tipo', filtrosAtivos.tipo);
            if (filtrosAtivos.porteiro) params.append('porteiro', filtrosAtivos.porteiro);
            if (filtrosAtivos.status) params.append('status', filtrosAtivos.status);
            if (filtrosAtivos.numeroOS) params.append('numero_os', filtrosAtivos.numeroOS);
            if (filtrosAtivos.matricula) params.append('matricula', filtrosAtivos.matricula);
            if (filtrosAtivos.carro) params.append('carro', filtrosAtivos.carro);
            if (filtrosAtivos.dataInicio) params.append('data_inicio', formatarDataParaAPI(filtrosAtivos.dataInicio));
            if (filtrosAtivos.dataFim) params.append('data_fim', formatarDataParaAPI(filtrosAtivos.dataFim));
            
            const response = await fetch(`/api/relatorios?${params}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            totalRelatorios = data.count || 0;
            renderizarRelatorios(data.data || []);
            renderizarPaginacao();
        } catch (error) {
            console.error('Erro ao carregar relatórios:', error);
            tabela.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-danger">
                        Erro ao carregar relatórios. Tente novamente.
                    </td>
                </tr>
            `;
            mostrarAlerta('Erro ao carregar relatórios', 'danger');
        }
    }
    
    // Função auxiliar para formatar data para API
    function formatarDataParaAPI(data) {
        if (!data) return '';
        try {
            if (typeof data === 'string') return data.split('T')[0];
            return data.toISOString().split('T')[0];
        } catch (e) {
            console.error('Erro ao formatar data:', e);
            return '';
        }
    }
    
    // Renderizar relatórios na tabela
    function renderizarRelatorios(relatorios) {
        const tabela = document.getElementById('tabelaRelatorios');
        
        if (relatorios.length === 0) {
            tabela.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center">
                        Nenhum relatório encontrado com os filtros atuais.
                    </td>
                </tr>
            `;
            return;
        }

        tabela.innerHTML = relatorios.map(relatorio => {
            let dataFormatada = 'N/A';
            try {
                if (relatorio.criado_em) {
                    const data = new Date(relatorio.criado_em);
                    dataFormatada = data.toLocaleDateString('pt-BR');
                }
            } catch (e) {
                console.error('Erro ao formatar data:', e);
            }
            
            const tipoNome = relatorio.tipos_relatorio?.nome || relatorio.tipo_nome || relatorio.tipo_id || 'N/A';
            const porteiroNome = relatorio.porteiros?.nome || relatorio.porteiro_nome || relatorio.porteiro_id || 'N/A';
            const status = relatorio.status || 'PENDENTE';
            
            let statusBadge = '';
            switch(status) {
                case 'PENDENTE':
                    statusBadge = '<span class="badge bg-warning status-badge">Pendente</span>';
                    break;
                case 'EM_DP':
                    statusBadge = '<span class="badge bg-info status-badge">Em DP</span>';
                    break;
                case 'EM_TRAFEGO':
                    statusBadge = '<span class="badge bg-primary status-badge">Em Tráfego</span>';
                    break;
                case 'COBRADO':
                    statusBadge = '<span class="badge bg-success status-badge">Cobrado</span>';
                    break;
                default:
                    statusBadge = `<span class="badge bg-secondary status-badge">${status}</span>`;
            }
            
            let resumo = 'Nenhum conteúdo';
            if (relatorio.dados) {
                if (typeof relatorio.dados === 'string') {
                    const linhas = relatorio.dados.split('\n');
                    resumo = linhas.slice(0, 3).join(' | ');
                } else if (typeof relatorio.dados === 'object') {
                    resumo = JSON.stringify(relatorio.dados);
                }
            }

            const numeroOS = relatorio.numero_os || 'N/A';
            
            // Extrair informações do motorista e veículo dos dados
            let motorista = 'N/A';
            let veiculo = 'N/A';
            let motoes = 'N/A';
            
            if (relatorio.dados) {
                try {
                    // Se os dados são uma string, tentar extrair informações
                    if (typeof relatorio.dados === 'string') {
                        // Buscar por padrões comuns
                        const motoristaMatch = relatorio.dados.match(/motorista[:\s]+([^\n\r,]+)/i);
                        const veiculoMatch = relatorio.dados.match(/veículo[:\s]+([^\n\r,]+)/i) || 
                                           relatorio.dados.match(/carro[:\s]+([^\n\r,]+)/i) ||
                                           relatorio.dados.match(/placa[:\s]+([^\n\r,]+)/i);
                        const motoesMatch = relatorio.dados.match(/motões[:\s]+([^\n\r,]+)/i) ||
                                          relatorio.dados.match(/motao[:\s]+([^\n\r,]+)/i);
                        
                        if (motoristaMatch) motorista = motoristaMatch[1].trim();
                        if (veiculoMatch) veiculo = veiculoMatch[1].trim();
                        if (motoesMatch) motoes = motoesMatch[1].trim();
                    }
                    // Se os dados são um objeto, tentar acessar diretamente
                    else if (typeof relatorio.dados === 'object') {
                        motorista = relatorio.dados.motorista || relatorio.dados.motorista_matricula || 'N/A';
                        veiculo = relatorio.dados.veiculo || relatorio.dados.carro || relatorio.dados.placa || 'N/A';
                        motoes = relatorio.dados.motoes || relatorio.dados.motao || 'N/A';
                    }
                } catch (e) {
                    console.log('Erro ao extrair dados do motorista/veículo:', e);
                }
            }
            
            return `
                <tr>
                    <td><strong class="text-primary">${numeroOS}</strong></td>
                    <td>${dataFormatada}</td>
                    <td>${motorista}</td>
                    <td>${veiculo}</td>
                    <td>${tipoNome}</td>
                    <td>${statusBadge}</td>
                    <td>
                        <button class="btn btn-sm btn-primary btn-ver" data-id="${relatorio.id}">
                            <i class="bi bi-eye"></i> Ver
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        document.querySelectorAll('.btn-ver').forEach(btn => {
            btn.addEventListener('click', () => verRelatorioDetalhado(btn.dataset.id));
        });
    }
    
    // Renderizar paginação
    function renderizarPaginacao() {
        const totalPages = Math.ceil(totalRelatorios / itemsPerPage);
        const paginacao = document.getElementById('paginacao');
        
        if (totalPages <= 1) {
            paginacao.innerHTML = '';
            return;
        }

        let html = '';
        
        html += `
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage - 1}">Anterior</a>
            </li>
        `;

        const maxVisiblePages = 5;
        let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
        let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

        if (endPage - startPage + 1 < maxVisiblePages) {
            startPage = Math.max(1, endPage - maxVisiblePages + 1);
        }

        if (startPage > 1) {
            html += `
                <li class="page-item">
                    <a class="page-link" href="#" data-page="1">1</a>
                </li>
                ${startPage > 2 ? '<li class="page-item disabled"><span class="page-link">...</span></li>' : ''}
            `;
        }

        for (let i = startPage; i <= endPage; i++) {
            html += `
                <li class="page-item ${currentPage === i ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        }

        if (endPage < totalPages) {
            html += `
                ${endPage < totalPages - 1 ? '<li class="page-item disabled"><span class="page-link">...</span></li>' : ''}
                <li class="page-item">
                    <a class="page-link" href="#" data-page="${totalPages}">${totalPages}</a>
                </li>
            `;
        }

        html += `
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage + 1}">Próximo</a>
            </li>
        `;

        paginacao.innerHTML = html;

        document.querySelectorAll('.page-link').forEach(link => {
            if (link.parentElement.classList.contains('disabled')) return;
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                currentPage = parseInt(link.dataset.page);
                await carregarRelatorios();
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        });
    }
    
    // Carregar estatísticas
    async function carregarEstatisticas() {
        const container = document.getElementById('estatisticas');
        container.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
            </div>
        `;

        try {
            const params = new URLSearchParams();
            if (filtrosAtivos.tipo) params.append('tipo', filtrosAtivos.tipo);
            if (filtrosAtivos.porteiro) params.append('porteiro', filtrosAtivos.porteiro);
            if (filtrosAtivos.status) params.append('status', filtrosAtivos.status);
            if (filtrosAtivos.numeroOS) params.append('numero_os', filtrosAtivos.numeroOS);
            if (filtrosAtivos.matricula) params.append('matricula', filtrosAtivos.matricula);
            if (filtrosAtivos.carro) params.append('carro', filtrosAtivos.carro);
            if (filtrosAtivos.dataInicio) params.append('data_inicio', formatarDataParaAPI(filtrosAtivos.dataInicio));
            if (filtrosAtivos.dataFim) params.append('data_fim', formatarDataParaAPI(filtrosAtivos.dataFim));
            
            const response = await fetch(`/api/estatisticas?${params}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const data = await response.json();
            
            let html = `
                <div class="mb-3">
                    <h6 class="text-center">Total de Relatórios</h6>
                    <h2 class="text-center text-primary">${data.total || 0}</h2>
                </div>
                <div class="mb-3">
                    <h6 class="text-center">Status</h6>
                    <div class="d-flex justify-content-around flex-wrap">
            `;
            
            // Adicionar cada status
            for (const [status, count] of Object.entries(data.por_status || {})) {
                let badgeClass = 'bg-secondary';
                let statusText = status;
                
                switch(status) {
                    case 'PENDENTE':
                        badgeClass = 'bg-warning';
                        statusText = 'Pendentes';
                        break;
                    case 'EM_DP':
                        badgeClass = 'bg-info';
                        statusText = 'Em DP';
                        break;
                    case 'EM_TRAFEGO':
                        badgeClass = 'bg-primary';
                        statusText = 'Em Tráfego';
                        break;
                    case 'COBRADO':
                        badgeClass = 'bg-success';
                        statusText = 'Cobrados';
                        break;
                }
                
                html += `
                    <div class="text-center mb-2">
                        <span class="badge ${badgeClass}">${statusText}</span>
                        <div class="fw-bold">${count}</div>
                    </div>
                `;
            }
            
            html += `</div></div>`;
            container.innerHTML = html;
        } catch (error) {
            console.error('Erro ao carregar estatísticas:', error);
            container.innerHTML = `
                <div class="alert alert-danger">
                    Erro ao carregar estatísticas
                </div>
            `;
        }
    }
    
    // Função para ver relatório detalhado
    async function verRelatorioDetalhado(id) {
        try {
            // console.log("Buscando relatório com ID:", id);
            
            const response = await fetch(`/api/relatorios/${encodeURIComponent(id)}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const relatorio = await response.json();
            relatorioSelecionado = relatorio;
            
            const modalTitulo = document.getElementById('modalTitulo');
            const modalCorpo = document.getElementById('modalCorpo');
            const btnFinalizarParaDP = document.getElementById('btnFinalizarParaDP');
            
            const numeroOS = relatorio.numero_os || 'N/A';
            modalTitulo.textContent = `Relatório ${numeroOS}`;
            
            let dataFormatada = 'N/A';
            try {
                if (relatorio.criado_em) {
                    const data = new Date(relatorio.criado_em);
                    dataFormatada = data.toLocaleDateString('pt-BR') + ' ' + data.toLocaleTimeString('pt-BR');
                }
            } catch (e) {
                console.error('Erro ao formatar data:', e);
            }
            
            const tipoNome = relatorio.tipos_relatorio?.nome || relatorio.tipo_nome || relatorio.tipo_id || 'N/A';
            const porteiroNome = relatorio.porteiros?.nome || relatorio.porteiro_nome || relatorio.porteiro_id || 'N/A';
            
            let fotosHTML = '';
            let fotosArray = [];

            if (relatorio.fotos) {
                try {
                    // console.log('Fotos do relatório:', relatorio.fotos);
                    
                    // Processar as fotos
                    fotosArray = processarFotos(relatorio.fotos);
                    // console.log('Fotos processadas:', fotosArray);
                    
                    // Gera o HTML das miniaturas
                    if (fotosArray.length > 0) {
                        fotosHTML = `<div class="mb-3">
                            <strong>Fotos do Relatório:</strong>
                            <div class="mt-2 d-flex flex-wrap gap-2" id="galeria-fotos">`;

                        fotosArray.forEach((urlFoto, index) => {
                            if (urlFoto && typeof urlFoto === 'string') {
                                // Garante que a URL é válida
                                let urlFinal = corrigirUrlFoto(urlFoto);
                                
                                // Escapa aspas simples para evitar quebra de HTML
                                const urlEscapada = urlFinal.replace(/'/g, "\\'");
                                
                                fotosHTML += `
                                    <div class="position-relative" style="width: 100px; height: 100px;">
                                        <img src="${urlFinal}" 
                                            class="img-thumbnail h-100 w-100" 
                                            style="object-fit: cover; cursor: pointer; border-radius: 4px;" 
                                            alt="Foto ${index + 1}"
                                            onclick="ampliarFoto('${urlEscapada}', ${index})"
                                            data-bs-toggle="tooltip" 
                                            title="Clique para ampliar"
                                            onerror="this.onerror=null; this.style.display='none'; this.nextElementSibling.style.display='block';"
                                            loading="lazy">
                                        
                                        <div class="position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center bg-light border rounded" 
                                            style="display: none; cursor: pointer;"
                                            onclick="ampliarFoto('${urlEscapada}', ${index})"
                                            title="Imagem não disponível - Clique para tentar abrir">
                                            <i class="bi bi-image text-muted" style="font-size: 24px;"></i>
                                        </div>
                                        
                                        <span class="position-absolute top-0 end-0 translate-middle badge rounded-pill bg-dark" 
                                            style="font-size: 10px; transform: translate(25%, -25%);">
                                            ${index + 1}
                                        </span>
                                    </div>
                                `;
                            }
                        });

                        fotosHTML += `</div></div>`;
                    }
                        
                } catch (e) {
                    console.error('Erro ao processar fotos:', e);
                    fotosHTML = `<div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle"></i> Erro ao carregar galeria de fotos.
                    </div>`;
                }
            }

            // Mostrar ou ocultar botão de finalizar
            if (relatorio.status === 'PENDENTE') {
                btnFinalizarParaDP.style.display = 'block';
            } else {
                btnFinalizarParaDP.style.display = 'none';
            }

            // Extrair informações do motorista e veículo para o modal
            let motoristaModal = 'N/A';
            let veiculoModal = 'N/A';
            let matriculaModal = 'N/A';
            
            if (relatorio.dados) {
                try {
                    if (typeof relatorio.dados === 'string') {
                        const motoristaMatch = relatorio.dados.match(/motorista[:\s]+([^\n\r,]+)/i);
                        const veiculoMatch = relatorio.dados.match(/veículo[:\s]+([^\n\r,]+)/i) || 
                                           relatorio.dados.match(/carro[:\s]+([^\n\r,]+)/i) ||
                                           relatorio.dados.match(/placa[:\s]+([^\n\r,]+)/i);
                        const matriculaMatch = relatorio.dados.match(/matrícula[:\s]+([^\n\r,]+)/i) ||
                                             relatorio.dados.match(/matricula[:\s]+([^\n\r,]+)/i) ||
                                             relatorio.dados.match(/mat[:\s]+([^\n\r,]+)/i);
                        
                        if (motoristaMatch) motoristaModal = motoristaMatch[1].trim();
                        if (veiculoMatch) veiculoModal = veiculoMatch[1].trim();
                        if (matriculaMatch) matriculaModal = matriculaMatch[1].trim();
                    } else if (typeof relatorio.dados === 'object') {
                        motoristaModal = relatorio.dados.motorista || relatorio.dados.motorista_nome || 'N/A';
                        veiculoModal = relatorio.dados.veiculo || relatorio.dados.carro || relatorio.dados.placa || 'N/A';
                        matriculaModal = relatorio.dados.matricula || relatorio.dados.motorista_matricula || 'N/A';
                    }
                } catch (e) {
                    console.log('Erro ao extrair dados para modal:', e);
                }
            }
            
            modalCorpo.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <div class="mb-3">
                            <strong>Data:</strong> ${dataFormatada}
                        </div>
                        <div class="mb-3">
                            <strong>Tipo:</strong> ${tipoNome}
                        </div>
                        <div class="mb-3">
                            <strong>Porteiro:</strong> ${porteiroNome}
                        </div>
                        <div class="mb-3">
                            <strong>Status:</strong> 
                            <span class="badge ${relatorio.status === 'PENDENTE' ? 'bg-warning' : relatorio.status === 'EM_DP' ? 'bg-info' : relatorio.status === 'EM_TRAFEGO' ? 'bg-primary' : 'bg-success'}">
                                ${relatorio.status || 'PENDENTE'}
                            </span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="mb-3">
                            <strong>Motorista:</strong> <span class="badge bg-info">${motoristaModal}</span>
                        </div>
                        <div class="mb-3">
                            <strong>Veículo:</strong> <span class="badge bg-secondary">${veiculoModal}</span>
                        </div>
                        <div class="mb-3">
                            <strong>Matrícula:</strong> <span class="badge bg-warning">${matriculaModal}</span>
                        </div>
                    </div>
                </div>
                ${fotosHTML}
                <div class="mb-3">
                    <strong>Conteúdo:</strong>
                    <pre class="bg-light p-3 mt-2">${relatorio.dados || 'Nenhum conteúdo'}</pre>
                </div>
            `;

            // Inicializa tooltips
            const tooltipTriggerList = [].slice.call(modalCorpo.querySelectorAll('[data-bs-toggle="tooltip"]'));
            tooltipTriggerList.map(function (tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
            
            const modal = new bootstrap.Modal(document.getElementById('modalRelatorio'));
            modal.show();
            
        } catch (error) {
            console.error('Erro ao carregar relatório:', error);
            mostrarAlerta('Erro ao carregar detalhes do relatório', 'danger');
        }
    }

    // Nova função para processar fotos
    function processarFotos(fotos) {
        if (!fotos) return [];
        
        let fotosArray = [];
        
        try {
            // Se for string, tenta parsear como JSON
            if (typeof fotos === 'string') {
                try {
                    fotos = JSON.parse(fotos);
                } catch (e) {
                    // Se não for JSON válido, trata como string única
                    fotosArray = [fotos];
                    return fotosArray;
                }
            }
            
            // Se for array, usa diretamente
            if (Array.isArray(fotos)) {
                fotosArray = fotos.filter(url => url && typeof url === 'string');
                return fotosArray;
            }
            
            // Se for objeto, extrai os valores
            if (typeof fotos === 'object' && fotos !== null) {
                fotosArray = Object.values(fotos).filter(url => url && typeof url === 'string');
                return fotosArray;
            }
            
        } catch (e) {
            console.error('Erro no processamento de fotos:', e);
        }
        
        return fotosArray;
    }
    
    // Finalizar relatório (admin → dp)
    function finalizarRelatorio(id) {
        relatorioSelecionado = { id: id };
        document.getElementById('btnFinalizarParaDP').click();
    }
    
    // Finalizar para DP
    async function finalizarParaDP() {
        if (!relatorioSelecionado) return;
        
        try {
            const response = await fetch(`/api/relatorios/${relatorioSelecionado.id}/status`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    status: 'EM_DP'
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                mostrarAlerta('Relatório enviado para o Departamento Pessoal com sucesso!', 'success');
                
                // Verificar se o modal ainda existe antes de tentar fechá-lo
                const modalElement = document.getElementById('modalRelatorio');
                if (modalElement) {
                    const modalInstance = bootstrap.Modal.getInstance(modalElement);
                    if (modalInstance) {
                        modalInstance.hide();
                    }
                }
                
                await carregarRelatorios();
                await carregarEstatisticas();
            } else {
                mostrarAlerta('Erro ao enviar relatório para DP: ' + data.message, 'danger');
            }
        } catch (error) {
            console.error('Erro ao finalizar relatório:', error);
            mostrarAlerta('Erro ao enviar relatório para DP', 'danger');
        }
    }
    
    // Função para exportar relatórios em HTML
    async function exportarRelatorios() {
        try {
            const params = new URLSearchParams();
            if (filtrosAtivos.tipo) params.append('tipo', filtrosAtivos.tipo);
            if (filtrosAtivos.porteiro) params.append('porteiro', filtrosAtivos.porteiro);
            if (filtrosAtivos.status) params.append('status', filtrosAtivos.status);
            if (filtrosAtivos.numeroOS) params.append('numero_os', filtrosAtivos.numeroOS);
            if (filtrosAtivos.matricula) params.append('matricula', filtrosAtivos.matricula);
            if (filtrosAtivos.carro) params.append('carro', filtrosAtivos.carro);
            if (filtrosAtivos.dataInicio) params.append('data_inicio', formatarDataParaAPI(filtrosAtivos.dataInicio));
            if (filtrosAtivos.dataFim) params.append('data_fim', formatarDataParaAPI(filtrosAtivos.dataFim));
            
            const response = await fetch(`/api/exportar/html?${params}`);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `relatorios_${new Date().toISOString().split('T')[0]}.html`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            
            mostrarAlerta('Relatórios exportados com sucesso!', 'success');
        } catch (error) {
            console.error('Erro ao exportar relatórios:', error);
            mostrarAlerta('Erro ao exportar relatórios', 'danger');
        }
    }
    
    // Inicializar aplicação quando o DOM estiver carregado
    init();
});