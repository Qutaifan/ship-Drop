# Image Download Guide — Phase 1 Candidates

## Target Directory Structure

```
fixtures/images/
├── candidate-us-2026-09-01-magnetic-cable-organizer/
│   ├── main-1.jpg
│   ├── main-2.jpg
│   ├── lifestyle-1.jpg
│   ├── detail-1.jpg
│   └── package-1.jpg
└── candidate-us-2026-09-01-foldable-silicone-bowl/
    ├── main-1.jpg
    ├── main-2.jpg
    ├── lifestyle-1.jpg
    ├── detail-1.jpg
    └── package-1.jpg
```

---

## Source URLs to Visit

### Magnetic Cable Organizer (6-Pack)

| # | Retailer | URL | Suggested Filename |
|---|---|---|---|
| 1 | Home Depot (Lukyamzn) | https://www.homedepot.com/p/Lukyamzn-Magnetic-Cord-Organizers-Cable-Clips-and-Straps-Silicone-Twist-Ties-Colorful-Headphone-Keeper-Holder-6-Pack-PH03327B189/336729507 | `main-1.jpg` |
| 2 | Home Depot (Yichuhaoxi) | https://www.homedepot.com/p/Yichuhaoxi-Magnetic-Cable-Clips-Silicon-Cable-Ties-in-White-6-Pack-Desk-Organizer-Cord-Holder-Adhesive-Home-Cable-Keeper-M505PH527F271/336133759 | `main-2.jpg` |
| 3 | Walmart (WZXPWT) | https://www.walmart.com/ip/WZXPWT-6-Pack-Magnetic-Cable-Organizer-Desktop-Wall-Mounted-Cable-Storage-Punch-Free-Headphone-Data-Cable-Holder-Minimalist-Cord-Management-Solution/19390606458 | `lifestyle-1.jpg` |
| 4 | Amazon (JOYROOM) | https://www.amazon.com/Adjustable-Management-JOYROOM-Organizer-Nightstand/dp/B0CH159ZNT | `detail-1.jpg` |
| 5 | eBay | https://www.ebay.com/itm/336009605571 | `package-1.jpg` |

### Foldable Silicone Bowl (4-Pack)

| # | Retailer | URL | Suggested Filename |
|---|---|---|---|
| 1 | Amazon (Potchen) | https://www.amazon.com/Potchen-Collapsible-Expandable-Containers-Resistant/dp/B0D3PJPGD2 | `main-1.jpg` |
| 2 | Amazon (AIMUZIKEER) | https://www.amazon.com/AIMUZIKEER-Collapsible-Organization-Accessories-Decorations/dp/B0FVM98Z6V | `main-2.jpg` |
| 3 | Walmart (Topekada) | https://www.walmart.com/ip/Topekada-4-Pack-Silicone-Collapsible-Bowls-Airtight-Lids-BPA-Free-Silicone-Food-Storage-Containers-Airtight-Lids-Microwave-Freezer-Foldable-Lunch-Box/18635760953 | `lifestyle-1.jpg` |
| 4 | Walmart (Multi-capacity) | https://www.walmart.com/ip/4-Pack-Collapsible-Silicone-Bowls-Lids-350-500-800-1200ML-Nestable-Leakproof-Food-Storage-Containers-Microwave-Freezer-Dishwasher-Safe-Camping-RV-Kit/20655073806 | `detail-1.jpg` |
| 5 | Amazon (Guyuyii) | https://www.amazon.com/clp/B07XL3LPPC | `package-1.jpg` |

---

## Quick Manual Steps

1. **Create directories:**
   ```bash
   mkdir -p fixtures/images/candidate-us-2026-09-01-magnetic-cable-organizer
   mkdir -p fixtures/images/candidate-us-2026-09-01-foldable-silicone-bowl
   ```

2. **For each URL above:**
   - Open in browser
   - Right-click main product image → "Save image as..."
   - Save to the appropriate folder with suggested filename
   - Repeat for 3–5 images per product (main, lifestyle, detail, package)

3. **Verify:**
   ```bash
   ls -la fixtures/images/candidate-us-2026-09-01-magnetic-cable-organizer/
   ls -la fixtures/images/candidate-us-2026-09-01-foldable-silicone-bowl/
   ```

---

## Update Candidate Files

After downloading, update the candidate markdown files to reference the images:

```markdown
## Product Images

| Type | Path |
|---|---|
| Main | `fixtures/images/candidate-us-2026-09-01-magnetic-cable-organizer/main-1.jpg` |
| Lifestyle | `fixtures/images/candidate-us-2026-09-01-magnetic-cable-organizer/lifestyle-1.jpg` |
| Detail | `fixtures/images/candidate-us-2026-09-01-magnetic-cable-organizer/detail-1.jpg` |
| Package | `fixtures/images/candidate-us-2026-09-01-magnetic-cable-organizer/package-1.jpg` |
```

---

## Automation Script (Optional)

If you prefer a script, save this as `scripts/download_candidate_images.py` and run with your own downloaded URLs:

```python
#!/usr/bin/env python3
"""Helper to organize downloaded candidate images."""
import shutil
from pathlib import Path

# Define your downloaded files mapping
# Edit these paths to match where you saved files locally
downloads = {
    "magnetic-cable-organizer": [
        ("~/Downloads/magnetic_main1.jpg", "main-1.jpg"),
        ("~/Downloads/magnetic_main2.jpg", "main-2.jpg"),
        ("~/Downloads/magnetic_lifestyle.jpg", "lifestyle-1.jpg"),
        ("~/Downloads/magnetic_detail.jpg", "detail-1.jpg"),
        ("~/Downloads/magnetic_package.jpg", "package-1.jpg"),
    ],
    "foldable-silicone-bowl": [
        ("~/Downloads/bowl_main1.jpg", "main-1.jpg"),
        ("~/Downloads/bowl_main2.jpg", "main-2.jpg"),
        ("~/Downloads/bowl_lifestyle.jpg", "lifestyle-1.jpg"),
        ("~/Downloads/bowl_detail.jpg", "detail-1.jpg"),
        ("~/Downloads/bowl_package.jpg", "package-1.jpg"),
    ],
}

base = Path("fixtures/images")
for candidate, files in downloads.items():
    dest_dir = base / f"candidate-us-2026-09-01-{candidate}"
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src, dst in files:
        src_path = Path(src).expanduser()
        if src_path.exists():
            shutil.copy2(src_path, dest_dir / dst)
            print(f"Copied {src_path} -> {dest_dir / dst}")
        else:
            print(f"MISSING: {src_path}")

print("Done. Verify with:")
print("  ls -la fixtures/images/candidate-us-2026-09-01-magnetic-cable-organizer/")
print("  ls -la fixtures/images/candidate-us-2026-09-01-foldable-silicone-bowl/")
```

---

## Next Steps After Images

1. Commit images:
   ```bash
   git add fixtures/images/
   git commit -m "feat(phase1): add product images for top 2 candidates"
   ```

2. Update candidate files with image references

3. Use images in Phase 2 landing page prototypes and ad creative briefs