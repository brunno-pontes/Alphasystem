import os
import json
from datetime import datetime, timedelta
from app.models import License
from app import db
import requests
import threading
import time

class LicenseManager:
    """
    Classe para gerenciar licenças do sistema
    """
    
    def __init__(self, server_url="http://seu_servidor_central.com"):
        self.server_url = server_url
        self.license_file = os.environ.get('LICENSE_FILE', 'instance/license.json')
        
    def load_license_key(self):
        """
        Carrega a chave de licença do arquivo ou variável de ambiente
        """
        # Primeiro tenta do arquivo de configuração
        try:
            if os.path.exists(self.license_file):
                with open(self.license_file, 'r') as f:
                    data = json.load(f)
                    return data.get('license_key')
        except:
            pass
        
        # Depois tenta da variável de ambiente
        return os.environ.get('PRATELEIRA_LICENSE_KEY')
    
    def save_license_key(self, license_key):
        """
        Salva a chave de licença no arquivo
        """
        os.makedirs(os.path.dirname(self.license_file), exist_ok=True)
        with open(self.license_file, 'w') as f:
            json.dump({'license_key': license_key}, f)
    
    def validate_license_online(self, license_key):
        """
        Valida a licença online com o servidor central
        """
        try:
            response = requests.post(
                f"{self.server_url}/api/validate_license", 
                json={'license_key': license_key},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('valid', False), data.get('message', '')
            else:
                return False, f'Erro no servidor: {response.status_code}'
        except requests.exceptions.RequestException as e:
            return False, f'Erro de conexão: {str(e)}'
        except Exception as e:
            return False, f'Erro inesperado: {str(e)}'
    
    def check_license_status(self):
        """
        Verifica o status da licença local
        """
        license_key = self.load_license_key()
        
        if not license_key:
            return {'valid': False, 'message': 'Nenhuma licença encontrada'}
        
        # Buscar licença no banco de dados
        license = License.query.filter_by(license_key=license_key).first()
        
        if not license:
            return {'valid': False, 'message': 'Licença não registrada no sistema'}
        
        # Verificar se expirou
        if not license.is_valid():
            return {'valid': False, 'message': 'Licença expirada'}
        
        # Verificar se precisa validar online (a cada 30 dias)
        if license.needs_validation():
            valid, message = self.validate_license_online(license_key)
            if valid:
                # Atualizar data da última validação
                license.last_validation = datetime.utcnow()
                db.session.commit()
                return {'valid': True, 'message': 'Licença validada online com sucesso'}
            else:
                # Permitir uso por até 3 dias extras após falha na validação
                grace_period_days = 3
                if license.last_validation and \
                   (datetime.utcnow() - license.last_validation) < timedelta(days=grace_period_days):
                    return {'valid': True, 'message': f'Validação online falhou, mas usando período de carência. {message}'}
                else:
                    return {'valid': False, 'message': f'Falha na validação online: {message}'}
        else:
            return {'valid': True, 'message': 'Licença válida e atualizada'}
    
    def validate_license(self):
        """
        Método principal para validação de licença
        """
        result = self.check_license_status()
        return result['valid']
    
    def setup_background_validation(self):
        """
        Configura validação em background para manter a licença atualizada
        """
        def background_task():
            while True:
                time.sleep(24 * 3600)  # Verificar a cada 24 horas
                try:
                    self.check_license_status()
                except:
                    pass  # Ignorar erros na validação em background
        
        thread = threading.Thread(target=background_task, daemon=True)
        thread.start()

# Instância global do gerenciador de licenças
license_manager = LicenseManager()

def check_license():
    """
    Função para verificar licença antes de cada requisição
    Permite acesso a administradores mesmo com licença inválida
    Para usuários normais, verifica a licença associada à sua conta
    """
    from flask import session
    from app.models import User
    from flask_login import current_user

    # Verificar se há um usuário logado via Flask-Login
    if current_user.is_authenticated:
        user = current_user
    else:
        # Alternativa usando a sessão
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
        else:
            user = None

    if user:
        # Administradores têm acesso irrestrito
        if hasattr(user, 'is_admin') and user.is_admin:
            return True

        # Para usuários normais, verificar a licença associada à sua conta
        if hasattr(user, 'license_key') and user.license_key:
            from app.models import License
            # Buscar a licença específica do usuário
            user_license = License.query.filter_by(license_key=user.license_key).first()
            if user_license and user_license.is_valid():
                return True
            else:
                return False
        else:
            # Usuário não tem licença associada
            return False

    # Nenhum usuário logado
    return license_manager.validate_license()