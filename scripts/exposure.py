"""Flood exposure analysis: Mount Albert, Mount Roskill and Sandringham.

Flags buildings that intersect the Auckland Council modelled flood plain,
then summarises exposure by suburb and by critical facility.
"""
from pathlib import Path

import geopandas as gpd

ROOT = Path(__file__).resolve().parent.parent
BUILDINGS = ROOT / "data" / "raw" / "nz-building-outlines.gpkg"
FLOOD = ROOT / "data" / "processed" / "flood_plains_fixed.gpkg"
PROCESSED = ROOT / "data" / "processed"
OUTPUTS = ROOT / "outputs"

SUBURBS = ["Mount Albert", "Mount Roskill", "Sandringham"]
CRITICAL_USES = ["School", "Hospital"]
CRS = 2193  # NZTM2000


def load_data():
    suburb_list = ", ".join(f"'{s}'" for s in SUBURBS)
    buildings = gpd.read_file(
        BUILDINGS,
        layer="nz_building_outlines",
        where=f"suburb_locality IN ({suburb_list})",
    )
    flood = gpd.read_file(FLOOD, layer="flood_plains_fixed")

    if buildings.crs.to_epsg() != CRS:
        buildings = buildings.to_crs(CRS)
    if flood.crs.to_epsg() != CRS:
        flood = flood.to_crs(CRS)
    return buildings, flood


def validate(gdf, name):
    invalid = (~gdf.is_valid).sum()
    empty = gdf.is_empty.sum()
    print(f"{name}: {len(gdf)} features, {invalid} invalid, {empty} empty")
    if invalid:
        gdf["geometry"] = gdf.geometry.make_valid()
        print(f"{name}: {(~gdf.is_valid).sum()} invalid after repair")
    return gdf


def flag_exposure(buildings, flood):
    joined = gpd.sjoin(buildings, flood[["geometry"]], how="inner", predicate="intersects")
    # A building touching two flood polygons appears twice in the join, so take unique indexes.
    buildings["exposed"] = buildings.index.isin(joined.index.unique()).astype(int)
    return buildings


def summarise_suburbs(buildings):
    suburbs = buildings.groupby("suburb_locality").agg(
        total=("exposed", "size"), exposed=("exposed", "sum")
    )
    suburbs["pct_exposed"] = (100 * suburbs["exposed"] / suburbs["total"]).round(1)
    return suburbs.sort_values("pct_exposed", ascending=False)


def summarise_critical(buildings):
    critical = buildings[(buildings["exposed"] == 1) & buildings["use"].isin(CRITICAL_USES)]
    return (
        critical.groupby(["name", "use"])
        .size()
        .rename("buildings")
        .sort_values(ascending=False)
    )


def main():
    buildings, flood = load_data()
    buildings = validate(buildings, "Buildings")
    flood = validate(flood, "Flood plains")

    buildings = flag_exposure(buildings, flood)
    total, exposed = len(buildings), buildings["exposed"].sum()
    print(f"\nExposed: {exposed} of {total} buildings ({100 * exposed / total:.1f}%)")

    print("\nBuilding uses in study area:")
    print(buildings["use"].value_counts(dropna=False))

    suburbs = summarise_suburbs(buildings)
    critical = summarise_critical(buildings)
    print(f"\n{critical.sum()} critical buildings at {len(critical)} facilities")
    print(critical)
    print("\nExposure by suburb:")
    print(suburbs)

    PROCESSED.mkdir(parents=True, exist_ok=True)
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    buildings.to_file(PROCESSED / "buildings_with_exposure.gpkg", driver="GPKG")
    suburbs.to_csv(OUTPUTS / "exposure_by_suburb.csv")
    critical.to_csv(OUTPUTS / "critical_exposed.csv")
    print(f"\nOutputs written to {OUTPUTS}")
    buildings.drop(columns="geometry").to_csv(OUTPUTS / "buildings_with_exposure.csv", index=False)


if __name__ == "__main__":
    main()