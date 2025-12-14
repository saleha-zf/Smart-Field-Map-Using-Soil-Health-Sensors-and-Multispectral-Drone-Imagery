"""
Cloud Optimized GeoTIFF (COG) Converter
Converts large GeoTIFF files to COG format for efficient web visualization
"""
import rasterio
from rasterio.shutil import copy
from rasterio.enums import Resampling
import os

def create_cog(input_path, output_path=None, tile_size=512, compression='DEFLATE'):
    """
    Convert a GeoTIFF to Cloud Optimized GeoTIFF (COG) format.
    
    Parameters:
    -----------
    input_path : str
        Path to input GeoTIFF
    output_path : str, optional
        Path for output COG (default: adds '_cog' suffix)
    tile_size : int
        Internal tile size (256 or 512 recommended)
    compression : str
        Compression method ('DEFLATE', 'LZW', 'JPEG', etc.)
    
    Returns:
    --------
    str : Path to created COG file
    """
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_cog{ext}"
    
    print(f"🔄 Converting to Cloud Optimized GeoTIFF...")
    print(f"   Input: {input_path}")
    print(f"   Output: {output_path}")
    
    # COG creation options
    cog_profile = {
        'driver': 'GTiff',
        'tiled': True,
        'blockxsize': tile_size,
        'blockysize': tile_size,
        'compress': compression,
        'COPY_SRC_OVERVIEWS': 'YES',
        'TILED': 'YES',
    }
    
    with rasterio.open(input_path) as src:
        profile = src.profile.copy()
        profile.update(cog_profile)
        
        print(f"\n📊 Source info:")
        print(f"   Bands: {src.count}")
        print(f"   Size: {src.width} x {src.height}")
        print(f"   Data type: {src.dtypes[0]}")
        
        # Calculate overview levels
        max_dim = max(src.width, src.height)
        overview_levels = []
        level = 2
        while max_dim / level > tile_size:
            overview_levels.append(level)
            level *= 2
        
        print(f"\n🔍 Creating overviews at levels: {overview_levels}")
        
        # Copy with COG profile
        with rasterio.open(output_path, 'w', **profile) as dst:
            for band_idx in range(1, src.count + 1):
                data = src.read(band_idx)
                dst.write(data, band_idx)
            
            # Build overviews
            if overview_levels:
                dst.build_overviews(overview_levels, Resampling.average)
                dst.update_tags(ns='rio_overview', resampling='average')
        
        # Validate COG
        print("\n✅ COG created successfully!")
        
        # Get file sizes
        input_size = os.path.getsize(input_path) / (1024**3)  # GB
        output_size = os.path.getsize(output_path) / (1024**3)  # GB
        
        print(f"\n📦 File sizes:")
        print(f"   Original: {input_size:.2f} GB")
        print(f"   COG: {output_size:.2f} GB")
        print(f"   Compression ratio: {(1 - output_size/input_size)*100:.1f}%")
        
        return output_path

if __name__ == "__main__":
    input_file = "p17 NARC MERGED ALL BANDS.tif"
    
    if os.path.exists(input_file):
        print("⚠️  WARNING: This will create a large file (~3GB)")
        print("    Processing may take several minutes...\n")
        create_cog(input_file)
    else:
        print(f"❌ Error: File not found: {input_file}")
