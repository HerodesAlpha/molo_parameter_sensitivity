#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple hydrostatic / eigenperiod study tool for MOLO-type floaters.

- Supports arbitrary number of columns (outer + center)
- Computes displacement, GM, hydrostatic stiffness
- Estimates heave and pitch/roll eigenperiods
- Includes heave added mass scaling from lower flanges / plates,
  calibrated against the MOLO Y7 15 MW reference.

You can adapt the example in main() to test different geometries.
"""

import math
from dataclasses import dataclass, field
from typing import List, Optional

G = 9.81          # m/s^2
RHO_W = 1025.0    # kg/m3  (seawater)


@dataclass
class Column:
    """Single vertical column (cylindrical)"""
    radius: float         # radial distance from centerline [m]
    diameter: float       # OD at waterplane [m]
    draft: float          # submerged length [m]
    freeboard: float      # height above SWL [m]


@dataclass
class MassItem:
    """Lumped mass with vertical position."""
    mass: float           # [t]
    z: float              # [m] (positive upwards, 0 at SWL)


@dataclass
class LowerPlates:
    """
    Represent the three radial lower flanges:
    each is approx. a rectangular plate length x width.
    """
    n_plates: int         # typically 3
    length: float         # radial length [m] (center to outer edge)
    width: float          # width [m]


@dataclass
class FloaterConfig:
    columns: List[Column]
    lower_plates: LowerPlates
    mass_items: List[MassItem]  # tower, RNA, steel, ballast etc.
    water_density: float = RHO_W
    gravity: float = G
    # Optional: calibration data for heave added mass (15 MW reference)
    ref_mass_total: Optional[float] = None           # [kg]
    ref_C33: Optional[float] = None                  # [N/m]
    ref_T_heave: Optional[float] = None              # [s]
    ref_plate_length: Optional[float] = None         # [m]
    ref_plate_width: Optional[float] = None          # [m]


def compute_displacement(config: FloaterConfig) -> float:
    """Displacement volume [m3] from cylindrical columns."""
    V = 0.0
    for col in config.columns:
        area = math.pi * (col.diameter / 2.0)**2
        V += area * col.draft
    return V


def compute_waterplane_area(config: FloaterConfig) -> float:
    """Waterplane area [m2] from column waterplanes."""
    A = 0.0
    for col in config.columns:
        A += math.pi * (col.diameter / 2.0)**2
    return A


def compute_zB(config: FloaterConfig) -> float:
    """Approximate vertical position of center of buoyancy [m]."""
    # For equal drafts on all columns this is a good approximation:
    # B roughly at -draft_mean/2
    drafts = [c.draft for c in config.columns]
    draft_mean = sum(drafts) / len(drafts)
    return -draft_mean / 2.0


def compute_zG(config: FloaterConfig) -> float:
    """Vertical CoG [m] from mass items (mass in tonnes)."""
    m_total = sum(m.mass for m in config.mass_items)  # [t]
    if m_total == 0.0:
        return 0.0
    zG = sum(m.mass * m.z for m in config.mass_items) / m_total
    return zG


def compute_pitch_BM(config: FloaterConfig, disp_volume: float) -> float:
    """
    Approximate BM for pitch/roll using ring-column approximation:
    I_wp ≈ sum( A_col * r^2 / 2 ), then BM = I_wp / ∇.
    """
    I_wp = 0.0
    for col in config.columns:
        A = math.pi * (col.diameter / 2.0)**2
        # For a ring of columns, pitch inertia about x or y is A*r^2/2
        I_wp += A * (col.radius**2) / 2.0
    BM = I_wp / disp_volume
    return BM


def heave_stiffness(config: FloaterConfig, Aw: float) -> float:
    """Heave hydrostatic stiffness C33 [N/m]."""
    return config.water_density * config.gravity * Aw


def pitch_stiffness(config: FloaterConfig, disp_volume: float, GM: float) -> float:
    """Pitch/roll hydrostatic stiffness [Nm/rad]."""
    return config.water_density * config.gravity * disp_volume * GM


def calibrate_heave_added_mass_ratio(config: FloaterConfig) -> float:
    """
    Calibrate heave added mass ratio (a33/m) from reference 15 MW case.
    Requires:
        ref_mass_total [kg],
        ref_C33 [N/m],
        ref_T_heave [s]
    """
    if config.ref_mass_total is None or config.ref_C33 is None or config.ref_T_heave is None:
        # Default fallback: assume a33/m ≈ 4
        return 4.0

    m = config.ref_mass_total
    C33 = config.ref_C33
    T = config.ref_T_heave

    # T = 2π * sqrt( (m + a33) / C33 )
    # => m + a33 = (T/(2π))^2 * C33
    m_eff = (T / (2.0 * math.pi))**2 * C33
    a33 = m_eff - m
    ratio = a33 / m
    return ratio


def scale_heave_added_mass_ratio(config: FloaterConfig, ref_ratio: float) -> float:
    """
    Scale heave added mass ratio from reference using plate area.
    a33_new/m_new ≈ ref_ratio * (B_new * L_new / (B_ref * L_ref))
    """
    if config.ref_plate_length is None or config.ref_plate_width is None:
        # No reference plate geometry: just use ref_ratio directly
        return ref_ratio

    # Reference plates (15 MW)
    A_ref = config.ref_plate_length * config.ref_plate_width * 3.0  # 3 plates

    # New plates
    plates = config.lower_plates
    A_new = plates.length * plates.width * plates.n_plates

    scale = A_new / A_ref
    return ref_ratio * scale


def heave_period(config: FloaterConfig,
                 disp_volume: float,
                 Aw: float) -> float:
    """
    Compute heave natural period [s], including added mass from lower plates.
    Uses calibration from 15 MW reference if provided.
    """
    m_struct = sum(m.mass for m in config.mass_items) * 1000.0  # [kg]
    C33 = heave_stiffness(config, Aw)

    # 1) calibrate ratio a33/m on reference
    ref_ratio = calibrate_heave_added_mass_ratio(config)

    # 2) scale with plate area
    ratio_new = scale_heave_added_mass_ratio(config, ref_ratio)

    m_eff = m_struct * (1.0 + ratio_new)

    T = 2.0 * math.pi * math.sqrt(m_eff / C33)
    return T


def pitch_period(config: FloaterConfig,
                 GM: float) -> float:
    """
    Compute pitch/roll natural period [s].
    Uses structural inertia about SWL with respect to a horizontal axis.
    """
    # Effective inertia: sum m_i z_i^2. Mass in tonnes.
    I_struct = 0.0  # [t·m2]
    for m in config.mass_items:
        I_struct += m.mass * (m.z**2)

    # Convert t·m2 to kg·m2
    I_struct *= 1000.0

    # Hydrostatic stiffness
    V = compute_displacement(config)
    C_theta = pitch_stiffness(config, V, GM)

    # We ignore rotational added inertia; plates contribute but are small
    I_eff = I_struct

    T = 2.0 * math.pi * math.sqrt(I_eff / C_theta)
    return T


def summarize_floater(config: FloaterConfig) -> None:
    """Compute and print main hydrostatic properties and eigenperiods."""
    V = compute_displacement(config)
    m_disp = V * config.water_density / 1000.0  # [t]
    Aw = compute_waterplane_area(config)
    zB = compute_zB(config)
    zG = compute_zG(config)
    BG = zG - zB
    BM = compute_pitch_BM(config, V)
    GM = BM - BG

    C33 = heave_stiffness(config, Aw)
    Ctheta = pitch_stiffness(config, V, GM)

    T_heave = heave_period(config, V, Aw)
    T_pitch = pitch_period(config, GM)

    print("=== Floater summary ===")
    print(f"Displacement volume   : {V:8.1f} m³")
    print(f"Displacement mass     : {m_disp:8.1f} t")
    print(f"Waterplane area       : {Aw:8.1f} m²")
    print(f"zB (CoB)              : {zB:8.2f} m")
    print(f"zG (CoG)              : {zG:8.2f} m")
    print(f"BG                    : {BG:8.2f} m")
    print(f"BM (pitch)            : {BM:8.2f} m")
    print(f"GM (pitch)            : {GM:8.2f} m")
    print(f"C33 (heave stiff.)    : {C33:8.3e} N/m")
    print(f"Cθ  (pitch stiff.)    : {Ctheta:8.3e} Nm/rad")
    print()
    print(f"Heave period T33      : {T_heave:6.2f} s")
    print(f"Pitch/Roll period Tθ  : {T_pitch:6.2f} s")
    print("=======================")


def main():
    # ---------------------------
    # Example: 24 MW, 6+1 layout
    # ---------------------------
    draft = 24.0
    freeboard = 12.0

    # Radii (you can tweak these)
    R_in = 50.0
    R_out = 84.0

    # Columns: 6 outer (2 per arm) + 1 center
    columns = []

    # 3 arms, 120° apart; for hydrostatics we only need radii, not angle,
    # so just define 3 inner + 3 outer with their radii:
    for _ in range(3):
        columns.append(Column(radius=R_in, diameter=9.0, draft=draft, freeboard=freeboard))
        columns.append(Column(radius=R_out, diameter=9.0, draft=draft, freeboard=freeboard))

    # Center column
    columns.append(Column(radius=0.0, diameter=10.0, draft=draft, freeboard=freeboard))

    # Lower plates for the 24 MW concept
    lower_plates = LowerPlates(
        n_plates=3,
        length=R_out,   # from center to outer edge
        width=14.5      # e.g. 14–15 m
    )

    # Mass items (tonnes, z in m)
    mass_items = [
        MassItem(mass=1170.0, z=80.0),    # tower
        MassItem(mass=1350.0, z=160.0),   # RNA
        # approx main steel for floater, CoG a bit below SWL
        MassItem(mass=5100.0, z=-5.0),
        # ballast, low in the columns
        MassItem(mass=4000.0, z=-20.0),
    ]

    # 15 MW reference for heave calibration (MOLO Y7)
    # These numbers are approximate – tune them if you want a more exact match.
    ref_disp_mass = 7975.0 * 1000.0  # kg
    # approximate 15 MW waterplane area (7 columns, 10.5 m OD):
    Aw_ref = 7.0 * math.pi * (10.5 / 2.0)**2
    C33_ref = RHO_W * G * Aw_ref
    T_heave_ref = 16.0  # s
    R_ref = 67.22
    B_ref = 14.0

    config = FloaterConfig(
        columns=columns,
        lower_plates=lower_plates,
        mass_items=mass_items,
        ref_mass_total=ref_disp_mass,
        ref_C33=C33_ref,
        ref_T_heave=T_heave_ref,
        ref_plate_length=R_ref,
        ref_plate_width=B_ref
    )

    summarize_floater(config)


if __name__ == "__main__":
    main()
