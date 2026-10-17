"""Independent exact checks of selected finite identities in the Bloch-law paper.

This is not a proof of the paper's random-environment estimates or thermodynamic result.
Uses Python standard-library rational arithmetic; no copied upstream implementation.
"""
from fractions import Fraction as Q
from pathlib import Path
import datetime, hashlib, json

ROOT=Path(__file__).resolve().parent
def dot(a,b): return sum((x*y for x,y in zip(a,b)),Q(0))
def mv(a,x): return [dot(row,x) for row in a]
def tr(a): return [list(row) for row in zip(*a)]
def sub(a,b): return [x-y for x,y in zip(a,b)]

def solve(a,b):
    """Exact RREF solution, free coordinates zero; None means inconsistent."""
    if not a: return []
    n=len(a[0]); rows=[list(row)+[rhs] for row,rhs in zip(a,b)]; pivots=[];r=0
    for c in range(n):
        pivot=next((k for k in range(r,len(rows)) if rows[k][c]),None)
        if pivot is None: continue
        rows[r],rows[pivot]=rows[pivot],rows[r]
        v=rows[r][c];rows[r]=[x/v for x in rows[r]]
        for k in range(len(rows)):
            if k!=r:
                v=rows[k][c];rows[k]=[x-v*y for x,y in zip(rows[k],rows[r])]
        pivots.append(c);r+=1
        if r==len(rows):break
    if any(all(x==0 for x in row[:n]) and row[n]!=0 for row in rows):return None
    x=[Q(0)]*n
    for k,c in enumerate(pivots):x[c]=rows[k][n]
    return x

def hit(u,i=0):
    """Solve first-step equations only on coordinates able to reach the target.

    A disjoint closed recurrent class has hitting probability zero; do not invert
    the entire singular transient candidate matrix or assume almost-sure killing.
    """
    n=len(u);reachable={i}
    while True:
        more={j for j in range(n) if any(u[k][j]>0 for k in reachable)}
        if more<=reachable:break
        reachable|=more
    indices=sorted(reachable-{i})
    a=[[Q(j==k)-u[k][j] for k in indices] for j in indices]
    x=solve(a,[u[i][j] for j in indices]);assert x is not None
    f=[Q(0)]*n;f[i]=Q(1)
    for j,value in zip(indices,x):f[j]=value
    assert all(0<=x<=1 for x in f)
    return f,dot([u[k][i] for k in range(n)],f)

def run():
    (ROOT/'audit').mkdir(exist_ok=True)
    f=Q
    cases=[
      ('immediate_killing',[[f(0)]],set()),
      ('self_loop',[[f(2,3)]],set()),
      ('non_symmetric',[[f(1,4),f(1,2)],[f(1,8),f(1,4)]],set()),
      ('three_state_leak',[[f(1,5),f(2,5),f(0)],[f(1,10),f(1,10),f(1,4)],[f(1,5),f(0),f(1,5)]],set()),
      ('closed_cycle',[[f(0),f(0),f(1)],[f(1),f(0),f(0)],[f(0),f(1),f(0)]],set()),
      ('unreachable_recurrent_class',[[f(1,4),f(1,2),f(0)],[f(1,8),f(1,4),f(0)],[f(0),f(0),f(1)]],set()),
      ('explicit_killed_coordinate',[[f(1,4),f(1,2),f(0)],[f(1,8),f(1,4),f(0)],[f(0),f(0),f(0)]],{2}),
      ('absorbing_target',[[f(1),f(0),f(0)],[f(0),f(1,4),f(1,2)],[f(0),f(1,8),f(1,4)]],set()),
    ]
    rows=[];bound_count=0;orientation_counterexamples=0
    for name,u,killed in cases:
        n=len(u);ut=tr(u)
        assert all(x>=0 for row in u for x in row)
        assert all(sum(row)<=1 for row in u+ut)
        assert all(all(u[k][j]==u[j][k]==0 for j in range(n)) for k in killed)
        a=[[Q(i==j)-u[i][j] for j in range(n)] for i in range(n)]
        g=[[Q(i==j)-(u[i][j]+u[j][i])/2 for j in range(n)] for i in range(n)]
        hitting,q=hit(u)
        if name in {'non_symmetric','unreachable_recurrent_class','explicit_killed_coordinate'}:
            assert q==Q(1,3) and hitting[:2]==[Q(1),Q(2,3)]
        if name=='unreachable_recurrent_class':assert hitting[2]==0
        if name in {'closed_cycle','absorbing_target'}:assert q==1
        harmonic=mv(tr(a),hitting);expected=[1-q]+[Q(0)]*(n-1)
        assert harmonic==expected
        orientation_counterexamples+=mv(a,hitting)!=expected
        for trial in [Q(0),Q(2,3),Q(-3,2)]:
            h=[Q(1)]+[trial if j not in killed else Q(0) for j in range(1,n)]
            y=sub(hitting,h);energy=dot(y,mv(a,y));assert energy>=0
            for c in [Q(0),Q(1,2),Q(1)]:
                plus=sub(mv(u,h),h);minus=sub(mv(ut,h),h);plus[0]+=c;minus[0]+=c
                assert energy==dot(y,minus)
                assert q-(1-c)==dot(h,plus)+dot(y,plus)
                dual=[solve(g,mu) for mu in [plus,minus]]
                bound_checked=all(x is not None for x in dual)
                if bound_checked:
                    x2=max(dot(mu,x) for mu,x in zip([plus,minus],dual));assert x2>=0
                    # G is symmetric diagonally dominant with nonnegative diagonal,
                    # hence PSD. G*x=mu implies the energy-dual bound with sqrt(mu*x).
                    assert all(g[j][j]>=sum(abs(g[j][k]) for k in range(n) if j!=k) for j in range(n))
                    assert abs(q-(1-c))<=abs(dot(h,plus))+2*x2
                    bound_count+=1
                rows.append(dict(case=name,trial=str(trial),c=str(c),q=str(q),hitting=list(map(str,hitting)),identities_pass=True,stability_bound_checked=bound_checked))
    assert orientation_counterexamples>0
    # Independent Gaussian-moment arithmetic for the ideal-magnon coefficient.
    quartic_gaussian_ratio=Q(3,4)
    one_dimensional=quartic_gaussian_ratio/Q(12)
    three_dimensional=3*one_dimensional
    leading=Q(1,8)
    correction=leading*three_dimensional
    assert one_dimensional==Q(1,16) and correction==Q(3,128)
    # Negative control: forgetting dimension-three multiplication must be detectable.
    assert leading*one_dimensional!=correction
    result=dict(status='pass',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      transition_scenarios=len(cases),exact_parameter_cases=len(rows),identity_cases_passed=len(rows),
      energy_dual_stability_cases_passed=bound_count,
      invalid_forward_in_place_of_adjoint_detected_scenarios=orientation_counterexamples,
      ideal_density=dict(leading_rational_factor=str(leading),correction_rational_factor=str(correction),
                        expression='zeta(3/2)/(8*pi^(3/2))*t^(-3/2) + 3*zeta(5/2)/(128*pi^(3/2))*t^(-5/2)',t='beta*S'),
      cases=rows,
      limits=['Finite cases support the checked identities; they do not prove the entire theorem.',
              'The exact Gaussian arithmetic checks coefficient normalization, not the paper\'s interaction-error estimate.',
              'No Lean build, infinite-volume computation, quantum hardware or private research implementation used.'])
    (ROOT/'audit'/'CAPACITY_CHECK_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))

if __name__=='__main__':run()
