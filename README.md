# Flood Exposure Analysis — Central Auckland

Which buildings and schools in Mount Albert, Mount Roskill and Sandringham
sit within Auckland Council's modelled flood plain?

## Key findings
- 3,284 of 22,772 buildings (14.4%) intersect the modelled flood plain.
- Sandringham is the most exposed suburb at 28.0%, more than double
  Mount Roskill (11.6%) and Mount Albert (10.7%).
- 40 buildings across 8 schools are exposed; Mt Roskill Grammar is the
  most affected with 20 buildings. No hospitals are located in the study area.

## Data
- NZ Building Outlines, LINZ Data Service (layer 101290), downloaded [date], EPSG:2193
- Flood Plains, Auckland Council open data, downloaded [date]

Data files are not included in this repository. Download them into `data/raw/`.

## Method
1. Validate both layers; 26 invalid flood polygons (ring self-intersections) repaired.
2. Filter buildings to the three suburbs.
3. Flag buildings intersecting any flood plain polygon.
4. Summarise by suburb and by critical facility.

Results were produced in QGIS and reproduced independently in Python.

## Limitations
- Intersect predicate: any overlap counts as exposed, including buildings
  that only touch the edge of a flood area.
- 98.8% of buildings have no recorded use, so critical facilities are
  limited to the types LINZ classifies (schools, hospitals, supermarkets).
- Results reflect a single modelled flood scenario.

## How to run
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python scripts/exposure.py