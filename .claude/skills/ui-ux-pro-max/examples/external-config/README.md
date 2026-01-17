# UI/UX Pro Max External Configuration Example

This example demonstrates how to set up and use external configuration with the UI/UX Pro Max skill for advanced customization.

## Directory Structure

```
.ui-ux-pro-max-config/
├── config.json                    # Main configuration file
├── domains/
│   └── custom-fintech.csv        # Custom fintech domain patterns
├── stacks/
│   └── enterprise-tools.csv      # Custom enterprise stack patterns
├── reasoning/
│   └── custom-reasoning.json     # Custom reasoning rules
└── brand/
    └── brand.json                # Brand configuration
```

## Features Demonstrated

### 1. Brand Integration
The `brand/brand.json` file defines:
- TechCorp brand colors (Google-inspired palette)
- Inter and JetBrains Mono typography
- Clean, minimalist design philosophy
- Geometric spacing system

### 2. Custom Domain (Fintech)
The `domains/custom-fintech.csv` includes specialized patterns:
- Financial dashboards with real-time data
- Trading interfaces for high-frequency operations
- Compliance forms meeting FINRA/SEC requirements
- Risk indicators with clear escalation levels
- Market data tables with instant change recognition

### 3. Custom Stack (Enterprise Tools)
The `stacks/enterprise-tools.csv` provides:
- SSO integration patterns (OAuth 2.0, SAML)
- Audit logging for compliance
- Role-based access control systems
- Data encryption best practices
- Bulk operations for large datasets
- White-labeling capabilities

### 4. Custom Reasoning Rules
The `reasoning/custom-reasoning.json` emphasizes:
- High security and compliance weights
- Industry-specific adjustments for fintech/healthcare/enterprise
- Framework preferences (React hooks, Vue Composition API)
- Accessibility-first design principles

## Usage Examples

### Basic Search with Brand Applied
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "dashboard design" --apply-brand --config-path ./examples/external-config/.ui-ux-pro-max-config/
```
*Results will use TechCorp brand colors and typography*

### Custom Domain Search
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "trading interface" --domain custom-fintech --config-path ./examples/external-config/.ui-ux-pro-max-config/
```
*Returns fintech-specific trading interface patterns*

### Custom Stack Search
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py "authentication" --stack enterprise-tools --config-path ./examples/external-config/.ui-ux-pro-max-config/
```
*Returns enterprise SSO and authentication patterns*

### Configuration Status Check
```bash
python3 .claude/skills/ui-ux-pro-max/scripts/search.py --config-status --config-path ./examples/external-config/.ui-ux-pro-max-config/
```
*Shows detailed external configuration status*

## Expected Output

When using this configuration, you'll see:

1. **Enhanced Search Results**: All design recommendations incorporate TechCorp brand colors (#1a73e8 primary, #34a853 secondary)

2. **Industry-Specific Patterns**: Fintech searches return specialized patterns like compliance forms and trading interfaces

3. **Enterprise Integration**: Stack searches include enterprise-specific patterns like SSO integration and audit logging

4. **Reasoning-Aware Results**: Search results prioritize security, compliance, and accessibility based on custom reasoning rules

## Testing the Configuration

1. **Copy this directory** to your project root:
   ```bash
   cp -r .claude/skills/ui-ux-pro-max/examples/external-config/.ui-ux-pro-max-config ./
   ```

2. **Run configuration validation**:
   ```bash
   python3 .claude/skills/ui-ux-pro-max/scripts/search.py --config-status
   ```

3. **Test brand integration**:
   ```bash
   python3 .claude/skills/ui-ux-pro-max/scripts/search.py "color palette" --apply-brand
   ```

4. **Test custom patterns**:
   ```bash
   python3 .claude/skills/ui-ux-pro-max/scripts/search.py "compliance form" --domain custom-fintech
   ```

## Customization Guide

### Adding Your Own Brand
1. Edit `brand/brand.json` with your colors and fonts
2. Update `config.json` to enable brand integration
3. Test with `--apply-brand` flag

### Creating Custom Domains
1. Create new CSV file in `domains/` directory
2. Include required columns: `term,description,examples,code_example,reasoning,category,priority`
3. Add domain name to `config.json` enabled array

### Adding Custom Stacks
1. Create new CSV file in `stacks/` directory
2. Include platform-specific patterns and anti-patterns
3. Add stack name to `config.json` enabled array

### Customizing Reasoning
1. Edit `reasoning/custom-reasoning.json`
2. Adjust weights for different criteria (accessibility, security, etc.)
3. Add industry-specific adjustments
4. Set framework preferences

## Performance Notes

This example configuration includes:
- **52 custom domain entries** (fintech patterns)
- **20 custom stack entries** (enterprise tools)
- **Brand configuration** with full color and typography system
- **Custom reasoning rules** with industry adjustments

Total configuration size is well under the 1000-entry recommended limit, ensuring fast search performance.

## Integration with Development Workflow

This configuration can be:
- **Version controlled** alongside your project
- **Shared with your team** for consistent design patterns
- **Customized per environment** (dev/staging/prod)
- **Extended with additional domains** as your project grows

The external configuration system maintains full backward compatibility with the base UI/UX Pro Max skill while providing powerful customization capabilities.