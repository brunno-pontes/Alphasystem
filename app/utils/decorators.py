from functools import wraps
from flask import session, redirect, url_for, flash
from flask_login import current_user

def license_required(f):
    """
    Decorator para verificar licença antes de acessar rotas
    Permite acesso irrestrito a administradores
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Usar apenas current_user do Flask-Login, que é mais confiável
        if current_user.is_authenticated:
            user = current_user
            # Verificar se é admin - usando getattr para mais segurança
            if getattr(user, 'is_admin', False):
                return f(*args, **kwargs)

            # Para outros usuários, verificar a licença associada à sua conta
            user_license_key = getattr(user, 'license_key', None)
            if user_license_key:
                from app.models import License
                # Buscar a licença específica do usuário
                user_license = License.query.filter_by(license_key=user_license_key).first()
                if user_license and user_license.is_valid():
                    return f(*args, **kwargs)
                else:
                    flash('Licença inválida ou expirada. Por favor, entre em contato com o administrador.', 'error')
                    return redirect(url_for('auth.login'))
            else:
                # Usuário não tem licença associada
                flash('Usuário não tem licença associada. Contate o administrador.', 'error')
                return redirect(url_for('auth.login'))
        else:
            # Verificar licença do sistema para usuários não logados
            from app.utils.license_manager import check_license
            if not check_license():
                flash('Licença do sistema inválida ou expirada. Por favor, entre em contato com o suporte.', 'error')
                return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function