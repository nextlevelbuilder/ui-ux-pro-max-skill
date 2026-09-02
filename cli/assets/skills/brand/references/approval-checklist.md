# Asset Approval Checklist

Comprehensive checklist for reviewing marketing assets before approval.

## Quick Review

Before detailed review, verify:
- [ ] Asset serves stated purpose
- [ ] Target audience appropriate
- [ ] No obvious errors or issues
- [ ] Aligns with campaign goals

## Visual Elements

### Logo Usage
- [ ] Correct logo variant for context
- [ ] Proper clear space maintained
- [ ] Minimum size requirements met
- [ ] Approved colors only
- [ ] No unauthorized modifications
- [ ] Appropriate for background

### Color Compliance
- [ ] Uses brand palette colors only
- [ ] Primary/secondary ratio appropriate (60/30/10)
- [ ] Semantic colors used correctly
- [ ] No off-brand colors introduced
- [ ] Consistent across all elements

### Typography
- [ ] Brand fonts used throughout
- [ ] Correct font weights applied
- [ ] Proper type hierarchy
- [ ] Appropriate sizes for medium
- [ ] Line heights adequate
- [ ] No orphans/widows in body text

### Imagery
- [ ] Matches brand photography style
- [ ] Appropriate subjects/content
- [ ] Quality meets requirements
- [ ] Properly licensed/credited
- [ ] Optimized for intended use

## Accessibility

### Visual Accessibility
- [ ] Text contrast ratio >= 4.5:1 (AA)
- [ ] Large text contrast >= 3:1
- [ ] Interactive elements have visible focus
- [ ] Color not sole indicator of meaning
- [ ] Alt text for all images

### Content Accessibility
- [ ] Clear and scannable layout
- [ ] Readable font sizes
- [ ] Logical reading order
- [ ] Meaningful headings structure
- [ ] Links describe destination

## Content Quality

### Copy Review
- [ ] Matches brand voice
- [ ] Appropriate tone for context
- [ ] No prohibited terms used
- [ ] Value proposition clear
- [ ] CTA compelling and clear
- [ ] Proofread for errors

### Messaging
- [ ] Aligns with key messages
- [ ] Differentiators highlighted
- [ ] Benefits over features
- [ ] Target audience addressed
- [ ] No conflicting claims

## Technical Requirements

### File Specifications
- [ ] Correct file format
- [ ] Appropriate resolution
- [ ] File size optimized
- [ ] Proper naming convention
- [ ] Metadata included

### Platform Requirements
| Platform | Verified |
|----------|----------|
| Instagram | [ ] Correct dimensions |
| Twitter/X | [ ] Meets requirements |
| LinkedIn | [ ] Professional standards |
| Facebook | [ ] Guidelines compliant |
| Email | [ ] Size under 1MB |
| Web | [ ] Optimized for web |

## Legal & Compliance

### Intellectual Property
- [ ] Stock images licensed
- [ ] Music/audio cleared
- [ ] No trademark violations
- [ ] User content authorized
- [ ] Credits included where needed

### Regulatory
- [ ] Required disclosures present
- [ ] No misleading claims
- [ ] Pricing accurate
- [ ] Terms linked where needed
- [ ] Privacy compliant

## Review Status

### Reviewer Sign-off

| Review Area | Reviewer | Date | Status |
|-------------|----------|------|--------|
| Visual Design | | | [ ] Pass / [ ] Revisions |
| Copy/Content | | | [ ] Pass / [ ] Revisions |
| Brand Compliance | | | [ ] Pass / [ ] Revisions |
| Technical | | | [ ] Pass / [ ] Revisions |
| Legal | | | [ ] Pass / [ ] Revisions |

### Final Approval

- [ ] All review areas passed
- [ ] Revisions completed (if any)
- [ ] Final version uploaded
- [ ] Metadata updated
- [ ] Ready for publish/use

**Approved By:** _______________

**Date:** _______________

**Version:** _______________

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| Logo too small | Increase to minimum size |
| Wrong font | Replace with brand font |
| Low contrast | Adjust colors for accessibility |
| Off-brand color | Replace with palette color |
| Blurry image | Use higher resolution source |
| Missing alt text | Add descriptive alt text |
| Weak CTA | Strengthen action-oriented copy |

## Automation Support

The `validate-asset.cjs` script can auto-check:
- Color palette compliance
- Minimum dimensions
- File format/size
- Naming convention
- Basic metadata

Run: `node scripts/validate-asset.cjs <asset-path>`

## Archival

After approval:
1. Update asset status in manifest.json
2. Add approver and timestamp
3. Move previous versions to archive
4. Update campaign tracking
5. Notify relevant teams
