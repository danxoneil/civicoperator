# NC Tobacco Policy Timeline Documentation

## Overview
Interactive timeline visualization of tobacco policy milestones in Mecklenburg County, NC (1969-2025).

## File Structure
- **nc-tobacco-policy-history.html** - Self-contained HTML file with embedded data and styling
- Timeline data is stored in the `TIMELINE` JavaScript array within the HTML file

## Data Source
Data extracted from: **Mecklenburg County Public Health – Tobacco Policy Timeline** (1969–2025)

## Timeline Coverage
- **1969-2025**: Comprehensive policy history covering:
  - Local ordinances (City of Charlotte, Mecklenburg County, towns)
  - State legislation (North Carolina)
  - Federal policies
  - Institutional tobacco-free adoptions (schools, hospitals, universities, behavioral health)
  - Tax policy changes
  - Public health initiatives

## Update Procedures

### Adding New Timeline Entries
1. Open `nc-tobacco-policy-history.html`
2. Locate the `TIMELINE` JavaScript array (around line 58)
3. Add or update year objects following this format:
```javascript
{year: YYYY, items: [
  "Policy description 1.",
  "Policy description 2."
]}
```

### Styling
- CSS is minified for performance
- Responsive design with mobile breakpoints at 991.98px
- Print-friendly media queries included

### Key Features
- Alternating left/right timeline layout
- Year nodes with visual indicators
- Responsive mobile view (single column)
- Bootstrap 5.3.3 framework

## Recent Changes (October 2025)
- Expanded timeline from ~10 to 16+ years of detailed entries
- Added years 2004, 2005, 2007-2024 with comprehensive policy milestones
- Removed broken embedded image placeholder (IMG_2005)
- Cleaned up unused CSS for thumbnail images

## Known Issues & Future Enhancements
1. **Missing Image**: The 2005 "Smoke Free Charlotte" entry originally planned to include an article cover image, but no source image was provided
2. **Data Externalization**: Consider moving timeline data to external JSON file for easier maintenance
3. **Version Control**: Use descriptive commit messages when making updates

## Technical Stack
- HTML5
- Bootstrap 5.3.3 (CSS framework)
- Vanilla JavaScript (no build step required)
- Self-contained (no external dependencies beyond CDN)

## Browser Compatibility
Works in all modern browsers. Requires JavaScript enabled.
