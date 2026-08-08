# src/recommend.py
import joblib
import numpy as np

MODEL_PATH = "models/regression_model.joblib"

def load_model():
    return joblib.load(MODEL_PATH)

def irrigation_recommendation(soil_moisture, predicted_yield, thresholds=(25,40)):
    """
    Regras:
     - If soil_moisture < thresholds[0] -> irrigate alto
     - If between thresholds -> irrigate moderado
     - If > thresholds[1] -> evitar irrigação
    Retorna volume sugerido (mL) e justificativa.
    """
    if soil_moisture < thresholds[0]:
        vol = 300  # mL
        reason = "Umidade baixa -> irrigação alta recomendada"
    elif soil_moisture < thresholds[1]:
        vol = 120
        reason = "Umidade média -> irrigação moderada"
    else:
        vol = 0
        reason = "Umidade adequada -> não irrigar"
    # Modifica volume levemente baseado no yield previsto (se rendimento muito baixo, priorizar)
    if predicted_yield < 0.06:
        vol *= 1.2
        reason += " (ajuste: yield previsto baixo)"
    return vol, reason

def fertilizer_recommendation(soil_ph, predicted_yield):
    """
    Regras simplificadas:
     - ph < 5.8 -> recomendar calagem (reduzir acidez)
     - ph > 7.0 -> recomendar correção ácida (se necessário)
     - baseline de aplicação mínima se yield previsto baixo
    """
    rec = []
    amount = 0.0
    if soil_ph < 5.8:
        rec.append("Calagem recomendada para elevar pH")
        amount += 0.5
    elif soil_ph > 7.0:
        rec.append("Correção para reduzir pH (consultar especialista)")
        amount += 0.2
    else:
        rec.append("pH adequado")
    if predicted_yield < 0.06:
        rec.append("Aplicar fertilizante adicional leve (aumentar ~0.3 kg/ha)")
        amount += 0.3
    return amount, "; ".join(rec)

def recommend_from_point(soil_moisture, soil_ph, features=None):
    """
    Carrega modelo, faz previsão baseada nas features fornecidas (opcional),
    e retorna recomendações.
    features: dict com air_temp, humidity, irrigation_ml, fertilizer_kg (se não, assume 0)
    """
    if features is None:
        features = {"air_temp":25,"humidity":60,"irrigation_ml":0,"fertilizer_kg":0}
    model = load_model()
    X = np.array([[soil_moisture, soil_ph, features["air_temp"], features["humidity"], features["irrigation_ml"], features["fertilizer_kg"]]])
    pred_yield = model.predict(X)[0]
    vol, irr_reason = irrigation_recommendation(soil_moisture, pred_yield)
    fert_amount, fert_reason = fertilizer_recommendation(soil_ph, pred_yield)
    return {
        "predicted_yield": float(pred_yield),
        "irrigation_ml_suggested": float(vol),
        "irrigation_reason": irr_reason,
        "fertilizer_kg_suggested": float(fert_amount),
        "fertilizer_reason": fert_reason
    }

if __name__ == "__main__":
    print(recommend_from_point(22.0, 5.6))
