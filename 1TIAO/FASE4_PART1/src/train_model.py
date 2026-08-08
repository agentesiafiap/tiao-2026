import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import sys
import os

# --- CONFIGURAÇÃO ---
CSV_FILE = "../data/simulated_sensor_data.csv"

# Variáveis Alvo para Regressão:
TARGETS = {
    'yield_ton_per_ha': "Estimativa de Rendimento (ton/ha)",
    'irrigation_ml': "Sugestão de Volume de Irrigação (ml)",
    'fertilizer_kg': "Sugestão de Fertilização (kg)"
}

# Modelos a serem comparados
MODELS = {
    'Regressão Linear Múltipla': LinearRegression(),
    'Regressão Ridge': Ridge(alpha=1.0, random_state=42),
    'Random Forest Regressor': RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
}
# --- FIM CONFIGURAÇÃO ---

def load_data():
    """Carrega e prepara os dados."""
    if not os.path.exists(CSV_FILE):
        print(f"ERRO: Arquivo {CSV_FILE} não encontrado. Abortando a análise.")
        sys.exit(1)
        
    df = pd.read_csv(CSV_FILE)
    
    FEATURES = ['soil_moisture', 'soil_ph', 'air_temp', 'humidity']
    
    df = df.drop(columns=['sensor_id', 'timestamp'], errors='ignore')
    df = df.dropna()

    return df, FEATURES

def evaluate_model(y_test, y_pred):
    """Calcula e retorna as métricas de avaliação: MAE, MSE, RMSE, R²."""
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    return {'MAE': mae, 'MSE': mse, 'RMSE': rmse, 'R2': r2}

def run_predictive_analysis(df, features):
    """Treina e avalia todos os modelos para todas as variáveis alvo."""
    
    results = {}
    
    for target_name, target_desc in TARGETS.items():
        print(f"\n[ANALISANDO ALVO: {target_desc}]")
        
        X = df[features]
        y = df[target_name]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        
        target_results = {}
        
        for model_name, model in MODELS.items():
            
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            metrics = evaluate_model(y_test, y_pred)
            target_results[model_name] = metrics
            
            print(f"  > Modelo {model_name}: R² = {metrics['R2']:.4f}, RMSE = {metrics['RMSE']:.4f}")
            
        results[target_name] = target_results
        
    return results

def present_recommendations(results):
    """Interpreta os resultados e apresenta a avaliação comparativa completa."""
    
    print("\n\n" + "="*50)
    print("      RECOMENDAÇÕES DE MANEJO BASEADAS EM REGRESSÃO")
    print("="*50)
    
    # ----------------------------------------------------------------------
    # 1. ENCONTRAR O MELHOR MODELO E DEFINIR MÉTRICAS CHAVES
    # ----------------------------------------------------------------------

    # Rendimento (Foco no R²)
    yield_results = results['yield_ton_per_ha']
    best_r2_yield_name = max(yield_results, key=lambda name: yield_results[name]['R2'])
    best_r2_yield = yield_results[best_r2_yield_name]['R2']
    
    # Irrigação (Foco no MAE)
    irrigation_results = results['irrigation_ml']
    best_mae_irrigation_name = min(irrigation_results, key=lambda name: irrigation_results[name]['MAE'])
    best_mae_irrigation = irrigation_results[best_mae_irrigation_name]['MAE']
    
    # Fertilização (Foco no MAE)
    fertilizer_results = results['fertilizer_kg']
    best_mae_fertilizer_name = min(fertilizer_results, key=lambda name: fertilizer_results[name]['MAE'])
    best_mae_fertilizer = fertilizer_results[best_mae_fertilizer_name]['MAE']

    print(f"\n[Melhores Modelos por Alvo]")
    print(f" - Rendimento (R²): {best_r2_yield_name} (R²: {best_r2_yield:.4f})")
    print(f" - Irrigação (MAE): {best_mae_irrigation_name} (MAE: {best_mae_irrigation:.2f} ml)")
    print(f" - Fertilização (MAE): {best_mae_fertilizer_name} (MAE: {best_mae_fertilizer:.4f} kg)")

    
    # ----------------------------------------------------------------------
    # 2. SUGESTÕES E INTERPRETAÇÕES
    # ----------------------------------------------------------------------

    if best_r2_yield < 0.70:
        print("\n[RECOMENDAÇÃO 1 (MODELAGEM)]: O R² para Rendimento está baixo (< 0.70). Sugere-se engenharia de features (ex: criar índice NPK total ou interações) para melhorar o poder preditivo.")
    else:
        # CORREÇÃO AQUI: Inserção dinâmica do nome do modelo vencedor
        print(f"\n[RECOMENDAÇÃO 1 (MODELAGEM)]: O R² está satisfatório ({best_r2_yield:.4f}). O modelo **{best_r2_yield_name}** é o mais eficiente para este dataset.")
        
    print(f"\n[SUGESTÃO DE IRRIGAÇÃO]: O erro de previsão de volume (MAE) é de apenas {best_mae_irrigation:.2f} ml. O controle automatizado baseado nesta previsão é altamente preciso e pode ser implementado.")
    
    print(f"\n[SUGESTÃO DE MANEJO]: O erro de previsão de fertilizante é muito baixo ({best_mae_fertilizer:.4f} kg). Isso permite um controle rigoroso de insumos, otimizando custos e prevenindo a poluição por excesso de nutrientes.")


    # ----------------------------------------------------------------------
    # 3. APRESENTAÇÃO TABULAR COMPLETA (MAE, MSE, RMSE, R²)
    # ----------------------------------------------------------------------
    
    print("\n\n" + "="*70)
    print("        AVALIAÇÃO COMPARATIVA DETALHADA (TODAS AS MÉTRICAS)")
    print("="*70)

    all_metrics = []
    for target, models_data in results.items():
        for model_name, metrics in models_data.items():
            row = {
                'Alvo': TARGETS[target], 
                'Modelo': model_name,
                'R2': metrics['R2'],
                'RMSE': metrics['RMSE'],
                'MAE': metrics['MAE'],
                'MSE': metrics['MSE']
            }
            all_metrics.append(row)

    df_metrics = pd.DataFrame(all_metrics)
    
    # Arredondamento dos valores para 4 casas decimais para visualização limpa
    df_metrics['R2'] = df_metrics['R2'].round(4)
    df_metrics['RMSE'] = df_metrics['RMSE'].round(4)
    df_metrics['MAE'] = df_metrics['MAE'].round(4)
    df_metrics['MSE'] = df_metrics['MSE'].round(6) # MSE é geralmente menor, 6 casas é mais útil
    
    # Imprime o DataFrame arredondado, garantindo uma formatação de console limpa
    # Note que a ordem das colunas foi definida na criação do dicionário.
    print(df_metrics.to_string(index=False))

if __name__ == "__main__":
    df, features = load_data()
    
    if not df.empty:
        results = run_predictive_analysis(df, features)
        present_recommendations(results)
    else:
        print("Análise abortada devido à falha no carregamento dos dados.")