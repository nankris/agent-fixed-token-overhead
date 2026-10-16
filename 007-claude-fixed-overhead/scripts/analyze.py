import csv, statistics as S, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
import numpy as np
D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(f"{D}/results/runs.csv")))
order = ["default","strict_mcp","safe_mode","strict_noskills","strict_noskills_nodyn","strict_noskills_core3","strict_noskills_notools","custom_sysprompt_notools"]
label = {"default":"default (MCP+skills+all tools)","strict_mcp":"--strict-mcp-config","safe_mode":"--safe-mode","strict_noskills":"+ --disable-slash-commands",
 "strict_noskills_nodyn":"+ --exclude-dynamic-…","strict_noskills_core3":"+ --tools Bash,Read,Edit","strict_noskills_notools":"+ --tools \"\"","custom_sysprompt_notools":"+ --system-prompt (1 line), no tools"}
out=[]
for c in order:
    rs=[r for r in rows if r["cond"]==c]
    prompt=[int(r["input_tokens"])+int(r["cache_creation_tokens"])+int(r["cache_read_tokens"]) for r in rs]
    cost=[float(r["est_cost_usd"]) for r in rs]
    out.append(dict(cond=c, n=len(rs), prompt_tokens_median=int(S.median(prompt)), prompt_min=min(prompt), prompt_max=max(prompt),
        cache_creation_median=int(S.median(int(r["cache_creation_tokens"]) for r in rs)),
        cache_read_median=int(S.median(int(r["cache_read_tokens"]) for r in rs)),
        est_cost_median=round(S.median(cost),4), model=rs[0]["model"]))
w=csv.DictWriter(open(f"{D}/results/summary.csv","w"),fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
for o in out: print(o)
# implied prices via least squares on all rows: cost = a*input + b*cc + c*cr + d*out
A=np.array([[int(r["input_tokens"]),int(r["cache_creation_tokens"]),int(r["cache_read_tokens"]),int(r["output_tokens"])] for r in rows],float)
y=np.array([float(r["est_cost_usd"]) for r in rows])
coef,*_=np.linalg.lstsq(A,y,rcond=None); print("implied $/M input,cc,cr,out:",(coef*1e6).round(3))
fig,ax=plt.subplots(1,2,figsize=(13,5))
names=[label[o["cond"]] for o in out]; vals=[o["prompt_tokens_median"] for o in out]
ax[0].barh(names[::-1], vals[::-1], color="#4a7bd1")
for i,v in enumerate(vals[::-1]): ax[0].text(v+200,i,f"{v:,}",va="center",fontsize=9)
ax[0].set_xlabel("prompt tokens on a 1-word reply (median of 3)"); ax[0].set_title("Claude Code 2.1.300 fixed overhead, trimmed step by step")
ax[0].set_xlim(0,max(vals)*1.18)
c=[o["est_cost_median"] for o in out]
ax[1].barh(names[::-1], c[::-1], color="#d17b4a")
for i,v in enumerate(c[::-1]): ax[1].text(v+0.002,i,f"${v:.3f}",va="center",fontsize=9)
ax[1].set_xlabel("API-equivalent est. $ per call (Claude's total_cost_usd)"); ax[1].set_title("…and what that first call costs (cold-ish cache)")
ax[1].set_xlim(0,max(c)*1.25); ax[1].set_yticks([])
plt.tight_layout(); plt.savefig(f"{D}/results/chart.png",dpi=110)
