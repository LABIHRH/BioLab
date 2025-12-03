import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp
from scipy.stats import linregress

# --- 1. CÁLCULO DE FASES (Optimizado) ---
def detectar_fase_exponencial_optimizada(tiempo, biomasa):
    """Detecta la fase exponencial buscando la ventana con mejor R²."""
    if len(tiempo) < 4:
        return {'detectada': False, 'mu_max': 0, 'r2': 0, 'inicio': 0, 'fin': 0}

    log_biomasa = np.log(biomasa + 1e-10) # Evitar log(0)
    mejor_r2 = 0
    resultado = {
        'detectada': False, 'inicio': tiempo[0], 'fin': tiempo[-1],
        'duracion': 0, 'velocidad_crecimiento': 0, 'r_cuadrado': 0
    }

    n_puntos = len(tiempo)
    min_window = 3
    max_window = max(4, int(n_puntos * 0.6)) 

    for ventana in range(min_window, max_window + 1):
        for i in range(n_puntos - ventana + 1):
            t_subset = tiempo[i : i + ventana]
            ln_x_subset = log_biomasa[i : i + ventana]
            slope, intercept, r_value, _, _ = linregress(t_subset, ln_x_subset)
            r_sq = r_value ** 2

            if r_sq > mejor_r2 and r_sq > 0.90 and slope > 0:
                mejor_r2 = r_sq
                resultado.update({
                    'detectada': True,
                    'inicio': t_subset[0],
                    'fin': t_subset[-1],
                    'duracion': t_subset[-1] - t_subset[0],
                    'velocidad_crecimiento': slope,
                    'r_cuadrado': r_sq
                })
    return resultado

# --- 2. SIMULACIÓN (Monod + Luedeking-Piret) ---
def modelo_cinetico_monod_luedeking(t, y, params, productos_info):
    X = y[0]
    S = max(0, y[1])
    
    mu_max, Ks, Yxs, ms = params['mu_max'], params['Ks'], params['Yxs'], params['ms']

    mu = (mu_max * S) / (Ks + S) if S > 1e-6 else 0
    dX_dt = mu * X
    
    qs = (mu / Yxs) + ms
    dS_dt = -qs * X
    if S <= 0 and dS_dt < 0: dS_dt = 0

    derivadas = [dX_dt, dS_dt]
    
    for prod_key in productos_info.keys():
        alpha = productos_info[prod_key]['alpha']
        beta = productos_info[prod_key]['beta']
        dP_dt = (alpha * dX_dt) + (beta * X)
        derivadas.append(dP_dt)

    return derivadas

def simular_bioproceso(t_total, y0, params, productos_info):
    t_eval = np.linspace(0, t_total, 1000)
    sol = solve_ivp(
        modelo_cinetico_monod_luedeking, (0, t_total), y0,
        args=(params, productos_info), t_eval=t_eval, method='LSODA', min_step=1e-3
    )
    return sol

# --- 3. TRANSFERENCIA DE MASA (KLa Dinámico) ---
def calcular_kla_dinamico(tiempo, do_valores, do_saturacion=100.0):
    """Calcula KLa usando ln(C* - CL) = -KLa * t + C"""
    try:
        mask = (do_valores < do_saturacion) & (do_valores > 0)
        t_valid = tiempo[mask]
        do_valid = do_valores[mask]
        
        if len(t_valid) < 3:
            return {'exito': False, 'error': "Pocos puntos válidos (< 100% DO)."}

        # Linealización
        y_log = np.log(do_saturacion - do_valid)
        slope, intercept, r_value, _, _ = linregress(t_valid, y_log)
        
        return {
            'exito': True, 'kla': -slope, 'r2': r_value**2, 'pendiente': slope,
            'datos_t': t_valid, 'datos_y_log': y_log,
            'datos_y_pred': slope * t_valid + intercept
        }
    except Exception as e:
        return {'exito': False, 'error': str(e)}