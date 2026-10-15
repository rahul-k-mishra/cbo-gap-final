"""Figure 2 from exactcal_summary.csv (left, exact calibration) and the two
144-cell panels (right). Left panel previously plotted the probe-calibrated
values now superseded in Table 3."""
import csv, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 8})
E = list(csv.DictReader(open('exactcal_summary.csv')))
for x in E: x['d'] = int(x['d']); x['tau'] = float(x['tau']); x['slope'] = float(x['slope'])
V = [float(x['slope']) for x in csv.DictReader(open('visibility_summary.csv'))]
D = [2, 5, 10, 40]
f, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
for t, mk, col in ((0.5, 'o', 'k'), (0.1, 's', '0.45'), (0.01, '^', '0.7')):
    y = [np.mean([x['slope'] for x in E if x['d'] == d and abs(x['tau'] - t) < 1e-12]) for d in D]
    assert np.isfinite(y).all()
    ax[0].plot(D, y, mk + '-', color=col, lw=1.5, ms=4.5, label=r'$\tau_0=%g$' % t)
ax[0].axhline(-1.0, color='r', ls='--', lw=0.9)
ax[0].set_xscale('log', base=2); ax[0].set_xticks(D); ax[0].set_xticklabels(D)
ax[0].set_xlabel(r'dimension $d$'); ax[0].set_ylabel(r'$\hat\gamma$')
ax[0].legend(fontsize=6.5, frameon=False, loc='lower left')
ax[0].set_title('exact calibration', fontsize=8)
S = [x['slope'] for x in E]
bins = np.linspace(-1.45, -0.55, 34)
ax[1].hist(V, bins=bins, color='0.75', edgecolor='0.4', lw=0.4,
           label=r'$B$-matched, s.d. $0.379$')
ax[1].hist(S, bins=bins, histtype='step', color='k', lw=1.4,
           label=r'exactly calibrated, s.d. $0.109$')
ax[1].axvline(-1.0, color='r', ls='--', lw=0.9)
ax[1].set_xlabel(r'$\hat\gamma$'); ax[1].set_ylabel('cells')
ax[1].legend(fontsize=6.5, frameon=False)
ax[1].set_title(r'$144$ cells each', fontsize=8)
f.tight_layout(); f.savefig('fig2.pdf'); plt.close(f)
print("fig2.pdf rebuilt from exactcal_summary.csv; all finite")
