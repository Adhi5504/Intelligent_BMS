"""Preliminary thermal sizing of a passive PCM milk-chilling can (20 L). ALL inputs are design assumptions;
nothing here is measured. Lumped model: milk (one node) coupled to PCM at its melting point through UA_pcm,
ambient leak through PUF shell. Run: python3 thermal_calc.py"""
import math, json
# --- assumptions ---
V=20.0; rho=1.03; cp=3.93e3          # L, kg/L, J/kgK (whole milk ~3.9 kJ/kgK)
T0=35.0; Tt=4.0; Tamb=38.0           # fresh milk, target, worst-case ambient (C)
Tpcm=0.0                             # ice-type PCM (latent 334 kJ/kg; 300 usable after packaging/contact losses)
L_ice=300e3; L_par=180e3             # J/kg usable
k=0.025; th=0.04                     # PUF W/mK, 40 mm
A=0.62; bridge=1.5                   # mean area m2, lid/gasket thermal bridge factor
UA_leak=k*A/th*bridge                # W/K
UA_pcm=34.0                          # milk<->PCM coupling W/K (assumption: packs on wall + base, stirring by transport)
m=V*rho; C=m*cp
tau=C/UA_pcm
t_pull=tau*math.log((T0-Tpcm)/(Tt-Tpcm))
Q_pull=C*(T0-Tt)
m_ss=2.2; Q_ss=m_ss*500*(T0-Tt)      # inner SS 304 can sensible heat
hold=6*3600
Tm_ss=Tpcm+UA_leak*(Tamb-Tpcm)/UA_pcm  # quasi-steady milk temp rise above PCM
Q_leak=UA_leak*(Tamb-(Tt+Tpcm)/2)*hold
Q_tot=Q_pull+Q_ss+Q_leak
for name,L in (("ice-type",L_ice),("paraffin",L_par)):
    mp=Q_tot*1.15/L
    print(f"PCM {name}: {mp:.1f} kg (incl 15% margin)")
m_ice=Q_tot*1.15/L_ice
print(f"milk {m:.1f} kg, C={C/1e3:.1f} kJ/K, tau={tau/60:.0f} min, pull-down to {Tt}C: {t_pull/3600:.2f} h")
print(f"Q_pull={Q_pull/1e6:.2f} MJ, Q_ss={Q_ss/1e6:.3f}, Q_leak(6h)={Q_leak/1e6:.2f} MJ, total={Q_tot/1e6:.2f} MJ")
print(f"UA_leak={UA_leak:.2f} W/K, steady milk T above PCM={Tm_ss:.2f} C, leak share={Q_leak/Q_tot*100:.0f}%")
# time-series with PCM consumption
dt=30; t=0; Tm=T0; Q_used=0; mp=m_ice; cap=mp*L_ice; series=[]
while t<=9*3600:
    if t%1800==0: series.append((t/3600,round(Tm,2),round(100*max(0,1-Q_used/cap),1)))
    if Q_used<cap:
        q_pcm=UA_pcm*(Tm-Tpcm); q_leak=UA_leak*(Tamb-Tm)
        Tm+= (q_leak-q_pcm)*dt/C; Q_used+=q_pcm*dt-q_leak*dt*0  # leak enters milk, extracted by pcm
    else:
        Tm+= UA_leak*(Tamb-Tm)*dt/(C+mp*4180)
    t+=dt
print("t(h), milk T (C), PCM left (%)"); [print(s) for s in series[::2]]
json.dump([[s[0],s[1]] for s in series],open("pulldown.json","w"))
# mass / weight
w={"outer HDPE shell":3.0,"PUF 40 mm":1.4,"SS304 inner can (0.8 mm)":m_ss,"PCM packs":round(m_ice,1),"lid+gasket+latches":1.0}
tot=sum(w.values()); print(w, "empty weight %.1f kg, full %.1f kg"%(tot,tot+m))
# BOM (Rs, assumed, prototype / 1000-unit run)
bom=[("SS304 inner can (food grade)",2200,1700),("HDPE rotomoulded outer shell",1800,1100),("PUF insulation (inj.)",800,500),
     ("PCM packs, 10 kg ice-type",1100,800),("Lid, EPDM gasket, latches",900,550),("Assembly, labour, QC",1500,600)]
p=sum(b[1] for b in bom); q=sum(b[2] for b in bom); print("BOM proto",p,"mass",q)
cycles=3*300
print("capex/cycle Rs %.1f -> per litre %.2f"%(q/cycles,q/cycles/V))
E=(Q_tot*1.15/1e6)/ (3.6) /2.0   # kWh electric, COP 2 freezer (heat removed ~ latent+sensible)
print("recharge energy %.2f kWh -> Rs %.1f/cycle at Rs8 -> Rs %.2f/L"%(E,E*8,E*8/V))
