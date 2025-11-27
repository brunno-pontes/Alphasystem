import requests
from datetime import datetime
from app.models import License
from app import db

class LicenseValidator:
    def __init__(self, server_url="http://seu_servidor_central.com"):
        self.server_url = server_url
    
    def validate_license(self, license_key):
        """
        Valida a licença conectando ao servidor central
        Retorna True se válida, False caso contrário
        """
        try:
            # Buscar a licença no banco de dados local
            license = License.query.filter_by(license_key=license_key).first()
            
            if not license:
                return False
            
            # Verificar se a licença já expirou
            if not license.is_valid():
                return False
            
            # Verificar se é hora de validar online (a cada 30 dias)
            if license.needs_validation():
                # Enviar requisição para o servidor central
                response = requests.post(f"{self.server_url}/validate_license", json={
                    'license_key': license_key,
                    'client_id': license.id
                }, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('valid'):
                        # Atualizar data da última validação
                        license.last_validation = datetime.utcnow()
                        db.session.commit()
                        return True
                    else:
                        return False
                else:
                    # Se o servidor não responder, permitir uso por até 3 dias
                    # após a última validação bem-sucedida
                    if (datetime.utcnow() - license.last_validation).days <= 3:
                        return True
                    return False
            else:
                return True  # Licença ainda não precisa de validação
        except requests.exceptions.RequestException:
            # Se houver erro de conexão, permitir uso por até 3 dias
            # após a última validação bem-sucedida
            if license and (datetime.utcnow() - license.last_validation).days <= 3:
                return True
            return False
        except Exception:
            return False

def check_license():
    """
    Função para verificar licença antes de cada requisição
    """
    # Pegar a licença do sistema (pode ser armazenada em arquivo de config ou variável de ambiente)
    from flask import current_app, request
    import os
    
    # Neste exemplo, vamos usar uma licença padrão armazenada em variável de ambiente
    license_key = os.environ.get('PRATELEIRA_LICENSE_KEY')
    
    # Se não houver licença configurada, negar acesso
    if not license_key:
        return False
    
    validator = LicenseValidator()
    return validator.validate_license(license_key)