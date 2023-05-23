import numpy as np
import pandas as pd
import math
from scipy.integrate import odeint

def sir(X, t, beta, gammaI, N):
    S1, S2, I1, I2, R1, R2 = X
    dXdt = [-beta[0,0]*I1*S1/N - beta[1,0]*I2*S1/N, #dS1/dt
            -beta[1,1]*I2*S2/N - beta[0,1]*I1*S2/N, #dS2/dt
            beta[0,0]*I1*S1/N + beta[1,0]*I2*S1/N - gammaI*I1, #dI1/dt
            beta[1,1]*I2*S2/N + beta[0,1]*I1*S2/N - gammaI*I2, #dI2/dt
            gammaI*I1, #dR1/dt
            gammaI*I2]  #dR2/dt
    return dXdt

def sir_different_population_size(X, t, beta, gammaI, N1, N2):
    S1, S2, I1, I2, R1, R2 = X
    if (N1>0)&(N2>0):
        dXdt = [-beta[0,0]*I1*S1/N1 - beta[1,0]*I2*S1/N1, #dS1/dt
                -beta[1,1]*I2*S2/N2 - beta[0,1]*I1*S2/N2, #dS2/dt
                beta[0,0]*I1*S1/N1 + beta[1,0]*I2*S1/N1 - gammaI*I1, #dI1/dt
                beta[1,1]*I2*S2/N2 + beta[0,1]*I1*S2/N2 - gammaI*I2, #dI2/dt
                gammaI*I1, #dR1/dt
                gammaI*I2]  #dR2/dt
    elif N1==0:
        dXdt = [0, #dS1/dt
                -beta[1,1]*I2*S2/N2 - beta[0,1]*I1*S2/N2, #dS2/dt
                0, #dI1/dt
                beta[1,1]*I2*S2/N2 + beta[0,1]*I1*S2/N2 - gammaI*I2, #dI2/dt
                0, #dR1/dt
                gammaI*I2]  #dR2/dt
    elif N2==0:
        dXdt = [-beta[0,0]*I1*S1/N1 - beta[1,0]*I2*S1/N1, #dS1/dt
                0, #dS2/dt
                beta[0,0]*I1*S1/N1 + beta[1,0]*I2*S1/N1 - gammaI*I1, #dI1/dt
                0 - gammaI*I2, #dI2/dt
                gammaI*I1, #dR1/dt
                0]  #dR2/dt
    return dXdt

def get_intercept(dxdt, t, slope = 'decreasing'):
    # slope = 'decreasing' indicates that the function has a negative slope at the intercept
    
    dxdt_idx0 = np.where(np.diff(np.sign(dxdt)))[0]

    i_s = []
    for i in range(len(dxdt_idx0)):
        idx =dxdt_idx0[i]
        if np.isnan(dxdt[idx]):
            i_s.append(i)
        if slope == 'decreasing':
            if (dxdt[idx-1]<0)&(dxdt[idx+1]>0):
                i_s.append(i)
        elif slope == 'increasing':
            if (dxdt[idx-1]>0)&(dxdt[idx+1]<0):
                i_s.append(i)
    dxdt_idx0 = np.delete(dxdt_idx0, i_s)
    
    if len(dxdt_idx0)>0:
        dxdt_turnaround_time = t[dxdt_idx0[0]]
    else:
        dxdt_turnaround_time = np.nan
        
    return dxdt_turnaround_time

def run_simple_sim(epsilon, Na = 5000, Nb = 5000, R0a = 1.5, R0b = 1.5, gammaI = 1/5.5, Ia_0=1, Ib_0=0):
    # gammaI is in units of inverse days
    # epsilon is the fraction of infections occuring across populations
    beta = gammaI*np.array([[R0a*(1-epsilon), R0a*epsilon], [R0b*epsilon, R0b*(1-epsilon)]])

    # Define initial conditions
    Ra_0 = 0
    Rb_0 = 0

    Sa_0 = Na-Ia_0
    Sb_0 = Nb-Ib_0

    X0 = [Sa_0, Sb_0, Ia_0, Ib_0, Ra_0, Rb_0]

    # Run ODE solver
    t = np.linspace(0,200,2000)
    sol = odeint(sir_different_population_size, X0, t, args = (beta, gammaI, Na, Nb))

    # read out results
    Sa = sol[:,0]
    Sb = sol[:,1]
    Ia = sol[:,2]
    Ib = sol[:,3]
    Ra = sol[:,4]
    Rb = sol[:,5]

    dIadt = np.diff(Ia)/((t[1]-t[0])/2)
    dIbdt = np.diff(Ib)/((t[1]-t[0])/2)
    dIabdt = np.diff(Ia+Ib)/((t[1]-t[0])/2)
    t_d = t[:-1]+(t[1]-t[0])/2 # time for dIa/dt and dIb/dt
    
    dIadt_turnaround_time = get_intercept(dIadt, t_d, slope = 'decreasing')
    dIbdt_turnaround_time = get_intercept(dIbdt, t_d, slope = 'decreasing')
    dIabdt_turnaround_time = get_intercept(dIabdt, t_d, slope = 'decreasing')

    return t, Sa, Sb, Ia, Ib, Ra, Rb, dIadt, dIbdt, dIabdt, t_d, dIadt_turnaround_time, dIbdt_turnaround_time, dIabdt_turnaround_time

def sample_wastewater(t, Ia, Ib, Na, Nb, fa, fb, n, v):
    W = (n/v)*(Ia*fa+Ib*fb)/(Na*fa+Nb*fb)
    dWdt = np.diff(W)/((t[1]-t[0])/2)
    t_W = t[:-1]+(t[1]-t[0])/2 # time for dWdt

    dWdt_turnaround_time = get_intercept(dWdt, t_W, slope = 'decreasing')
        
    return W, dWdt, t_W, dWdt_turnaround_time