from pathlib import Path

medical_images_dir = '.'
search_dirs = [Path(medical_images_dir), Path(medical_images_dir) / 'visualization']

found_paths = []
print(f"Searching in: {[str(d) for d in search_dirs]}")
for d in search_dirs:
    if d.exists():
        print(f"Directory {d} exists.")
        pngs = list(d.glob('*.png'))
        jpgs = list(d.glob('*.jpg'))
        print(f"  Found {len(pngs)} PNGs and {len(jpgs)} JPGs in {d}")
        found_paths.extend(pngs)
        found_paths.extend(jpgs)
    else:
        print(f"Directory {d} DOES NOT exist.")

unique_paths = list(set(found_paths))
unique_paths.sort(key=lambda x: x.name)

print(f"\nTotal unique images found: {len(unique_paths)}")
for p in unique_paths:
    print(f"  - {p} (Type: {type(p)})")
