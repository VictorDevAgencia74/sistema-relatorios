// static/js/app.js - VERSÃO COMPLETA CORRIGIDA
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ app.js carregado com sucesso!');
    
    // Elementos da interface
    const tipoRelatorio = document.getElementById('tipoRelatorio');
    const formContainer = document.getElementById('formContainer');
    const preview = document.getElementById('preview');
    const textoRelatorio = document.getElementById('textoRelatorio');
    const btnEnviar = document.getElementById('btnEnviar');
    const nomePorteiro = document.getElementById('nomePorteiro');
    const logoutBtn = document.getElementById('logoutBtn');
    const loadingTipos = document.getElementById('loadingTipos');
    
    let usuarioLogado = null;
    let tiposRelatorio = [];
    let fotosAvaria = {};
    
    // Inicialização
    async function init() {
        console.log('Iniciando app do porteiro...');
        
        // Verificar autenticação primeiro
        await verificarAutenticacao();
        
        // Configurar eventos
        configurarEventos();
        
        // Carregar tipos de relatório
        await carregarTiposRelatorio();
        
        console.log('App do porteiro inicializado com sucesso!');
    }
    
    // Configurar eventos
    function configurarEventos() {
        if (tipoRelatorio) {
            tipoRelatorio.addEventListener('change', function() {
                const tipoId = this.value;
                const tipoSelecionado = tiposRelatorio.find(t => t.id == tipoId);
                
                console.log('Tipo selecionado:', tipoSelecionado);
                
                if (!tipoSelecionado) {
                    if (formContainer) formContainer.innerHTML = '';
                    if (preview) preview.classList.add('d-none');
                    if (btnEnviar) btnEnviar.classList.add('d-none');
                    fotosAvaria = {};
                    return;
                }
                
                // Gerar formulário dinâmico
                gerarFormulario(tipoSelecionado);
                
                if (preview) preview.classList.remove('d-none');
                if (btnEnviar) btnEnviar.classList.remove('d-none');
                atualizarPreview();
            });
        }
        
        if (btnEnviar) {
            btnEnviar.addEventListener('click', async function() {
                await enviarRelatorio();
            });
        }
        
        if (logoutBtn) {
            logoutBtn.addEventListener('click', function(e) {
                e.preventDefault();
                fazerLogout();
            });
        }
    }
    
    // Função para verificar autenticação
    async function verificarAutenticacao() {
        try {
            console.log('Verificando autenticação...');
            const response = await fetch('/api/check-auth');
            const data = await response.json();
            
            if (data.success && data.user.setor === 'porteiro') {
                usuarioLogado = data.user;
                console.log('Usuário autenticado:', usuarioLogado);
                
                // Mostrar nome do porteiro
                if (nomePorteiro) {
                    nomePorteiro.textContent = usuarioLogado.nome;
                }
            } else {
                console.log('Usuário não autenticado, redirecionando...');
                // Redirecionar para login se não estiver autenticado
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Erro ao verificar autenticação:', error);
            window.location.href = '/';
        }
    }
    
    // Função para fazer logout
    async function fazerLogout() {
        try {
            const response = await fetch('/api/logout', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                window.location.href = '/';
            }
        } catch (error) {
            console.error('Erro ao fazer logout:', error);
            window.location.href = '/';
        }
    }
    
    // Carregar tipos de relatório
    async function carregarTiposRelatorio() {
        try {
            console.log('Carregando tipos de relatório...');
            
            // Mostrar loading e ocultar select
            if (loadingTipos) loadingTipos.style.display = 'block';
            if (tipoRelatorio) tipoRelatorio.style.display = 'none';
            
            const response = await fetch('/api/tipos-relatorio');
            
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            
            tiposRelatorio = await response.json();
            console.log('Tipos de relatório carregados:', tiposRelatorio);
            
            if (tipoRelatorio && tiposRelatorio.length > 0) {
                tipoRelatorio.innerHTML = '<option value="">Selecione o tipo de relatório</option>';
                
                tiposRelatorio.forEach(tipo => {
                    const option = document.createElement('option');
                    option.value = tipo.id;
                    option.textContent = tipo.nome;
                    tipoRelatorio.appendChild(option);
                });
                
                // Ocultar loading e mostrar select
                if (loadingTipos) loadingTipos.style.display = 'none';
                if (tipoRelatorio) tipoRelatorio.style.display = 'block';
                
                console.log('Dropdown de tipos preenchido com sucesso');
            } else {
                console.warn('Nenhum tipo de relatório encontrado');
                if (loadingTipos) {
                    loadingTipos.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Nenhum tipo de relatório configurado';
                    loadingTipos.className = 'alert alert-warning';
                }
            }
        } catch (error) {
            console.error('Erro ao carregar tipos:', error);
            
            if (loadingTipos) {
                loadingTipos.innerHTML = '<i class="bi bi-exclamation-triangle"></i> Erro ao carregar tipos de relatório';
                loadingTipos.className = 'alert alert-danger';
            }
            
            mostrarAlerta('Erro ao carregar tipos de relatório', 'danger');
        }
    }
    
    // Função para gerar formulário
    function gerarFormulario(tipo) {
        if (!formContainer) return;
        
        formContainer.innerHTML = '';
        fotosAvaria = {};
        
        try {
            // Verifica se campos é string JSON ou já é objeto
            const campos = typeof tipo.campos === 'string' 
                ? JSON.parse(tipo.campos) 
                : tipo.campos;
            
            console.log('Campos parseados:', campos);
            
            campos.forEach(campo => {
                const div = document.createElement('div');
                div.className = 'mb-3';
                
                const label = document.createElement('label');
                label.className = 'form-label';
                label.textContent = campo.label + (campo.required ? ' *' : '');
                label.htmlFor = campo.name;
                
                let input;
                
                if (campo.type === 'select') {
                    input = document.createElement('select');
                    input.className = 'form-select';
                    input.required = campo.required || false;
                    input.id = campo.name;
                    input.name = campo.name;
                    
                    if (!campo.required) {
                        const emptyOption = document.createElement('option');
                        emptyOption.value = '';
                        emptyOption.textContent = 'Selecione...';
                        input.appendChild(emptyOption);
                    }
                    
                    campo.options.forEach(opcao => {
                        const option = document.createElement('option');
                        option.value = opcao;
                        option.textContent = opcao;
                        input.appendChild(option);
                    });
                    
                    input.addEventListener('change', atualizarPreview);
                } 
                else if (campo.type === 'file') {
                    input = document.createElement('input');
                    input.type = 'file';
                    input.accept = 'image/*';
                    input.capture = 'environment';
                    input.className = 'form-control';
                    input.multiple = false;
                    input.name = campo.name;
                    input.id = campo.name;
                    
                    const previewContainer = document.createElement('div');
                    previewContainer.className = 'mt-2';
                    
                    input.addEventListener('change', function(e) {
                        if (e.target.files && e.target.files[0]) {
                            const reader = new FileReader();
                            reader.onload = function(event) {
                                fotosAvaria[campo.name] = {
                                    file: e.target.files[0],
                                    preview: event.target.result,
                                    indice: 0,
                                    publicUrl: ''
                                };
                                
                                previewContainer.innerHTML = `
                                    <img src="${event.target.result}" class="img-thumbnail mt-2" style="max-width: 150px;">
                                    <button type="button" class="btn btn-sm btn-danger ms-2" onclick="removerFoto('${campo.name}')">
                                        Remover
                                    </button>
                                `;
                                atualizarPreview();
                            };
                            reader.readAsDataURL(e.target.files[0]);
                        }
                    });
                    
                    div.appendChild(label);
                    div.appendChild(input);
                    div.appendChild(previewContainer);
                    formContainer.appendChild(div);
                    return;
                }
                else {
                    input = document.createElement('input');
                    input.type = campo.type;
                    input.className = 'form-control';
                    input.required = campo.required || false;
                    input.placeholder = campo.placeholder || '';
                    input.id = campo.name;
                    input.name = campo.name;
                    input.addEventListener('input', atualizarPreview);
                }
                
                div.appendChild(label);
                div.appendChild(input);
                formContainer.appendChild(div);
            });
            
        } catch (error) {
            console.error('Erro ao gerar formulário:', error);
            formContainer.innerHTML = `
                <div class="alert alert-danger">
                    Erro ao carregar formulário: ${error.message}
                </div>
            `;
        }
    }
    
    // Função para atualizar preview
    function atualizarPreview() {
        try {
            const tipoSelect = document.getElementById('tipoRelatorio');
            if (!tipoSelect) return;
            
            const tipoId = tipoSelect.value;
            const tipoSelecionado = tiposRelatorio.find(t => t.id == tipoId);
            
            if (!tipoSelecionado) return;
            
            let texto = `${tipoSelecionado.nome.toUpperCase()}\n\n`;
            const dataAtual = new Date();
            
            texto += `Data: ${dataAtual.toLocaleDateString('pt-BR')} ${dataAtual.toLocaleTimeString('pt-BR')}\n`;
            texto += `Porteiro: ${usuarioLogado?.nome || 'Não identificado'}\n\n`;
            
            const campos = typeof tipoSelecionado.campos === 'string' 
                ? JSON.parse(tipoSelecionado.campos) 
                : tipoSelecionado.campos;
            
            campos.forEach(campo => {
                if (campo.type !== 'file') {
                    const elemento = document.getElementById(campo.name);
                    const valor = elemento?.value || (campo.default || '');
                    texto += `• ${campo.label}: ${valor}\n`;
                }
            });
            
            if (campos.some(c => c.type === 'file')) {
                texto += `\nFotos da avaria:`;
                let fotoIndex = 1;
                campos.forEach(campo => {
                    if (campo.type === 'file' && fotosAvaria[campo.name]) {
                        fotosAvaria[campo.name].indice = fotoIndex;
                        texto += `\n- ${campo.label}: FOTO${fotoIndex++}`;
                    }
                });
            }
            
            if (textoRelatorio) {
                textoRelatorio.textContent = texto;
            }
        } catch (error) {
            console.error('Erro ao atualizar preview:', error);
        }
    }
    
    // Função para mostrar alertas
    function mostrarAlerta(mensagem, tipo = 'info') {
        // Remover alertas existentes
        const alertasExistentes = document.querySelectorAll('.alert');
        alertasExistentes.forEach(alerta => alerta.remove());
        
        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show mt-3`;
        alerta.role = 'alert';
        alerta.innerHTML = `
            ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        const container = document.querySelector('.container');
        if (container) {
            container.prepend(alerta);
            
            setTimeout(() => {
                if (alerta.parentNode) {
                    alerta.remove();
                }
            }, 5000);
        }
    }
    
    // Função para copiar texto com fallback
    async function copiarParaAreaTransferencia(texto) {
        try {
            // Tentativa com Clipboard API moderna
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(texto);
                console.log('Texto copiado para a área de transferência (Clipboard API)');
                return true;
            } else {
                // Fallback para método antigo
                const textarea = document.createElement('textarea');
                textarea.value = texto;
                textarea.style.position = 'fixed';
                textarea.style.left = '-9999px';
                textarea.style.top = '0';
                textarea.setAttribute('readonly', '');
                document.body.appendChild(textarea);
                
                textarea.select();
                textarea.setSelectionRange(0, 99999);
                
                const successful = document.execCommand('copy');
                document.body.removeChild(textarea);
                
                if (successful) {
                    console.log('Texto copiado para a área de transferência (fallback)');
                    return true;
                } else {
                    console.error('Falha ao copiar texto com ambos os métodos');
                    return false;
                }
            }
        } catch (error) {
            console.error('Erro ao copiar texto:', error);
            return false;
        }
    }
    
    // Função para enviar relatório - COM SISTEMA DE CÓPIA CORRIGIDO
    async function enviarRelatorio() {
        if (!btnEnviar) return;
        
        const btnEnviarOriginal = btnEnviar.innerHTML;
        btnEnviar.disabled = true;
        btnEnviar.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Enviando...';

        try {
            const tipoSelect = document.getElementById('tipoRelatorio');
            if (!tipoSelect) return;
            
            const tipoId = tipoSelect.value;
            const tipoSelecionado = tiposRelatorio.find(t => t.id == tipoId);
            let textoRelatorioContent = textoRelatorio ? textoRelatorio.textContent : '';
            
            if (!tipoSelecionado) {
                mostrarAlerta('Selecione um tipo de relatório válido', 'warning');
                return;
            }

            // Validação dos campos obrigatórios
            const campos = typeof tipoSelecionado.campos === 'string' 
                ? JSON.parse(tipoSelecionado.campos) 
                : tipoSelecionado.campos;
            
            const camposInvalidos = campos.filter(campo => {
                if (campo.required && campo.type !== 'file') {
                    const elemento = document.getElementById(campo.name);
                    return !elemento?.value;
                }
                return false;
            });
            
            if (camposInvalidos.length > 0) {
                mostrarAlerta(`Preencha os campos obrigatórios: ${camposInvalidos.map(c => c.label).join(', ')}`, 'warning');
                btnEnviar.disabled = false;
                btnEnviar.innerHTML = '<i class="bi bi-whatsapp"></i> Enviar por WhatsApp';
                return;
            }

            // Processar fotos para base64
            const fotosBase64 = [];
            for (const campoNome in fotosAvaria) {
                if (fotosAvaria[campoNome].file) {
                    const reader = new FileReader();
                    const base64 = await new Promise((resolve) => {
                        reader.onload = function(e) {
                            resolve(e.target.result);
                        };
                        reader.readAsDataURL(fotosAvaria[campoNome].file);
                    });
                    fotosBase64.push({
                        base64: base64,
                        campoNome: campoNome,
                        fileName: fotosAvaria[campoNome].file.name
                    });
                }
            }

            const response = await fetch('/api/relatorios', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    tipo_id: parseInt(tipoId),
                    dados: textoRelatorioContent,
                    destinatario_whatsapp: tipoSelecionado.destinatario_whatsapp || '',
                    fotos: fotosBase64
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // ✅ Substituir FOTO1, FOTO2, etc. pelas URLs reais
                let textoComUrls = textoRelatorioContent;
                
                if (data.fotosUrls && data.fotosUrls.length > 0) {
                    data.fotosUrls.forEach((urlInfo, index) => {
                        const placeholder = `FOTO${index + 1}`;
                        textoComUrls = textoComUrls.replace(placeholder, urlInfo.url);
                    });
                }

                // ✅ USAR NOVO SISTEMA DE CÓPIA COM FALLBACK
                const copiadoComSucesso = await copiarParaAreaTransferencia(textoComUrls);
                
                if (copiadoComSucesso) {
                    mostrarAlerta('Relatório enviado com sucesso e copiado para área de transferência!', 'success');
                } else {
                    mostrarAlerta('Relatório enviado! (Não foi possível copiar automaticamente)', 'warning');
                }

                // Enviar para WhatsApp com URLs reais
                const textoCodificado = encodeURIComponent(textoComUrls);
                let destino = tipoSelecionado.destinatario_whatsapp;
                if (destino && destino.startsWith('http')) {
                    window.open(`${destino}`, '_blank');
                } else if (destino) {
                    window.open(`https://wa.me/${destino}?text=${textoCodificado}`, '_blank');
                }

                // Limpa formulário
                if (tipoSelect) tipoSelect.value = '';
                if (formContainer) formContainer.innerHTML = '';
                if (preview) preview.classList.add('d-none');
                btnEnviar.classList.add('d-none');
                fotosAvaria = {};
                
            } else {
                mostrarAlerta(`Erro ao enviar: ${data.message}`, 'danger');
            }
        } catch (error) {
            console.error('Erro ao enviar relatório:', error);
            mostrarAlerta(`Erro ao enviar: ${error.message}`, 'danger');
        } finally {
            btnEnviar.disabled = false;
            btnEnviar.innerHTML = '<i class="bi bi-whatsapp"></i> Enviar por WhatsApp';
        }
    }
    
    // Iniciar a aplicação
    init();
});

// Função global para remover foto
function removerFoto(nomeCampo) {
    const inputFile = document.querySelector(`input[name="${nomeCampo}"]`);
    if (inputFile) {
        inputFile.value = '';
        if (inputFile.nextElementSibling) {
            inputFile.nextElementSibling.innerHTML = '';
        }
    }
    // Dispara evento para atualizar preview
    const event = new Event('change', { bubbles: true });
    const tipoRelatorio = document.getElementById('tipoRelatorio');
    if (tipoRelatorio) {
        tipoRelatorio.dispatchEvent(event);
    }
}