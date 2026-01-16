# Config Loader API Contract

**Feature**: [spec.md](../spec.md) | **Data Model**: [data-model.md](../data-model.md)
**Date**: 2026-01-16

## Overview

This contract defines the API for loading, validating, and merging external configuration files with built-in skill data. The Config Loader is responsible for extending the existing CSV-based architecture with external customizations.

## Module: `config_loader.py`

### Core Functions

#### `load_external_config(config_path: str = None) -> Dict`

**Purpose**: Load and validate external configuration from file system

**Parameters**:
- `config_path` (optional): Custom path to external configuration directory. Defaults to `.ui-ux-pro-max-config/`

**Returns**: Configuration dictionary with validated external data

**Schema**:
```python
{
    "enabled": bool,
    "domains": {
        "files": List[str],      # Loaded domain CSV files
        "data": List[Dict],      # Parsed domain data
        "errors": List[str]      # Validation errors
    },
    "stacks": {
        "files": List[str],      # Loaded stack CSV files
        "data": List[Dict],      # Parsed stack data
        "errors": List[str]      # Validation errors
    },
    "brand": {
        "enabled": bool,
        "config": Dict,          # Brand configuration
        "errors": List[str]      # Validation errors
    },
    "reasoning": {
        "enabled": bool,
        "rules": List[Dict],     # Custom reasoning rules
        "errors": List[str]      # Validation errors
    },
    "performance": {
        "max_entries": int,
        "current_entries": int,
        "warnings": List[str]    # Performance warnings
    },
    "metadata": {
        "config_path": str,      # Path to configuration directory
        "last_modified": str,    # ISO timestamp of last modification
        "version": str           # Configuration version
    }
}
```

**Error Handling**:
- Missing configuration directory → Return empty config with `enabled: false`
- Invalid JSON files → Log errors, skip invalid sections, continue loading
- Missing required fields → Use default values, log warnings
- File permission errors → Log error, fall back to built-in data only

#### `merge_with_builtin(external_config: Dict, builtin_data: Dict) -> Dict`

**Purpose**: Merge external configuration with built-in skill data using conflict resolution strategy

**Parameters**:
- `external_config`: External configuration from `load_external_config()`
- `builtin_data`: Built-in CSV data from existing skill

**Returns**: Merged data dictionary with combined built-in and external data

**Merge Strategy**:
1. **Domains**: Append external domains to built-in domains
2. **Stacks**: Append external stacks to built-in stacks
3. **CSV Data**: Combine rows, external data has higher search priority
4. **Conflicts**: Log conflicts, prefer external values for non-critical fields
5. **Validation**: Re-validate merged data for consistency

**Schema**:
```python
{
    "domains": List[Dict],       # Combined domain data
    "stacks": List[Dict],        # Combined stack data
    "brand_config": Dict,        # Brand configuration (external only)
    "reasoning_rules": List[Dict], # Custom reasoning rules
    "conflicts": List[Dict],     # Resolved conflicts with details
    "statistics": {
        "builtin_entries": int,
        "external_entries": int,
        "total_entries": int,
        "conflicts_resolved": int
    }
}
```

#### `validate_configuration(config: Dict) -> ValidationResult`

**Purpose**: Validate external configuration files against required schemas

**Parameters**:
- `config`: Configuration dictionary to validate

**Returns**: Validation result with detailed error information

**Schema**:
```python
ValidationResult = {
    "valid": bool,               # Overall validation status
    "errors": List[Dict],        # Validation errors
    "warnings": List[Dict],      # Non-critical issues
    "file_validations": {
        "config.json": {
            "valid": bool,
            "errors": List[str],
            "schema_version": str
        },
        "brand/brand.json": {
            "valid": bool,
            "errors": List[str],
            "required_fields": List[str],
            "missing_fields": List[str]
        },
        "domains/*.csv": {
            "valid": bool,
            "errors": List[str],
            "row_count": int,
            "column_validation": Dict
        },
        "stacks/*.csv": {
            "valid": bool,
            "errors": List[str],
            "row_count": int,
            "column_validation": Dict
        }
    }
}
```

**Validation Rules**:
- **JSON Schema**: Strict validation against defined schemas
- **CSV Format**: Required columns present, data types correct
- **File References**: All referenced files exist and are readable
- **Cross-Validation**: Configuration references are consistent
- **Performance**: Entry count within performance limits

#### `get_config_status() -> Dict`

**Purpose**: Get current status of external configuration system

**Returns**: Status information for debugging and monitoring

**Schema**:
```python
{
    "enabled": bool,
    "config_path": str,
    "last_loaded": str,          # ISO timestamp
    "auto_reload": bool,
    "performance": {
        "entries": int,
        "memory_usage": str,
        "load_time": float,
        "cache_hit_rate": float
    },
    "health": {
        "status": "healthy|warning|error",
        "issues": List[str],
        "recommendations": List[str]
    }
}
```

### Utility Functions

#### `discover_config_files(config_path: str) -> List[str]`

**Purpose**: Discover available configuration files in directory structure

**Returns**: List of discovered configuration file paths

#### `watch_config_changes(callback: Callable) -> None`

**Purpose**: Monitor configuration files for changes and trigger reloads

**Parameters**:
- `callback`: Function to call when changes are detected

#### `cache_config(config: Dict, cache_key: str) -> None`

**Purpose**: Cache validated configuration for performance

#### `get_cached_config(cache_key: str) -> Dict`

**Purpose**: Retrieve cached configuration if available and valid

## Integration Points

### With `core.py`

```python
# Extended search function signature
def search_domains(query: str, domain: str = None, external_config: Dict = None) -> List[Dict]:
    """
    Search domains with external configuration support

    Args:
        query: Search query string
        domain: Domain filter (existing parameter)
        external_config: External configuration data

    Returns:
        Ranked search results with external data included
    """
```

### With `brand_processor.py`

```python
# Brand integration interface
def apply_brand_config(results: List[Dict], brand_config: Dict) -> List[Dict]:
    """
    Apply brand configuration to search results

    Args:
        results: Search results from core.py
        brand_config: Brand configuration from external config

    Returns:
        Results modified with brand-specific recommendations
    """
```

### With `search.py` (CLI)

```python
# CLI integration with external config
def main():
    # Load external configuration
    external_config = load_external_config()

    # Merge with built-in data
    merged_data = merge_with_builtin(external_config, builtin_data)

    # Perform search with merged data
    results = search_domains(query, domain, external_config)

    # Apply brand configuration if enabled
    if external_config.get("brand", {}).get("enabled"):
        results = apply_brand_config(results, external_config["brand"]["config"])

    # Return formatted results
    return format_results(results)
```

## Error Scenarios

### Configuration File Errors

**Invalid JSON**:
```python
{
    "error": "json_parse_error",
    "file": "config.json",
    "line": 15,
    "message": "Unexpected token '}' at line 15",
    "action": "skip_file_continue_loading"
}
```

**Missing Required Fields**:
```python
{
    "error": "missing_required_field",
    "file": "brand/brand.json",
    "field": "colors.primary",
    "message": "Required brand primary color not specified",
    "action": "use_default_value"
}
```

**CSV Format Errors**:
```python
{
    "error": "csv_format_error",
    "file": "domains/custom.csv",
    "row": 5,
    "column": "description",
    "message": "Description exceeds maximum length of 500 characters",
    "action": "truncate_and_warn"
}
```

### Performance Errors

**Entry Limit Exceeded**:
```python
{
    "error": "performance_limit_exceeded",
    "current_entries": 1250,
    "max_entries": 1000,
    "message": "External configuration exceeds recommended entry limit",
    "action": "continue_with_warning"
}
```

### File System Errors

**Permission Denied**:
```python
{
    "error": "permission_denied",
    "path": ".ui-ux-pro-max-config/",
    "message": "Cannot read configuration directory",
    "action": "fallback_to_builtin_only"
}
```

## Testing Contract

### Unit Test Requirements

```python
class TestConfigLoader(unittest.TestCase):
    def test_load_external_config_success(self):
        """Test successful loading of valid external configuration"""

    def test_load_external_config_missing_directory(self):
        """Test handling of missing configuration directory"""

    def test_load_external_config_invalid_json(self):
        """Test handling of invalid JSON files"""

    def test_merge_with_builtin_no_conflicts(self):
        """Test merging external and built-in data without conflicts"""

    def test_merge_with_builtin_with_conflicts(self):
        """Test conflict resolution during merge"""

    def test_validate_configuration_valid(self):
        """Test validation of correct configuration"""

    def test_validate_configuration_errors(self):
        """Test validation error detection and reporting"""

    def test_performance_limits(self):
        """Test performance warning system"""

    def test_file_watching(self):
        """Test configuration file change detection"""

    def test_caching_behavior(self):
        """Test configuration caching and invalidation"""
```

### Integration Test Requirements

```python
class TestConfigLoaderIntegration(unittest.TestCase):
    def test_end_to_end_search_with_external_config(self):
        """Test complete search workflow with external configuration"""

    def test_brand_integration_workflow(self):
        """Test brand configuration integration with search results"""

    def test_cli_integration(self):
        """Test CLI command with external configuration loading"""

    def test_error_recovery(self):
        """Test graceful degradation on configuration errors"""
```

This contract provides the foundation for implementing robust external configuration support while maintaining backward compatibility with the existing UI/UX Pro Max skill architecture.