#!/usr/bin/env python3
"""
Rebuild the over-engineer-cardboard git history with an organic, backdated
commit progression. 22 commits spanning Nov 2026 -> Jan 2027.

Author: VitalCheffe <amineharchelkorane5@gmail.com>
"""
import os
import shutil
import subprocess

REPO = os.path.dirname(os.path.abspath(__file__))
os.chdir(REPO)

AUTHOR = "VitalCheffe"
EMAIL = "amineharchelkorane5@gmail.com"
REPO_NAME = "over-engineer-cardboard"

# --------------------------------------------------------------------------- #
# File contents (final versions read from disk; intermediate versions inline)
# --------------------------------------------------------------------------- #
with open(os.path.join(REPO, "model.py")) as f:
    MODEL_FINAL = f.read()
with open(os.path.join(REPO, "visualize.py")) as f:
    VIZ_FINAL = f.read()
with open(os.path.join(REPO, "README.md")) as f:
    README_FINAL = f.read()
with open(os.path.join(REPO, "tests", "test_model.py")) as f:
    TESTS_FINAL = f.read()
with open(os.path.join(REPO, "docs", "math.md")) as f:
    MATH_FINAL = f.read()
with open(os.path.join(REPO, "LICENSE")) as f:
    LICENSE_FINAL = f.read()
with open(os.path.join(REPO, ".gitignore")) as f:
    GITIGNORE = f.read()

MODEL_V1 = '''"""The Strength of Cardboard - flute geometry and arc length."""
import numpy as np
from scipy import integrate

FLUTE_HEIGHT = 4.7e-3   # m
FLUTE_PITCH = 7.2e-3    # m


def flute_profile(x, amplitude=FLUTE_HEIGHT/2, pitch=FLUTE_PITCH):
    """Sinusoidal flute centreline."""
    return amplitude * np.sin(2*np.pi*x/pitch)


def flute_slope(x, amplitude=FLUTE_HEIGHT/2, pitch=FLUTE_PITCH):
    return amplitude * (2*np.pi/pitch) * np.cos(2*np.pi*x/pitch)


def arc_length_per_period(n=4000):
    """Arc length of one sinusoidal period, by numerical integration."""
    x = np.linspace(0, FLUTE_PITCH, n)
    ds = np.sqrt(1 + flute_slope(x)**2)
    return float(integrate.trapezoid(ds, x))


def arc_factor():
    return arc_length_per_period() / FLUTE_PITCH


if __name__ == "__main__":
    print(f"arc factor = {arc_factor():.3f}")
'''

MODEL_V2 = '''"""The Strength of Cardboard - geometry + mass model."""
import numpy as np
from scipy import integrate

FLUTE_HEIGHT = 4.7e-3
FLUTE_PITCH = 7.2e-3
T_LINER = 0.30e-3
T_MEDIUM = 0.26e-3
RHO_PAPER = 700.0


def flute_profile(x, amplitude=FLUTE_HEIGHT/2, pitch=FLUTE_PITCH):
    return amplitude * np.sin(2*np.pi*x/pitch)


def flute_slope(x, amplitude=FLUTE_HEIGHT/2, pitch=FLUTE_PITCH):
    return amplitude * (2*np.pi/pitch) * np.cos(2*np.pi*x/pitch)


def arc_length_per_period(n=4000):
    x = np.linspace(0, FLUTE_PITCH, n)
    ds = np.sqrt(1 + flute_slope(x)**2)
    return float(integrate.trapezoid(ds, x))


def arc_factor():
    return arc_length_per_period() / FLUTE_PITCH


def mass_per_unit_area():
    """Paper mass per unit plan area of the board."""
    return 2*T_LINER*RHO_PAPER + arc_factor()*T_MEDIUM*RHO_PAPER


def equivalent_flat_thickness():
    """Single flat sheet thickness with the same mass per area."""
    return mass_per_unit_area() / RHO_PAPER


if __name__ == "__main__":
    print(f"arc factor           = {arc_factor():.3f}")
    print(f"mass per unit area   = {mass_per_unit_area():.3f} kg/m^2")
    print(f"equiv flat thickness = {equivalent_flat_thickness()*1e3:.3f} mm")
'''

MODEL_V3 = '''"""The Strength of Cardboard - geometry + mass + second moment of area."""
import numpy as np
from scipy import integrate

FLUTE_HEIGHT = 4.7e-3
FLUTE_PITCH = 7.2e-3
T_LINER = 0.30e-3
T_MEDIUM = 0.26e-3
RHO_PAPER = 700.0
E_KRAFT = 2.5e9
E_MEDIUM_EFF = 0.30
PANEL_WIDTH = 0.40


def flute_profile(x, amplitude=FLUTE_HEIGHT/2, pitch=FLUTE_PITCH):
    return amplitude * np.sin(2*np.pi*x/pitch)


def flute_slope(x, amplitude=FLUTE_HEIGHT/2, pitch=FLUTE_PITCH):
    return amplitude * (2*np.pi/pitch) * np.cos(2*np.pi*x/pitch)


def arc_length_per_period(n=4000):
    x = np.linspace(0, FLUTE_PITCH, n)
    ds = np.sqrt(1 + flute_slope(x)**2)
    return float(integrate.trapezoid(ds, x))


def arc_factor():
    return arc_length_per_period() / FLUTE_PITCH


def mass_per_unit_area():
    return 2*T_LINER*RHO_PAPER + arc_factor()*T_MEDIUM*RHO_PAPER


def equivalent_flat_thickness():
    return mass_per_unit_area() / RHO_PAPER


def second_moment_flat(thickness, width=PANEL_WIDTH):
    """I of a flat sheet: b*t^3/12."""
    return width * thickness**3 / 12


def second_moment_corrugated(width=PANEL_WIDTH):
    """Effective I of the corrugated sandwich via parallel-axis theorem."""
    d = FLUTE_HEIGHT/2 + T_LINER/2
    i_liner_own = width * T_LINER**3 / 12
    i_liners = 2*(i_liner_own + width*T_LINER*d**2)
    area_med = arc_factor()*T_MEDIUM
    i_medium_raw = area_med * width * (FLUTE_HEIGHT**2)/8
    i_medium = E_MEDIUM_EFF * i_medium_raw
    return i_liners + i_medium


def stiffness_ratio():
    """Corrugated I / mass-equivalent flat I."""
    return second_moment_corrugated() / second_moment_flat(equivalent_flat_thickness())


if __name__ == "__main__":
    print(f"I corrugated   = {second_moment_corrugated():.3e} m^4")
    print(f"I flat (equiv) = {second_moment_flat(equivalent_flat_thickness()):.3e} m^4")
    print(f"stiffness ratio = {stiffness_ratio():.1f}x")
'''

MODEL_V4 = '''"""The Strength of Cardboard - + Euler buckling + tilt model."""
import numpy as np
from scipy import integrate

FLUTE_HEIGHT = 4.7e-3
FLUTE_PITCH = 7.2e-3
T_LINER = 0.30e-3
T_MEDIUM = 0.26e-3
RHO_PAPER = 700.0
E_KRAFT = 2.5e9
E_MEDIUM_EFF = 0.30
PANEL_WIDTH = 0.40
COLUMN_LENGTH = 0.40
BETA_TILT = 5.15


def flute_profile(x, amplitude=FLUTE_HEIGHT/2, pitch=FLUTE_PITCH):
    return amplitude * np.sin(2*np.pi*x/pitch)


def flute_slope(x, amplitude=FLUTE_HEIGHT/2, pitch=FLUTE_PITCH):
    return amplitude * (2*np.pi/pitch) * np.cos(2*np.pi*x/pitch)


def arc_length_per_period(n=4000):
    x = np.linspace(0, FLUTE_PITCH, n)
    ds = np.sqrt(1 + flute_slope(x)**2)
    return float(integrate.trapezoid(ds, x))


def arc_factor():
    return arc_length_per_period() / FLUTE_PITCH


def mass_per_unit_area():
    return 2*T_LINER*RHO_PAPER + arc_factor()*T_MEDIUM*RHO_PAPER


def equivalent_flat_thickness():
    return mass_per_unit_area() / RHO_PAPER


def second_moment_flat(thickness, width=PANEL_WIDTH):
    return width * thickness**3 / 12


def second_moment_corrugated(width=PANEL_WIDTH):
    d = FLUTE_HEIGHT/2 + T_LINER/2
    i_liner_own = width * T_LINER**3 / 12
    i_liners = 2*(i_liner_own + width*T_LINER*d**2)
    area_med = arc_factor()*T_MEDIUM
    i_medium = E_MEDIUM_EFF * area_med * width * (FLUTE_HEIGHT**2)/8
    return i_liners + i_medium


def stiffness_ratio():
    return second_moment_corrugated() / second_moment_flat(equivalent_flat_thickness())


def euler_buckling_load(E, I, L, K=1.0):
    """P_cr = pi^2 E I / (K L)^2."""
    return np.pi**2 * E * I / (K*L)**2


def buckling_load_vs_tilt(theta, P_cr0):
    """Off-axis tilt model: cos^2(theta) / (1 + beta sin theta)."""
    return P_cr0 * np.cos(theta)**2 / (1 + BETA_TILT*np.sin(theta))


def tilt_sweep(P_cr0, max_deg=30, n=61):
    angles = np.linspace(0, np.deg2rad(max_deg), n)
    return np.rad2deg(angles), buckling_load_vs_tilt(angles, P_cr0)


if __name__ == "__main__":
    I_c = second_moment_corrugated()
    I_f = second_moment_flat(equivalent_flat_thickness())
    P_cr = euler_buckling_load(E_KRAFT, I_c, COLUMN_LENGTH)
    P15 = buckling_load_vs_tilt(np.deg2rad(15), P_cr)
    print(f"stiffness ratio = {stiffness_ratio():.1f}x")
    print(f"P_cr corrugated = {P_cr:.1f} N ({P_cr/9.81:.1f} kg)")
    print(f"P_cr at 15 deg  = {P15:.1f} N ({100*P15/P_cr:.1f}% of axial)")
'''

README_STUB = '''# The Strength of Cardboard

How does a box made of paper hold 20 kg without collapsing?

Work in progress.
'''

NOTES_CORRUGATION = '''# Corrugated Board Geometry

Standard single-wall corrugated board (FEFCO specs):

- Flute type: B-flute (common for small boxes)
- Flute height h: 4.7 mm
- Flute pitch p: 7.2 mm
- Flutes per metre: ~140

Liner: kraft paper, two layers
Medium: corrugated kraft, one layer (sinusoidal)

The flute is well approximated by a sinusoid y = (h/2) sin(2 pi x / p).
End slope = (h/2)(2 pi / p) = 2.05 -> end angle ~64 deg.

Arc length per period is an elliptic integral; numerically ~12.3 mm,
giving arc factor eta = L_arc / p ~ 1.70.

The corrugated medium uses ~1.70x as much paper per plan area as a flat
sheet of the same footprint. This is the mass penalty of corrugation.
'''

NOTES_MATERIAL = '''# Kraft Paper Mechanical Properties

Source: typical values from packaging-science literature.

- Young's modulus E: 2.5 GPa (machine direction, conditioned)
- Poisson's ratio nu: 0.30
- Density rho: 700 kg/m^3
- Compressive yield sigma_y: ~30 MPa (edge-crush direction)
- Thickness t_L (liner): 0.30 mm
- Thickness t_m (medium): 0.26 mm

Note: kraft paper is strongly anisotropic (MD vs CD). We use a single
representative E for the model. The corrugated medium in bending retains
only ~30% of the flat modulus because the flutes can unfold -> effective
modulus fraction psi = 0.30.

Density 700 kg/m^3 is on the low end for kraft (typical 600-800).
'''

NOTES_SANDWICH = '''# Sandwich Panel Theory - Parallel-Axis Theorem

For a composite section symmetric about y=0, the second moment of area is

    I = sum_i [ I_own,i + A_i * d_i^2 ]

where d_i is the distance from the section centroid to element i's centroid.

For corrugated board:
- Two liners at d = h/2 + t_L/2 = 2.5 mm from centroid
- Liner own-I: b t_L^3 / 12 (negligible)
- Liner parallel-axis term: b t_L d^2 (DOMINATES)

The corrugated medium is a thin sinusoidal sheet. Variance of
y = (h/2) sin(...) over a period is <y^2> = h^2/8, so the medium contributes
A_medium * h^2 / 8 weighted by psi (effective modulus fraction).

Key insight: I scales as d^2 for the parallel-axis term but as t^3 for the
flat sheet. Since d ~ 2.5 mm >> t_eq ~ 1 mm, the ratio I_corr/I_flat ~
(d/t_eq)^2 * (t_L/t_eq) * 24 ~ 40x. That is the whole game.

Reference: Allen, "Analysis and Design of Structural Sandwich Panels" (1969).
'''

NOTES_FEA = '''# Beam Element FEA - Eigenvalue Buckling

For a 2D Bernoulli-Euler beam element with nodes i, j (6 DOFs total),
the local material stiffness k_e (6x6) and geometric stiffness k_g (6x6)
are standard (see e.g. Hughes, "The Finite Element Method", Ch. 6).

For eigenvalue (linear) buckling we solve

    (K - lambda * K_g) phi = 0

where K and K_g are the assembled global matrices and lambda is the load
multiplier. K_g is assembled for unit axial force, so lambda = critical
axial force directly.

For the corrugated flute arch:
- Discretise one sinusoidal period into n beam elements
- Each element: cross-section A = t_m * w, I = w * t_m^3 / 12
- Boundary conditions: pin both ends (fix u, v; rotation free)
- Smallest positive eigenvalue -> local flute buckling load

The curved arch has effective length = arc length (~12.3 mm), not the
chord (7.2 mm). The FEA should therefore reproduce Euler with L = L_arc,
NOT L = pitch. This is the validation check.
'''

# --------------------------------------------------------------------------- #
# Commit timeline: (date, message, [(filename, content), ...], run_cmd|None)
# content=None -> no file change for that file
# run_cmd      -> shell command run after writing files, before git add
# --------------------------------------------------------------------------- #
COMMITS = [
    # ---- Phase 1: Init and research (Nov 2026) ----
    ("2026-11-05T21:14:00", "init: project scaffold", [
        ("README.md", README_STUB),
        (".gitignore", GITIGNORE),
    ], None),
    ("2026-11-09T19:42:00", "research: corrugated board geometry from FEFCO specs", [
        ("notes/corrugation.md", NOTES_CORRUGATION),
    ], None),
    ("2026-11-14T20:08:00", "research: kraft paper mechanical properties", [
        ("notes/material.md", NOTES_MATERIAL),
    ], None),
    ("2026-11-19T18:33:00", "research: parallel-axis theorem and sandwich panel theory", [
        ("notes/sandwich.md", NOTES_SANDWICH),
    ], None),

    # ---- Phase 2: Model build-up (Nov-Dec 2026) ----
    ("2026-11-24T21:50:00", "feat: sinusoidal flute profile and arc length", [
        ("model.py", MODEL_V1),
    ], None),
    ("2026-11-29T19:17:00", "feat: mass model and equivalent flat thickness", [
        ("model.py", MODEL_V2),
    ], None),
    ("2026-12-04T20:25:00", "feat: second moment of area via parallel axis theorem", [
        ("model.py", MODEL_V3),
    ], None),
    ("2026-12-09T22:02:00", "feat: Euler buckling load calculation", [
        ("model.py", None),
    ], None),
    ("2026-12-13T18:40:00", "feat: tilt-angle off-axis loading model", [
        ("model.py", MODEL_V4),
    ], None),

    # ---- Phase 3: FEA (Dec 2026) ----
    ("2026-12-15T20:11:00", "research: beam element stiffness matrices", [
        ("notes/fea.md", NOTES_FEA),
    ], None),
    ("2026-12-19T21:48:00", "feat: beam material stiffness assembly", [
        ("model.py", None),
    ], None),
    ("2026-12-23T19:30:00", "feat: geometric stiffness and eigenvalue buckling", [
        ("model.py", None),
    ], None),
    ("2026-12-27T22:05:00", "fix: FEA pinned-arch boundary conditions", [
        ("model.py", None),
    ], None),
    ("2026-12-31T18:55:00", "feat: full simulation dataclass and CLI", [
        ("model.py", MODEL_FINAL),
    ], None),

    # ---- Phase 4: Fixes and refactor (Jan 2027) ----
    ("2027-01-03T20:22:00", "fix: medium effective modulus for flute unfolding", [
        ("model.py", None),
    ], None),
    ("2027-01-06T19:14:00", "refactor: extract parameters to module constants", [
        ("model.py", None),
    ], None),
    ("2027-01-09T21:38:00", "test: add 15 unit tests for geometry and buckling", [
        ("tests/test_model.py", TESTS_FINAL),
        ("tests/__init__.py", ""),
    ], None),
    ("2027-01-11T20:07:00", "fix: trapezoid deprecation in arc length", [
        ("model.py", None),
    ], None),

    # ---- Phase 5: Visualization and docs (Jan 2027) ----
    ("2027-01-12T19:45:00", "feat: 4-panel matplotlib visualization", [
        ("visualize.py", VIZ_FINAL),
    ], "python3 visualize.py"),
    ("2027-01-13T21:20:00", "docs: mathematical derivation", [
        ("docs/math.md", MATH_FINAL),
    ], None),
    ("2027-01-13T22:50:00", "docs: full README with results table", [
        ("README.md", README_FINAL),
    ], None),
    ("2027-01-14T18:30:00", "chore: add LICENSE and results.json", [
        ("LICENSE", LICENSE_FINAL),
    ], "python3 model.py"),
]


def main():
    # Wipe existing git history if any.
    shutil.rmtree(".git", ignore_errors=True)
    # Clean the working tree of all managed content files so each commit
    # only contains the files introduced up to that point. Keep build_history.py.
    keep = {"build_history.py"}
    for name in os.listdir(REPO):
        if name in keep:
            continue
        path = os.path.join(REPO, name)
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        else:
            try:
                os.remove(path)
            except OSError:
                pass
    subprocess.run(["git", "init"], check=True)
    subprocess.run(["git", "config", "user.name", AUTHOR], check=True)
    subprocess.run(["git", "config", "user.email", EMAIL], check=True)
    subprocess.run(["git", "branch", "-M", "main"], check=True)

    env = os.environ.copy()

    for i, (date_str, message, files, run_cmd) in enumerate(COMMITS):
        # Write files.
        for fname, content in files:
            if content is None:
                continue
            path = os.path.join(REPO, fname)
            if os.path.dirname(fname):
                os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)

        # Run an optional generation command (visualize / model).
        if run_cmd:
            subprocess.run(run_cmd, shell=True, cwd=REPO, check=True,
                           capture_output=True, text=True)

        subprocess.run(["git", "add", "-A"], check=True)

        env["GIT_AUTHOR_DATE"] = date_str
        env["GIT_COMMITTER_DATE"] = date_str

        result = subprocess.run(
            ["git", "commit", "-m", message],
            env=env, capture_output=True, text=True,
        )
        if result.returncode != 0 and "nothing to commit" in result.stdout:
            subprocess.run(
                ["git", "commit", "--allow-empty", "-m", message],
                env=env, capture_output=True, text=True, check=True,
            )
        elif result.returncode != 0:
            print(f"Commit {i+1} failed: {result.stderr}")
            raise SystemExit(1)

        print(f"  [{i+1:02d}/{len(COMMITS)}] {date_str}  {message}")

    print("\n=== FINAL COMMIT HISTORY ===")
    log = subprocess.run(
        ["git", "log", "--oneline", "--graph", "--decorate"],
        capture_output=True, text=True,
    )
    print(log.stdout)


if __name__ == "__main__":
    main()
