// Funções JavaScript para o Alphasystem

document.addEventListener('DOMContentLoaded', function() {
    // Adicionar confirmação para ações de exclusão
    const deleteButtons = document.querySelectorAll('.btn-danger[onclick*="confirm"]');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const confirmed = confirm('Tem certeza que deseja excluir este item? Esta ação não pode ser desfeita.');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });
    
    // Atualizar a exibição da licença na página (se disponível)
    updateLicenseDisplay();
});

function updateLicenseDisplay() {
    // Esta função pode ser usada para atualizar informações da licença na interface
    // Por exemplo, mostrando quanto tempo falta para a próxima validação
    console.log('Sistema de licença ativo');
}