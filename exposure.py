import geopandas as gpd
import pyogrio
BUILDINGS = "../data/raw/nz-building-outlines.gpkg"   # use your actual filename
FLOOD = "../data/processed/flood_plains_fixed.gpkg"
print(pyogrio.list_layers(BUILDINGS))
print(pyogrio.list_layers(FLOOD))
SUBURBS = ["Mount Albert", "Mount Roskill", "Sandringham"]
where = "suburb_locality IN ('Mount Albert', 'Mount Roskill', 'Sandringham')"

buildings = gpd.read_file(BUILDINGS, layer="nz_building_outlines", where=where)
flood = gpd.read_file(FLOOD, layer="flood_plains_fixed")

print(buildings)
print(len(buildings), buildings.crs)
print(len(flood), flood.crs)
print("Invalid:", (~flood.is_valid).sum())
print("Empty:", flood.is_empty.sum())

flood["geometry"] = flood.geometry.make_valid()
print("Invalid after fix:", (~flood.is_valid).sum())
joined = gpd.sjoin(buildings, flood[["geometry"]], how="inner", predicate="intersects")
exposed_idx = joined.index.unique()
buildings["exposed"] = buildings.index.isin(exposed_idx).astype(int)

print("Exposed:", buildings["exposed"].sum())
print(buildings["use"].value_counts(dropna=False))   # hospitals check: does 'Hospital' appear at all?

critical = buildings[(buildings["exposed"] == 1) & (buildings["use"].isin(["School", "Hospital"]))]
schools = critical.groupby(["name", "use"]).size().sort_values(ascending=False)
print(len(critical), "buildings at", len(schools), "facilities")
print(schools)

suburbs = buildings.groupby("suburb_locality").agg(total=("exposed", "size"), exposed=("exposed", "sum"))
suburbs["pct_exposed"] = (100 * suburbs["exposed"] / suburbs["total"]).round(1)
print(suburbs.sort_values("pct_exposed", ascending=False))
buildings.to_file("../data/processed/buildings_with_exposure.gpkg", driver="GPKG")
suburbs.to_csv("../../outputs/exposure_by_suburb.csv")
schools.to_csv("../../outputs/schools_exposed.csv", header=["buildings"])