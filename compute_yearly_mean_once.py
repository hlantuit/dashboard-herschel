
"""
ONE-OFF SCRIPT — run this once (locally, or as a one-time GitHub Actions
manual run) to compute the water level yearly mean for Herschel Island.
 
This value barely changes year to year, so rather than recomputing it on
every dashboard run, it's computed once here and the printed result is
hardcoded as a constant directly in dashboard_update.py.
 
VERSION 2 — much leaner than the first attempt, which hung for 55+
minutes and never finished. Two real changes, both justified by prior
dashboard runs' own logs:
 
1. Skips the 34x34 spatial neighborhood search entirely. The dashboard's
   own diagnostic logs have repeatedly shown the SINGLE nearest grid
   point to Herschel Island has valid (non-NaN) data — every successful
   run printed "using grid cell at distance 0m from Herschel Island".
   Querying one point instead of a 34x34 neighborhood cuts the data
   pulled by roughly 1,156x.
 
2. Samples roughly one value per day across the year (using a coarse
   time-step slice) instead of the full 15-minute resolution. A yearly
   MEAN doesn't need 35,000 individual readings to be accurate — daily
   sampling gives a statistically near-identical result from a dataset
   ~96x smaller. Together, these two changes should reduce the actual
   data transferred by roughly 100,000x compared to the first attempt.
 
Usage:
    pip install xarray netCDF4 numpy --break-system-packages
    python3 compute_yearly_mean_once.py
 
Then copy the printed mean value into dashboard_update.py's
WATER_LEVEL_YEARLY_MEAN constant.
"""
import math
from datetime import datetime, timedelta
 
import numpy as np
import xarray as xr
 
LAT = 69.590
LON = -139.099
THREDDS_URL = "https://thredds.met.no/thredds/dodsC/cmems/topaz6/dataset-topaz6-arc-15min-3km-be.ncml"
UNIT_SCALE = 100_000  # this file's x/y coordinates are in units of 100km, not plain meters — confirmed earlier
 
 
def latlon_to_3413(lat_deg, lon_deg):
    """Standard EPSG:3413 polar stereographic forward projection (WGS84)."""
    a = 6378137.0
    f = 1 / 298.257223563
    e2 = 2 * f - f ** 2
    e = math.sqrt(e2)
    lat_ts = math.radians(70)
    lon0 = math.radians(-45)
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    t_c = math.tan(math.pi / 4 - lat_ts / 2) / (((1 - e * math.sin(lat_ts)) / (1 + e * math.sin(lat_ts))) ** (e / 2))
    m_c = math.cos(lat_ts) / math.sqrt(1 - e2 * math.sin(lat_ts) ** 2)
    t = math.tan(math.pi / 4 - lat / 2) / (((1 - e * math.sin(lat)) / (1 + e * math.sin(lat))) ** (e / 2))
    rho = a * m_c * (t / t_c)
    x = rho * math.sin(lon - lon0)
    y = -rho * math.cos(lon - lon0)
    return x, y
 
 
def main():
    print("Opening dataset (this can take a while)...")
    ds = xr.open_dataset(THREDDS_URL)
 
    target_x_m, target_y_m = latlon_to_3413(LAT, LON)
    target_x = target_x_m / UNIT_SCALE
    target_y = target_y_m / UNIT_SCALE
 
    print(f"Target point (native units): x={target_x:.3f}, y={target_y:.3f}")
    print("Selecting the single nearest grid point directly (no neighborhood search) "
          "— prior dashboard runs have repeatedly confirmed this exact point has valid data...")
 
    point_series = ds["zos"].sel(x=target_x, y=target_y, method="nearest")
 
    now = datetime.utcnow()
    year_start = now - timedelta(days=365)
 
    print("Slicing to the past 365 days at this single point...")
    point_year = point_series.sel(time=slice(year_start, now))
 
    # Sample roughly daily (every 96th step, since the data is 15-minute
    # resolution = 96 steps/day) rather than pulling all ~35,000 readings
    # — a yearly mean from ~365 samples is statistically almost identical
    # to one from 35,000, at a tiny fraction of the data transfer cost.
    print("Sampling roughly once per day (not full 15-minute resolution)...")
    point_daily = point_year.isel(time=slice(None, None, 96))
 
    print("Downloading the sampled values (this is the real network step)...")
    values = point_daily.values.flatten()
    valid_values = values[~np.isnan(values)]
 
    if len(valid_values) == 0:
        print("ERROR: no valid values found — the nearest point may not have data after all.")
        print("If this happens, the spatial-neighborhood search from the original version")
        print("may genuinely be necessary; consider running that version with a much longer")
        print("timeout (e.g. several hours) instead, or trying a different time-of-day to run it.")
        return
 
    yearly_mean = float(np.mean(valid_values))
 
    print("\n" + "=" * 60)
    print(f"RESULT: yearly mean water level = {yearly_mean:.4f} m")
    print(f"(computed from {len(valid_values)} daily-sampled readings)")
    print(f"Computed at: {now.isoformat()} UTC")
    print("=" * 60)
    print("\nCopy this into dashboard_update.py:")
    print(f'WATER_LEVEL_YEARLY_MEAN = {yearly_mean:.4f}  # computed {now.strftime("%Y-%m-%d")} via compute_yearly_mean_once.py')
 
 
if __name__ == "__main__":
    main()
