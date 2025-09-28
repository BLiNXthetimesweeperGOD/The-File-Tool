import struct
from typing import List, Tuple, Union, Optional


class DXTDecompressor:
    """Main class for DXT texture decompression."""
    
    @staticmethod
    def _unpack_565(color: int) -> Tuple[int, int, int]:
        """Unpack RGB565 color to RGB888."""
        r = (color >> 11) & 0x1F
        g = (color >> 5) & 0x3F
        b = color & 0x1F
        
        # Scale to 8-bit values
        r = (r << 3) | (r >> 2)
        g = (g << 2) | (g >> 4)
        b = (b << 3) | (b >> 2)
        
        return r, g, b
    
    @staticmethod
    def _interpolate_colors(c0: Tuple[int, int, int], c1: Tuple[int, int, int], 
                          factor: float) -> Tuple[int, int, int]:
        """Interpolate between two RGB colors."""
        r = int(c0[0] * (1 - factor) + c1[0] * factor)
        g = int(c0[1] * (1 - factor) + c1[1] * factor)
        b = int(c0[2] * (1 - factor) + c1[2] * factor)
        return r, g, b
    
    @staticmethod
    def _decompress_dxt1_block(block_data: bytes) -> List[List[Tuple[int, int, int, int]]]:
        """
        Decompress a single 8-byte DXT1 block to a 4x4 RGBA pixel array.
        
        Args:
            block_data: 8 bytes of DXT1 compressed data
            
        Returns:
            4x4 array of RGBA tuples (values 0-255)
        """
        if len(block_data) != 8:
            raise ValueError("DXT1 block must be exactly 8 bytes")
        
        # Unpack the block
        color0, color1, indices = struct.unpack('<HHI', block_data)
        
        # Decode colors
        c0 = DXTDecompressor._unpack_565(color0)
        c1 = DXTDecompressor._unpack_565(color1)
        
        # Generate color palette
        colors = [c0, c1]
        
        if color0 > color1:
            # Opaque mode - 4 colors, no transparency
            colors.append(DXTDecompressor._interpolate_colors(c0, c1, 1/3))
            colors.append(DXTDecompressor._interpolate_colors(c0, c1, 2/3))
            alphas = [255, 255, 255, 255]
        else:
            # Transparent mode - 3 colors + transparent
            colors.append(DXTDecompressor._interpolate_colors(c0, c1, 0.5))
            colors.append((0, 0, 0))  # Transparent black
            alphas = [255, 255, 255, 0]
        
        # Decode pixel indices and build result
        result = []
        for y in range(4):
            row = []
            for x in range(4):
                bit_offset = (y * 4 + x) * 2
                color_index = (indices >> bit_offset) & 0x3
                r, g, b = colors[color_index]
                a = alphas[color_index]
                row.append((r, g, b, a))
            result.append(row)
        
        return result
    
    @staticmethod
    def _decompress_dxt3_block(block_data: bytes) -> List[List[Tuple[int, int, int, int]]]:
        """
        Decompress a single 16-byte DXT3 block to a 4x4 RGBA pixel array.
        
        Args:
            block_data: 16 bytes of DXT3 compressed data
            
        Returns:
            4x4 array of RGBA tuples (values 0-255)
        """
        if len(block_data) != 16:
            raise ValueError("DXT3 block must be exactly 16 bytes")
        
        # Split alpha and color data
        alpha_data = block_data[:8]
        color_data = block_data[8:]
        
        # Decode alpha values (4 bits per pixel)
        alpha_values = []
        for i in range(8):
            byte_val = alpha_data[i]
            alpha_values.append((byte_val & 0xF) * 17)  # Scale 4-bit to 8-bit
            alpha_values.append(((byte_val >> 4) & 0xF) * 17)
        
        # Decompress color data (same as DXT1 but always opaque mode)
        color0, color1, indices = struct.unpack('<HHI', color_data)
        c0 = DXTDecompressor._unpack_565(color0)
        c1 = DXTDecompressor._unpack_565(color1)
        
        colors = [
            c0,
            c1,
            DXTDecompressor._interpolate_colors(c0, c1, 1/3),
            DXTDecompressor._interpolate_colors(c0, c1, 2/3)
        ]
        
        # Build result combining color and alpha
        result = []
        for y in range(4):
            row = []
            for x in range(4):
                pixel_index = y * 4 + x
                bit_offset = pixel_index * 2
                color_index = (indices >> bit_offset) & 0x3
                r, g, b = colors[color_index]
                a = alpha_values[pixel_index]
                row.append((r, g, b, a))
            result.append(row)
        
        return result
    
    @staticmethod
    def _decompress_dxt5_block(block_data: bytes) -> List[List[Tuple[int, int, int, int]]]:
        """
        Decompress a single 16-byte DXT5 block to a 4x4 RGBA pixel array.
        
        Args:
            block_data: 16 bytes of DXT5 compressed data
            
        Returns:
            4x4 array of RGBA tuples (values 0-255)
        """
        if len(block_data) != 16:
            raise ValueError("DXT5 block must be exactly 16 bytes")
        
        # Split alpha and color data
        alpha_data = block_data[:8]
        color_data = block_data[8:]
        
        # Decode alpha interpolation
        alpha0, alpha1 = struct.unpack('<BB', alpha_data[:2])
        alpha_indices_packed = struct.unpack('<Q', alpha_data)[0] >> 16
        
        # Generate alpha palette
        alphas = [alpha0, alpha1]
        if alpha0 > alpha1:
            # 8 alpha values
            for i in range(1, 7):
                alphas.append(int(alpha0 * (7-i)/7 + alpha1 * i/7))
        else:
            # 6 alpha values + transparent/opaque
            for i in range(1, 5):
                alphas.append(int(alpha0 * (5-i)/5 + alpha1 * i/5))
            alphas.extend([0, 255])
        
        # Decode alpha indices (3 bits per pixel)
        alpha_values = []
        for i in range(16):
            bit_offset = i * 3
            alpha_index = (alpha_indices_packed >> bit_offset) & 0x7
            alpha_values.append(alphas[alpha_index])
        
        # Decompress color data (same as DXT1/DXT3)
        color0, color1, indices = struct.unpack('<HHI', color_data)
        c0 = DXTDecompressor._unpack_565(color0)
        c1 = DXTDecompressor._unpack_565(color1)
        
        colors = [
            c0,
            c1,
            DXTDecompressor._interpolate_colors(c0, c1, 1/3),
            DXTDecompressor._interpolate_colors(c0, c1, 2/3)
        ]
        
        # Build result
        result = []
        for y in range(4):
            row = []
            for x in range(4):
                pixel_index = y * 4 + x
                bit_offset = pixel_index * 2
                color_index = (indices >> bit_offset) & 0x3
                r, g, b = colors[color_index]
                a = alpha_values[pixel_index]
                row.append((r, g, b, a))
            result.append(row)
        
        return result
    
    @classmethod
    def decompress_dxt1(cls, data: bytes, width: int, height: int) -> List[List[Tuple[int, int, int, int]]]:
        """
        Decompress DXT1 compressed texture data.
        
        Args:
            data: DXT1 compressed data
            width: Texture width in pixels
            height: Texture height in pixels
            
        Returns:
            2D array of RGBA tuples representing the decompressed image
        """
        if width % 4 != 0 or height % 4 != 0:
            raise ValueError("DXT1 textures must have dimensions divisible by 4")
        
        blocks_x = width // 4
        blocks_y = height // 4
        expected_size = blocks_x * blocks_y * 8
        
        if len(data) != expected_size:
            raise ValueError(f"Expected {expected_size} bytes for {width}x{height} DXT1 texture, got {len(data)}")
        
        result = []
        for block_y in range(blocks_y):
            # Initialize 4 rows for this block row
            block_rows = [[] for _ in range(4)]
            
            for block_x in range(blocks_x):
                block_offset = (block_y * blocks_x + block_x) * 8
                block_data = data[block_offset:block_offset + 8]
                decompressed_block = cls._decompress_dxt1_block(block_data)
                
                # Add block pixels to the appropriate rows
                for row_in_block in range(4):
                    block_rows[row_in_block].extend(decompressed_block[row_in_block])
            
            result.extend(block_rows)
        
        return result
    
    @classmethod
    def decompress_dxt3(cls, data: bytes, width: int, height: int) -> List[List[Tuple[int, int, int, int]]]:
        """
        Decompress DXT3 compressed texture data.
        
        Args:
            data: DXT3 compressed data
            width: Texture width in pixels
            height: Texture height in pixels
            
        Returns:
            2D array of RGBA tuples representing the decompressed image
        """
        if width % 4 != 0 or height % 4 != 0:
            raise ValueError("DXT3 textures must have dimensions divisible by 4")
        
        blocks_x = width // 4
        blocks_y = height // 4
        expected_size = blocks_x * blocks_y * 16
        
        if len(data) != expected_size:
            raise ValueError(f"Expected {expected_size} bytes for {width}x{height} DXT3 texture, got {len(data)}")
        
        result = []
        for block_y in range(blocks_y):
            block_rows = [[] for _ in range(4)]
            
            for block_x in range(blocks_x):
                block_offset = (block_y * blocks_x + block_x) * 16
                block_data = data[block_offset:block_offset + 16]
                decompressed_block = cls._decompress_dxt3_block(block_data)
                
                for row_in_block in range(4):
                    block_rows[row_in_block].extend(decompressed_block[row_in_block])
            
            result.extend(block_rows)
        
        return result
    
    @classmethod
    def decompress_dxt5(cls, data: bytes, width: int, height: int) -> List[List[Tuple[int, int, int, int]]]:
        """
        Decompress DXT5 compressed texture data.
        
        Args:
            data: DXT5 compressed data
            width: Texture width in pixels
            height: Texture height in pixels
            
        Returns:
            2D array of RGBA tuples representing the decompressed image
        """
        if width % 4 != 0 or height % 4 != 0:
            raise ValueError("DXT5 textures must have dimensions divisible by 4")
        
        blocks_x = width // 4
        blocks_y = height // 4
        expected_size = blocks_x * blocks_y * 16
        
        if len(data) != expected_size:
            raise ValueError(f"Expected {expected_size} bytes for {width}x{height} DXT5 texture, got {len(data)}")
        
        result = []
        for block_y in range(blocks_y):
            block_rows = [[] for _ in range(4)]
            
            for block_x in range(blocks_x):
                block_offset = (block_y * blocks_x + block_x) * 16
                block_data = data[block_offset:block_offset + 16]
                decompressed_block = cls._decompress_dxt5_block(block_data)
                
                for row_in_block in range(4):
                    block_rows[row_in_block].extend(decompressed_block[row_in_block])
            
            result.extend(block_rows)
        
        return result


# Convenience functions for easier usage
def decompressDxt1(data: bytes, width: int, height: int) -> List[List[Tuple[int, int, int, int]]]:
    """Convenience function to decompress DXT1 data."""
    return DXTDecompressor.decompress_dxt1(data, width, height)


def decompressDxt3(data: bytes, width: int, height: int) -> List[List[Tuple[int, int, int, int]]]:
    """Convenience function to decompress DXT3 data."""
    return DXTDecompressor.decompress_dxt3(data, width, height)


def decompressDxt5(data: bytes, width: int, height: int) -> List[List[Tuple[int, int, int, int]]]:
    """Convenience function to decompress DXT5 data."""
    return DXTDecompressor.decompress_dxt5(data, width, height)


def pixelsToBytes(pixels: List[List[Tuple[int, int, int, int]]], format: str = 'RGBA') -> bytes:
    """
    Convert pixel array to raw bytes.
    
    Args:
        pixels: 2D array of RGBA tuples
        format: Output format ('RGBA', 'RGB', 'BGRA', 'BGR')
        
    Returns:
        Raw pixel data as bytes
    """
    result = bytearray()
    
    for row in pixels:
        for r, g, b, a in row:
            if format == 'RGBA':
                result.extend([r, g, b, a])
            elif format == 'RGB':
                result.extend([r, g, b])
            elif format == 'BGRA':
                result.extend([b, g, r, a])
            elif format == 'BGR':
                result.extend([b, g, r])
            else:
                raise ValueError(f"Unsupported format: {format}")
    
    return bytes(result)


# Example usage
if __name__ == "__main__":
    # Example of how to use the library
    
    # For DXT1 (8 bytes per 4x4 block)
    # dxt1_data = b'...'  # Your DXT1 compressed data
    # width, height = 64, 64  # Texture dimensions
    # pixels = decompress_dxt1(dxt1_data, width, height)
    
    # For DXT3 (16 bytes per 4x4 block)
    # dxt3_data = b'...'  # Your DXT3 compressed data
    # pixels = decompress_dxt3(dxt3_data, width, height)
    
    # For DXT5 (16 bytes per 4x4 block)
    # dxt5_data = b'...'  # Your DXT5 compressed data
    # pixels = decompress_dxt5(dxt5_data, width, height)
    
    # Convert to raw bytes for use with PIL or other libraries
    # rgba_bytes = pixels_to_bytes(pixels, 'RGBA')
    
    # Example with PIL (if you have Pillow installed):
    # from PIL import Image
    # img = Image.frombytes('RGBA', (width, height), rgba_bytes)
    # img.save('output.png')
    
    print("DXT Decompression Library loaded successfully!")
    print("Use decompress_dxt1(), decompress_dxt3(), or decompress_dxt5() to decompress texture data.")
