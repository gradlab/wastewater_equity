import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style = 'ticks', font_scale = 1.2)
import mathematical_model_functions as fnc

# Start outbreak in population A with 1 infected individual

epsilons = [0.01, 0.05, 0.1, 0.5]
N = 5000
R0 = 1.5
R0a = R0
R0b = R0
gammaI = 1/5.5
Na = N
Nb = N
fa = 1
fb = 0.1
n = 5*10**6.7 # gene copies/person/day
v = 20 # liters wastewater/day

fig, ax = plt.subplots(1, 4, figsize = (13,4), sharex = True, sharey = True)

i=0
for epsilon in epsilons:
    t, Sa, Sb, Ia, Ib, Ra, Rb, dIadt, dIbdt, dIabdt, t_d, dIadt_turnaround_time, dIbdt_turnaround_time, dIabdt_turnaround_time = fnc.run_simple_sim(epsilon, Na=Na, Nb=Nb, R0a=R0a, R0b=R0b, gammaI=gammaI)
    W, dWdt, t_W, dWdt_turnaround_time = fnc.sample_wastewater(t, Ia, Ib, Na, Nb, fa, fb, n, v)
    
    t = t*gammaI
    t_W = t_W*gammaI
    dIadt_turnaround_time = dIadt_turnaround_time*gammaI
    dIbdt_turnaround_time = dIbdt_turnaround_time*gammaI
    dIabdt_turnaround_time = dIabdt_turnaround_time*gammaI
    dWdt_turnaround_time = dWdt_turnaround_time*gammaI
    
    ax[i].plot(t, Ia, label = 'A', color = 'k')
    ax[i].plot(t, Ib, label = 'B', color = 'k', linestyle = '--')
    ax[i].plot(t, Ia+Ib, label = 'A+B', color = 'k', linestyle = ':')
               
    ax[i].plot([dIadt_turnaround_time, dIadt_turnaround_time], [0, 700], color = 'k')
    ax[i].plot([dIbdt_turnaround_time, dIbdt_turnaround_time], [0, 700], color = 'k', linestyle = '--')
    ax[i].plot([dIabdt_turnaround_time, dIabdt_turnaround_time], [0, 700], color = 'k', linestyle = ':')

    ax0_twin = ax[i].twinx()
    pw = ax0_twin.plot(t, W, label = 'Wastewater concentration', color = 'tab:blue')
    ax0_twin.plot([dWdt_turnaround_time, dWdt_turnaround_time], [0, 85000], color = pw[0].get_color())
    
    ax[i].set_ylim(0, 700)
    ax[i].ticklabel_format(style='sci', axis='y', scilimits=(0,0))  
    ax[i].set_title('$\epsilon=$'+str(epsilon))

    ax0_twin.set_ylim(0,85000)
    ax0_twin.ticklabel_format(style='sci', axis='y', scilimits=(0,0))  
    
    if i!=3:
        ax0_twin.set_yticklabels([])
    i+=1

ax[0].legend()
ax[0].set_xlim(np.min(t), np.max(t))
ax[0].set_ylabel('# infected individuals')    
ax0_twin.yaxis.label.set_color('tab:blue')
ax0_twin.tick_params(colors='tab:blue', which='both', axis = 'y')
ax0_twin.spines['left'].set_color('tab:blue')
ax0_twin.set_ylabel('Wastewater concentration \n(# gene copies/L)')

fig.suptitle('Outbreak starts in population A\n$N_A$=$N_B$='+str(N)+', $R_0^A$=$R_0^B$='+str(R0)+', $\gamma_I$='+str(round(gammaI,2))+', $f_A=$' + str(fa)+', $f_B=$' + str(fb))
fig.supxlabel('Time (generation time)')
plt.tight_layout()
plt.savefig('../figures/fig5b_mathematical_model.png')
plt.savefig('../figures/fig5b_mathematical_model.pdf')