"""
Script para associar vendas existentes aos caixas correspondentes
"""
from app import create_app, db
from app.models import Sale, Cashier
from datetime import datetime

def associate_sales_with_cashiers():
    app = create_app()
    
    with app.app_context():
        # Obter todas as vendas sem caixa associado
        sales_without_cashier = Sale.query.filter(Sale.cashier_id.is_(None)).all()
        
        print(f"Encontradas {len(sales_without_cashier)} vendas sem caixa associado")
        
        for sale in sales_without_cashier:
            # Procurar por caixas abertos no momento da venda
            cashiers = Cashier.query.filter(
                Cashier.opening_date <= sale.sale_date
            ).filter(
                (Cashier.closing_date >= sale.sale_date) | (Cashier.closing_date.is_(None))
            ).all()
            
            # Preferir caixas do mesmo usuário
            user_cashiers = [c for c in cashiers if c.user_id == getattr(sale.product, 'user_id', None)]
            
            # Se não encontrar caixas do usuário, pegar qualquer caixa aberto
            if user_cashiers:
                selected_cashier = user_cashiers[0]
            elif cashiers:
                selected_cashier = cashiers[0]
            else:
                continue  # Nenhum caixa encontrado para essa venda
                
            # Associar a venda ao caixa
            sale.cashier_id = selected_cashier.id
            
            # Atualizar o total de vendas do caixa
            selected_cashier.total_sales += sale.total_price
            
            print(f"Venda {sale.id} associada ao caixa {selected_cashier.id}")
        
        # Confirmar todas as alterações
        db.session.commit()
        print("Todas as vendas foram associadas aos caixas correspondentes")

if __name__ == "__main__":
    associate_sales_with_cashiers()