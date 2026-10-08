"""Figure 4: the tau_0 x r regime map, generated from regimemap_M_summary.csv.
Asserts finiteness before writing. The predecessor of this file wrote NaN because
the rows it asked for were absent from a clobbered archive; that cannot pass here."""
import csv, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 9})
S = list(csv.DictReader(open('regimemap_M_summary.csv')))
for x in S:
    x['d'] = int(x['d']); x['r'] = float(x['r']); x['tau'] = float(x['tau']); x['slope'] = float(x['slope'])
TAUS = [0.5, 0.1, 0.03, 0.01]; RS = [0.5, 1.0, 1.5, 2.0, 3.0]
AXIDX = None
PANELS = [('isotropic', 10), ('isotropic', 40), ('anisotropic', 10), ('anisotropic', 40)]
def cell(dif, d, t, r):
    v = [x['slope'] for x in S if x['diffusion'] == dif and x['d'] == d
         and abs(x['tau'] - t) < 1e-9 and abs(x['r'] - r) < 1e-9]
    assert v, "no data for %s d=%d tau=%s r=%s" % (dif, d, t, r)
    return float(np.mean(v))
f, axg = plt.subplots(2, 2, figsize=(7.0, 5.2))
AX = axg.ravel()
for j, (dif, d) in enumerate(PANELS):
    A = np.array([[cell(dif, d, t, r) for r in RS] for t in TAUS])
    assert np.isfinite(A).all(), "NaN in panel %s d=%d" % (dif, d)
    im = AX[j].imshow(A, vmin=-1.04, vmax=-0.35, cmap='Greys_r', aspect='auto')
    AX[j].set_xticks(range(len(RS))); AX[j].set_xticklabels(RS, fontsize=8)
    AX[j].set_yticks(range(len(TAUS)))
    AX[j].set_yticklabels(TAUS if j % 2 == 0 else [], fontsize=8)
    AX[j].axvline(1.5, color='r', ls='--', lw=1.0)
    AX[j].set_title("%s, $d=%d$" % ("iso" if dif == 'isotropic' else "aniso", d), fontsize=9)
    AX[j].set_xlabel(r'$r$', fontsize=9)
    for a in range(len(TAUS)):
        for b in range(len(RS)):
            AX[j].text(b, a, "%.2f" % A[a, b], ha='center', va='center', fontsize=8.0,
                       color='k' if A[a, b] > -0.70 else 'w')
for j in (0, 2):
    AX[j].set_ylabel(r'$\tau_0$', fontsize=9)
cb = f.colorbar(im, ax=axg.ravel().tolist(), fraction=0.045, pad=0.02); cb.set_label(r'$\hat\gamma$', fontsize=9)
cb.ax.tick_params(labelsize=8)
f.savefig("fig6.pdf", bbox_inches='tight'); plt.close(f)
print("fig6.pdf: 4 panels x %d tau x %d r, all finite" % (len(TAUS), len(RS)))
