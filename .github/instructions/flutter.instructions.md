---
applyTo: "**/*.dart"
---

# Flutter UI/UX Design Guidelines

When working with Flutter/Dart files, follow these guidelines:

## Search Design Database First

Before implementing UI, search for relevant styles:

```bash
# Get product-specific recommendations
python3 .shared/ui-ux-pro-max/scripts/search.py "<product-type>" --domain product

# Get mobile app style guide
python3 .shared/ui-ux-pro-max/scripts/search.py "mobile app" --domain style

# Get color palette
python3 .shared/ui-ux-pro-max/scripts/search.py "<industry>" --domain color

# Get Flutter-specific best practices
python3 .shared/ui-ux-pro-max/scripts/search.py "<topic>" --stack flutter
```

## Flutter Best Practices

### Widget Structure
- Prefer composition over inheritance
- Extract widgets into separate classes
- Use `const` constructors when possible

### Styling
- Define theme in `ThemeData`
- Use `Theme.of(context)` for consistent styling
- Separate colors into a constants file

### Icons
- Use `Icon` widget with Material or Cupertino icons
- Consistent sizing: `Icon(Icons.star, size: 24)`
- Avoid emoji in production UI

### State & Interactivity
- Use provider, Riverpod, or Bloc for state management
- Add `InkWell` or `GestureDetector` for tap handling
- Use `AnimatedContainer` for smooth transitions

### Accessibility
- Add `Semantics` widgets for screen readers
- Use `ExcludeSemantics` to hide decorative elements
- Support text scaling
- Test with TalkBack/VoiceOver

### Performance
- Use `const` widgets where possible
- Implement `ListView.builder` for long lists
- Profile with Flutter DevTools
- Avoid rebuilding entire widget trees
