---
name: build-dashboard
description: Build a professional dashboard with charts, cards, and data visualization
argument-hint: Describe the dashboard purpose (e.g., "analytics dashboard", "admin panel")
tools:
  - execute/runInTerminal
---

# Build Dashboard

Create a professional dashboard with data visualization.

## Task: ${input:description:Describe your dashboard}

## Step 1: Search Design Database

```bash
# Product type recommendations
python3 .shared/ui-ux-pro-max/scripts/search.py "dashboard admin analytics" --domain product

# Chart recommendations
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:dataTypes:trend comparison}" --domain chart

# Color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "${input:industry:analytics}" --domain color

# Style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "dashboard minimal" --domain style

# UX guidelines
python3 .shared/ui-ux-pro-max/scripts/search.py "loading skeleton" --domain ux
python3 .shared/ui-ux-pro-max/scripts/search.py "table pagination" --domain ux
```

## Step 2: Implement Dashboard

Based on search results, create a dashboard with:

### Layout
- Sidebar navigation (collapsible on mobile)
- Top header with search, notifications, user menu
- Main content area with grid layout
- Responsive breakpoints

### Components
- Stat cards with trends
- Charts (based on chart search results)
- Data tables with sorting/filtering
- Activity feeds
- Quick actions

### Design System
- Apply color palette from search
- Use consistent spacing (8px grid)
- Card-based layout with subtle shadows
- Clear visual hierarchy

### Technical Requirements
- Semantic HTML structure
- Tailwind CSS
- Chart library (Chart.js, Recharts, or ApexCharts)
- Loading states and skeletons
- Accessible data tables
