import os
from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def init_admin_user():
    """Inicializa um usuário administrador padrão"""
    app = create_app()

    with app.app_context():
        # Criar tabelas se não existirem
        db.create_all()

        # Verificar se já existe um usuário admin
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Verificar se já existe outro usuário com o mesmo email
            existing_user_with_email = User.query.filter_by(email='admin@local').first()
            if existing_user_with_email:
                # Atualizar o usuário existente com nome 'admin' ou remover o email conflitante
                existing_user_with_email.email = f'old_email_{existing_user_with_email.id}@local'

            admin = User(
                username='admin',
                email='admin@local',
                password=generate_password_hash('root@10!'),
                is_admin=True,
                role='admin',  # Definir o role como admin também
                license_key=None  # Admin não precisa de licença específica
            )
            db.session.add(admin)
            message = "Usuário administrador criado com sucesso!"
        else:
            # Atualizar a senha e o role do usuário admin existente
            admin.password = generate_password_hash('root@10!')
            admin.is_admin = True  # Garantir que seja admin
            admin.role = 'admin'  # Definir o role como admin também
            message = "Usuário administrador já existe, senha e permissões atualizadas."

        db.session.commit()

        print(message)
        print("Usuário: admin")
        print("Senha: root@10!")

if __name__ == "__main__":
    init_admin_user()