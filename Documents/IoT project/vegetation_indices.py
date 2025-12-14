"""
Vegetation Indices Calculator
Calculates NDVI, NDWI, and EVI from multispectral orthomosaic
"""
import rasterio
import numpy as np
from rasterio.transform import from_bounds
import os

def calculate_vegetation_indices(input_tif, output_dir=None):
    """
    Calculate NDVI, NDWI, and EVI from a multispectral orthomosaic.
    
    Assumes band order: Red, Green, Blue, NIR (or similar)
    Adjust band indices based on your specific orthomosaic.
    
    Parameters:
    -----------
    input_tif : str
        Path to input orthomosaic GeoTIFF
    output_dir : str, optional
        Directory to save output indices (default: same as input)
    
    Returns:
    --------
    dict : Paths to generated index files
    """
    if output_dir is None:
        output_dir = os.path.dirname(input_tif)
    
    print(f"📂 Opening orthomosaic: {input_tif}")
    
    with rasterio.open(input_tif) as src:
        # Read metadata
        meta = src.meta.copy()
        meta.update(count=1, dtype='float32', compress='lzw')
        
        print(f"   Bands: {src.count}")
        print(f"   Size: {src.width} x {src.height}")
        print(f"   CRS: {src.crs}")
        
        # Determine band indices (adjust based on your data)
        # Common orders: RGB-NIR or Blue-Green-Red-NIR-RedEdge
        if src.count >= 4:
            # Assuming: Band 1=Red, Band 2=Green, Band 3=Blue, Band 4=NIR
            red_idx, green_idx, blue_idx, nir_idx = 1, 2, 3, 4
        else:
            raise ValueError(f"Expected at least 4 bands, got {src.count}")
        
        print(f"\n🔍 Reading bands...")
        print(f"   Red: Band {red_idx}")
        print(f"   Green: Band {green_idx}")
        print(f"   Blue: Band {blue_idx}")
        print(f"   NIR: Band {nir_idx}")
        
        # Read bands as float32 to avoid overflow
        red = src.read(red_idx).astype('float32')
        green = src.read(green_idx).astype('float32')
        blue = src.read(blue_idx).astype('float32')
        nir = src.read(nir_idx).astype('float32')
        
        # Calculate NDVI: (NIR - Red) / (NIR + Red)
        print("\n🌿 Calculating NDVI...")
        ndvi = np.where(
            (nir + red) != 0,
            (nir - red) / (nir + red),
            0
        )
        ndvi = np.clip(ndvi, -1, 1)  # Clip to valid range
        
        # Calculate NDWI: (Green - NIR) / (Green + NIR)
        print("💧 Calculating NDWI...")
        ndwi = np.where(
            (green + nir) != 0,
            (green - nir) / (green + nir),
            0
        )
        ndwi = np.clip(ndwi, -1, 1)
        
        # Calculate EVI: 2.5 * ((NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1))
        print("🌾 Calculating EVI...")
        evi_denominator = nir + 6 * red - 7.5 * blue + 1
        evi = np.where(
            evi_denominator != 0,
            2.5 * ((nir - red) / evi_denominator),
            0
        )
        evi = np.clip(evi, -1, 1)
        
        # Save indices
        output_paths = {}
        
        # Save NDVI
        ndvi_path = os.path.join(output_dir, "ndvi.tif")
        print(f"\n💾 Saving NDVI to: {ndvi_path}")
        with rasterio.open(ndvi_path, 'w', **meta) as dst:
            dst.write(ndvi, 1)
        output_paths['ndvi'] = ndvi_path
        
        # Save NDWI
        ndwi_path = os.path.join(output_dir, "ndwi.tif")
        print(f"💾 Saving NDWI to: {ndwi_path}")
        with rasterio.open(ndwi_path, 'w', **meta) as dst:
            dst.write(ndwi, 1)
        output_paths['ndwi'] = ndwi_path
        
        # Save EVI
        evi_path = os.path.join(output_dir, "evi.tif")
        print(f"💾 Saving EVI to: {evi_path}")
        with rasterio.open(evi_path, 'w', **meta) as dst:
            dst.write(evi, 1)
        output_paths['evi'] = evi_path
        
        print("\n✅ Vegetation indices calculated successfully!")
        print(f"   NDVI range: {np.nanmin(ndvi):.3f} to {np.nanmax(ndvi):.3f}")
        print(f"   NDWI range: {np.nanmin(ndwi):.3f} to {np.nanmax(ndwi):.3f}")
        print(f"   EVI range: {np.nanmin(evi):.3f} to {np.nanmax(evi):.3f}")
        
        return output_paths

if __name__ == "__main__":
    # Input orthomosaic
    input_file = "p17 NARC MERGED ALL BANDS.tif"
    
    if os.path.exists(input_file):
        calculate_vegetation_indices(input_file)
    else:
        print(f"❌ Error: File not found: {input_file}")
        print("Please ensure the orthomosaic is in the current directory.")
