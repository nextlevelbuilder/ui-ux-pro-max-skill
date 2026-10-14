# Slide Strategies

15 proven deck structures with emotion arcs.

## Strategy Selection

| Strategy | Slides | Goal | Audience |
|----------|--------|------|----------|
| YC Seed Deck | 10-12 | Raise seed funding | VCs |
| Guy Kawasaki | 10 | Pitch in 20 min | Investors |
| Series A | 12-15 | Raise Series A | Growth VCs |
| Product Demo | 5-8 | Demonstrate value | Prospects |
| Sales Pitch | 7-10 | Close deal | Qualified leads |
| Nancy Duarte Sparkline | Varies | Transform perspective | Any |
| Problem-Solution-Benefit | 3-5 | Quick persuasion | Time-pressed |
| QBR | 10-15 | Update stakeholders | Leadership |
| Team All-Hands | 8-12 | Align team | Employees |
| Conference Talk | 15-25 | Thought leadership | Attendees |
| Workshop | 20-40 | Teach skills | Learners |
| Case Study | 8-12 | Prove value | Prospects |
| Competitive Analysis | 6-10 | Strategic decisions | Internal |
| Board Meeting | 15-20 | Update board | Directors |
| Webinar | 20-30 | Generate leads | Registrants |

## Common Structures

### YC Seed Deck (10 slides)
1. Title/Hook
2. Problem
3. Solution
4. Traction
5. Market
6. Product
7. Business Model
8. Team
9. Financials
10. The Ask

**Emotion arc:** curiosity→frustration→hope→confidence→trust→urgency

### Sales Pitch (9 slides)
1. Personalized Hook
2. Their Problem
3. Cost of Inaction
4. Your Solution
5. Proof/Case Studies
6. Differentiators
7. Pricing/ROI
8. Objection Handling
9. CTA + Next Steps

**Emotion arc:** connection→frustration→fear→hope→trust→confidence→urgency

### Product Demo (6 slides)
1. Hook/Problem
2. Solution Overview
3. Live Demo/Screenshots
4. Key Features
5. Benefits/Pricing
6. CTA

**Emotion arc:** curiosity→frustration→hope→confidence→urgency

## Duarte Sparkline Pattern

Alternate between "What Is" (current pain) and "What Could Be" (better future):

```
What Is → What Could Be → What Is → What Could Be → New Bliss
(pain)     (hope)         (pain)     (hope)         (resolution)
```

Pattern breaks at 1/3 and 2/3 positions create engagement peaks.

## Search Commands

```bash
# Find strategy by goal
python .github/skills/design-system/scripts/search-slides.py "investor pitch" -d strategy

# Get emotion arc
python .github/skills/design-system/scripts/search-slides.py "series a funding" -d strategy --json
```

## Matching Strategy to Context

| Context | Recommended Strategy |
|---------|---------------------|
| Raising money | YC Seed, Series A, Guy Kawasaki |
| Selling product | Sales Pitch, Product Demo |
| Internal update | QBR, All-Hands, Board Meeting |
| Public speaking | Conference Talk, Workshop |
| Proving value | Case Study, Competitive Analysis |
| Lead generation | Webinar |
