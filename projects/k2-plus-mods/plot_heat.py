import csv, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
def load(p):
    rows=[r for r in csv.reader(open(p)) if r and not r[0].startswith("#")]
    h=rows[0]; return [dict(zip(h,r)) for r in rows[1:]]
a=load("2026-11-14-heater-alone.csv"); b=load("2026-11-15-vents-closed.csv")
def ph(d,p,k): x=[(float(r["t_s"])/60,float(r[k])) for r in d if r["phase"]==p]; return [i for i,_ in x],[j for _,j in x]
fig,ax=plt.subplots(1,3,figsize=(16,4.8))
O,N="#9aa0a6","#1a73e8"
for i,(p,k,t) in enumerate([("chamber","chamber_C","Chamber heater alone, target 55 °C\n(chamber air)"),("bed","bed_C","Bed alone, target 100 °C\n(bed)")]):
    x,y=ph(a,p,k); ax[i].plot(x,y,color=O,lw=2,label="14 Nov, a rear vent open")
    x,y=ph(b,p,k); ax[i].plot(x,y,color=N,lw=2,label="15 Nov, both vents closed")
    ax[i].set_title(t); ax[i].set_xlabel("minutes"); ax[i].set_ylabel("°C"); ax[i].grid(alpha=.3); ax[i].legend(loc="lower right")
ax[1].axhline(100,color="k",ls=":",lw=1)
# ABS + cool
xa,ba=ph(b,"abs","bed_C"); _,ca=ph(b,"abs","chamber_C"); _,pa=ph(b,"abs","ch_pwr"); _,fa=ph(b,"abs","exhaust_fan")
end=xa[-1]; xc,bc=ph(b,"cool","bed_C"); _,cc=ph(b,"cool","chamber_C"); xc=[end+v for v in xc]
A=ax[2]; A.plot(xa+xc,ba+bc,color="#d93025",lw=2,label="bed"); A.plot(xa+xc,ca+cc,color=N,lw=2,label="chamber air")
A.axvline(end,color="k",lw=1); A.text(end+1,95,"heaters off",fontsize=9)
A.axhline(55,color=N,ls=":",lw=1); A.axhline(100,color="#d93025",ls=":",lw=1)
on=[x for x,p in zip(xa,pa) if p>0][0]; A.axvspan(0,on,color="orange",alpha=.15,label="chamber heater held at 0%")
fon=[x for x,f in zip(xa,fa) if f>0][0]; A.annotate("rear exhaust fan 100%\n(chamber > 35 °C)",(fon,38),(1,72),arrowprops=dict(arrowstyle="->"),fontsize=8)
A.set_title("15 Nov: ABS (bed 100 + chamber 55), then cool-down\nbed started warm from the previous phase"); A.set_xlabel("minutes"); A.set_ylabel("°C"); A.grid(alpha=.3); A.legend(loc="upper right",bbox_to_anchor=(1,0.9),fontsize=8)
fig.tight_layout(); fig.savefig("2026-11-15-vents-closed.png",dpi=110)
