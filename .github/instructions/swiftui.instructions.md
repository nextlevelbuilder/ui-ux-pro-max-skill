---
applyTo: "**/*.swift"
---

# SwiftUI UI/UX Design Guidelines

When working with SwiftUI files, follow these guidelines:

## Search Design Database First

Before implementing UI, search for relevant styles:

```bash
# Get product-specific recommendations
python3 .shared/ui-ux-pro-max/scripts/search.py "<product-type>" --domain product

# Get mobile app style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "mobile app" --domain style

# Get color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "<industry>" --domain color

# Get SwiftUI-specific best practices
python3 .shared/ui-ux-pro-max/scripts/search.py "<topic>" --stack swiftui
```

## SwiftUI Best Practices

### View Structure
- Use `VStack`, `HStack`, `ZStack` for layouts
- Extract reusable views into separate structs
- Use `ViewBuilder` for conditional content

### Styling
- Use semantic colors: `Color.primary`, `Color.secondary`
- Apply modifiers in logical order
- Use `@Environment(\.colorScheme)` for dark mode

### Icons
- Use SF Symbols: `Image(systemName: "star.fill")`
- Apply consistent sizing with `.font(.title2)`
- Avoid emoji in production UI

### State & Interactivity
- Use `@State` for local view state
- Use `@Binding` for two-way data flow
- Add `.buttonStyle(.plain)` for custom tap areas
- Use `withAnimation` for smooth transitions

### Accessibility
- Add `.accessibilityLabel()` for custom controls
- Use semantic elements (Button, NavigationLink)
- Support Dynamic Type
- Test with VoiceOver

### Performance
- Use `LazyVStack`/`LazyHStack` for lists
- Apply `.drawingGroup()` for complex shapes
- Minimize view re-renders with proper state management
