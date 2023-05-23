import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style = 'ticks', font_scale = 1.2)
import mathematical_model_functions as fnc

# Sweep values of epsilon
epsilons = np.logspace(-2, -1, 21)

N = 5000
R0 = 1.5
gammaI = 1/5.5
Na = N
Nb = N
fa = 1
fbs = np.linspace(0, 1, 21)
n = 5*10**6.7 # gene copies/person/day
v = 20 # liters wastewater/day

parameter_sets = [{'Na':N, 'Nb':N, 'gammaI':gammaI, 'R0a':R0, 'R0b':R0},
                 {'Na':N, 'Nb':N, 'gammaI':1/3, 'R0a':R0, 'R0b':R0},
                 {'Na':N, 'Nb':N, 'gammaI':1/10, 'R0a':R0, 'R0b':R0},
                 {'Na':N, 'Nb':N, 'gammaI':gammaI, 'R0a':2, 'R0b':2},
                 {'Na':N, 'Nb':N, 'gammaI':gammaI, 'R0a':3, 'R0b':3},
                 {'Na':500, 'Nb':500, 'gammaI':gammaI, 'R0a':R0, 'R0b':R0},
                 {'Na':50000, 'Nb':50000, 'gammaI':gammaI, 'R0a':R0, 'R0b':R0},
                 {'Na':N, 'Nb':N, 'gammaI':gammaI, 'R0a':2, 'R0b':1.5}]

for parameter_set in parameter_sets:
    
    Na = parameter_set['Na']
    Nb = parameter_set['Nb']
    gammaI = parameter_set['gammaI']
    R0a = parameter_set['R0a']
    R0b = parameter_set['R0b']

    deltat_df = pd.DataFrame()

    for epsilon in epsilons:
        for fb in fbs:
            t, Sa, Sb, Ia, Ib, Ra, Rb, dIadt, dIbdt, dIabdt, t_d, dIadt_turnaround_time, dIbdt_turnaround_time, dIabdt_turnaround_time = fnc.run_simple_sim(epsilon, Na=Na, Nb=Nb, R0a=R0a, R0b=R0b, gammaI=gammaI)

            W, dWdt, t_W, dWdt_turnaround_time = fnc.sample_wastewater(t, Ia, Ib, Na, Nb, fa, fb, n, v)

            deltat = dIbdt_turnaround_time - dWdt_turnaround_time
            deltat=deltat*gammaI
            deltat_df = pd.concat([deltat_df, pd.DataFrame({'epsilon':[epsilon], 'fb':[fb], 'deltat':[deltat]})])

    pivoted = deltat_df.pivot('fb', 'epsilon', 'deltat')

    fig, ax = plt.subplots(1, 1, figsize = (6,4.5))
    if np.mean(pivoted.values)>0:
        im = ax.pcolormesh(pivoted.columns, pivoted.index, pivoted, vmin = 0, vmax = 4)
    else:
        im = ax.pcolormesh(pivoted.columns, pivoted.index, pivoted, vmin = -4, vmax = 0)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('Time between population B peak \nand wastewater peak, $\Delta t$ \n(units of generation time)')
    
    less_one_gen = np.where(np.abs(pivoted)<=1)
    less_one_gen_y = less_one_gen[0]
    less_one_gen_x = less_one_gen[1]

    ax.scatter(pivoted.columns[less_one_gen_x], pivoted.index[less_one_gen_y], marker = '.', color = 'lightblue')
        
    plt.yticks(rotation=0) 
    plt.ylabel('Fraction of population B sampled, $f_B$')
    plt.xlabel('Fraction of cross-population contacts, $\epsilon$')
    plt.xscale('log')
    plt.title('$N_A=$'+str(Na) + ', $N_B=$' + str(round(Nb)) + ', $\gamma_I=$' + str(round(gammaI,2)) + ', $R_0^A=$' + str(R0a) + ', $R_0^B=$' + str(R0b))
    plt.tight_layout()
    plt.savefig('../figures/figsi_mathematical_model_summary_Na' + str(round(Na)) + '_Nb' + str(round(Nb)) + '_gammaI' + str(round(gammaI,2)) + '_R0a' + str(R0a) + '_R0b' + str(R0b) + '.png', dpi = 300)
    plt.savefig('../figures/figsi_mathematical_model_summary_Na' + str(round(Na)) + '_Nb' + str(round(Nb)) + '_gammaI' + str(round(gammaI,2)) + '_R0a' + str(R0a) + '_R0b' + str(R0b) + '.pdf')