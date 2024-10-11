from gekko import GEKKO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# load data and parse into columns
data = pd.read_csv("teste.csv",sep=" ")
nomes = ["X", "Y", "th", "v", "w", "ideal_X", "ideal_Y", "ideal_th", "Tempo"]
data.columns = nomes


t = data['Tempo']
u = data[['v','w']]
y = data[['X','Y','th']]

# generate time-series model
m = GEKKO(remote=False)

# system identification
na = 3 # output coefficients
nb = 2 # input coefficients
yp,p,K = m.sysid(t,u,y,na,nb)

print(p)

# plt.figure(figsize=(8,5))
# plt.subplot(2,1,1)
# plt.plot(t,u)
# plt.legend([r'$V$',r'$W$'])
# plt.ylabel('Inputs')
# plt.subplot(2,1,2)
# plt.plot(t,y)
# plt.plot(t,yp)
# plt.legend([r'$X_{m}$',r'$Y_{m}$',r'$th_{m}$',r'$X_{p}$',r'$Y_{p}$',r'$th_{p}$'])
# plt.ylabel('Outputs')
# plt.xlabel('Time')
# plt.tight_layout()
# plt.savefig('sysid.png',dpi=300)
# plt.show()

na = 3
nb = 3
nc = 1

ny = 3
nu = 2

y,u = m.arx(p)

tf = 12
u0 = np.zeros(tf+1)
u1 = u0.copy()

u0[5:] = 2.0 #v
u1[2:] = 0.0 #w

u[0].value = u0
u[1].value = u1

m.time = np.linspace(0,tf,tf+1)
m.options.imode = 4
m.options.nodes = 2
m.solve()

plt.figure(1)
plt.subplot(2,1,1)
plt.plot(m.time,u[0].value,'r-',label=r'$v$')
plt.plot(m.time,u[1].value,'b--',label=r'$w$')
plt.ylabel('MV')
plt.legend(loc='best')
plt.subplot(2,1,2)
plt.plot(m.time,y[0].value,'r:',label=r'$y_0$')
plt.plot(m.time,y[1].value,'b.-',label=r'$y_1$')
plt.plot(m.time,y[2].value,'g.-',label=r'$y_2$')
plt.ylabel('CV')
plt.xlabel('Time (sec)')
plt.legend(loc='best')
plt.tight_layout()
plt.show()