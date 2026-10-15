"""Figure 5 from regimemap_D_real.csv. Left panel leads with the non-admissible
contrast gamma(1)-gamma(3), which the text calls the stronger result; the
boundary-spanning contrast gamma(0.75)-gamma(3) is shown dashed as sensitivity."""
import csv, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 8})
R = list(csv.DictReader(open('regimemap_D_real.csv')))
for x in R:
    x['d'] = int(x['d']); x['r'] = float(x['r']); x['slope'] = float(x['slope'])
D = [5, 10, 20, 40, 80]; RS = [0.75, 1.0, 1.25, 1.5, 2.0, 3.0]
def cs(dif, d, r):
    return dict(((x['objective'], x['rep']), x['slope']) for x in R
                if x['diffusion'] == dif and x['d'] == d and abs(x['r'] - r) < 1e-9)
def drop(dif, d, lo):
    a, b = cs(dif, d, lo), cs(dif, d, 3.0); k = sorted(set(a) & set(b))
    return -float(np.mean([a[x] - b[x] for x in k]))
f, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
for dif, mk, col in (('isotropic', 'o', 'k'), ('anisotropic', 's', '0.55')):
    y1 = [drop(dif, d, 1.0) for d in D]
    y0 = [drop(dif, d, 0.75) for d in D]
    assert np.isfinite(y1).all() and np.isfinite(y0).all()
    ax[0].plot(D, y1, mk + '-', color=col, lw=1.5, ms=4, label=dif + r', $r{=}1{\to}3$')
    ax[0].plot(D, y0, mk + '--', color=col, lw=1.0, ms=3, alpha=0.75,
               label=dif + r', $r{=}0.75{\to}3$')
ax[0].set_xscale('log', base=2); ax[0].set_xticks(D); ax[0].set_xticklabels(D)
ax[0].set_xlabel(r'dimension $d$'); ax[0].set_ylabel(r'severity $S(r_1,r_2)$')
ax[0].legend(fontsize=5.6, frameon=False, loc='upper left')
ax[0].set_title('severity outside the admissible region', fontsize=8)
for d, st in zip(D, ['-', '--', '-.', ':', '-']):
    g = []
    for r in RS:
        a, i = cs('anisotropic', d, r), cs('isotropic', d, r); k = sorted(set(a) & set(i))
        g.append(float(np.mean([a[x] - i[x] for x in k])))
    ax[1].plot(RS, g, st, marker='.', lw=1.2, ms=5, label='$d=%d$' % d)
ax[1].axhline(0, color='k', lw=0.6)
ax[1].axvline(1.0, color='r', ls='--', lw=1.0)
ax[1].set_xlabel(r'$r=d\sigma^2/(2\lambda)$')
ax[1].set_ylabel(r'anisotropic $-$ isotropic gap in $\hat\gamma$')
ax[1].legend(fontsize=6, frameon=False, ncol=2)
ax[1].set_title('paired difference by regime', fontsize=8)
f.tight_layout(); f.savefig('fig7.pdf'); plt.close(f)
print("fig7.pdf rebuilt: non-admissible contrast primary, all finite")
