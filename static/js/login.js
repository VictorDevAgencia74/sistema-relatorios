document.addEventListener('DOMContentLoaded', function() {
    const btnLogin = document.getElementById('btnLogin');
    const codigoAcesso = document.getElementById('codigoAcesso');
    const setorAcesso = document.getElementById('setorAcesso');
    
    btnLogin.addEventListener('click', fazerLogin);
    
    codigoAcesso.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            fazerLogin();
        }
    });
    
    function fazerLogin() {
        const setor = setorAcesso.value;
        const codigo = codigoAcesso.value.trim();
        
        if (!setor || !codigo) {
            alert('Por favor, selecione o setor e informe o código de acesso.');
            return;
        }
        
        fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                setor: setor,
                codigo: codigo
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Redirecionar para a página correta
                if (setor === 'porteiro') {
                    window.location.href = '/';
                } else if (setor === 'admin') {
                    window.location.href = '/admin';
                } else if (setor === 'dp') {
                    window.location.href = '/dp';
                } else if (setor === 'trafego') {
                    window.location.href = '/trafego';
                }
            } else {
                alert(data.message || 'Erro ao fazer login');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Erro ao fazer login. Tente novamente.');
        });
    }
});