"""all finished glyph forms as (outer, holes, kind) keyed 'letter_form'."""
import os, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def load(n, rel):
    sp = importlib.util.spec_from_file_location(n, os.path.join(ROOT, rel)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
def build():
    A = load("al", "alif/geom.py"); B = load("ba", "ba/geom.py"); J = load("je", "jeem/geom.py")
    SE = load("se", "seen/geom.py"); SA = load("sa", "sad/geom.py"); T = load("ta", "tah/geom.py"); K = load("ka", "kaf/geom.py")
    F = load("fa", "fa/geom.py"); AS = load("ain_strict", "ain/strict.py"); FS = load("fa_strict", "fa/strict.py"); HS = load("heh_strict", "heh/strict.py"); MS = load("mh_strict", "mh/strict.py")
    R = load("re", "reh/geom.py"); WW = load("wa", "waw/geom.py")
    g = {}
    def put(name, outer, holes=()):
        g[name] = (outer, list(holes), name.split("_")[-1])
    for f in ("isol", "fina"): put("alif_" + f, getattr(A, "alif_" + f)())
    for f in ("isol", "init", "medi", "fina"):
        put("lam_" + f, getattr(A, "lam_" + f)()); put("ba_" + f, getattr(B, "ba_" + f)())
        put("meem_" + f, getattr(MS, "meem_" + f)()); put("hah_" + f, getattr(MS, "hah_" + f)())
        put("kaf_" + f, getattr(K, "kaf_" + f)())
        put("fa_" + f, getattr(FS, "fa_" + f)())
        put("qaf_" + f, getattr(HS, "qaf_" + f)()) if f in ("isol", "fina") else put("qaf_" + f, getattr(FS, "fa_" + f)())
        put("heh_" + f, getattr(HS, "heh_" + f)())
        for L in ("nun", "ya"): put(L + "_" + f, getattr(HS, L + "_" + f)()) if f in ("isol", "fina") else put(L + "_" + f, getattr(B, "ba_" + f)())
        put("ain_" + f, getattr(AS, "ain_" + f)())
        put("tah_" + f, getattr(T, "tah_" + f)(), [T.slot()])
    put("seen_isol", SE.seen_isol()[0]); put("seen_init", SE.seen_init()); put("seen_medi", SE.seen_medi()); put("seen_fina", SE.seen_fina()[0])
    put("sad_isol", SA.sad_isol()[0], [SA.slot()]); put("sad_init", SA.sad_init(), [SA.slot()])
    put("sad_medi", SA.sad_medi(), [SA.slot()]); put("sad_fina", SA.sad_fina()[0], [SA.slot()])
    put("lamalif_isol", MS.lamalif_isol(), [MS.lamalif_isol_hole()]); put("lamalif_fina", MS.lamalif_fina())
    put("dal_isol", J.dal_isol()); put("dal_fina", J.dal_fina())
    raa = [(x, y - 1.5, 0) for x, y in R.SOLID]; put("raa_isol", raa); put("raa_fina", raa)
    waw = [(p[0], p[1] - 1.5, b) for p, b in WW.POLY]; put("waw_isol", waw); put("waw_fina", waw)
    return g
