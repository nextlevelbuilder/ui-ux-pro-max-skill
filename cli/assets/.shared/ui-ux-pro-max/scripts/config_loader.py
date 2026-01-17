#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI/UX Pro Max Config Loader - External configuration management
Loads and validates external configuration files from .ui-ux-pro-max-config/
"""

import csv
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime


class ConfigLoader:
    """Manages external configuration loading, validation, and merging"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader

        Args:
            config_path: Custom path to external configuration directory
        """
        self.config_path = Path(config_path) if config_path else Path.cwd() / ".ui-ux-pro-max-config"
        self.cache = {}
        self.last_modified = {}

    def load_external_config(self, config_path: Optional[str] = None) -> Dict:
        """
        Load and validate external configuration from file system

        Args:
            config_path: Custom path to external configuration directory

        Returns:
            Configuration dictionary with validated external data
        """
        if config_path:
            self.config_path = Path(config_path)

        # Check if configuration directory exists
        if not self.config_path.exists():
            return {
                "enabled": False,
                "domains": {"files": [], "data": [], "errors": []},
                "stacks": {"files": [], "data": [], "errors": []},
                "brand": {"enabled": False, "config": {}, "errors": []},
                "reasoning": {"enabled": False, "rules": [], "errors": []},
                "performance": {"max_entries": 1000, "current_entries": 0, "warnings": []},
                "metadata": {
                    "config_path": str(self.config_path),
                    "last_modified": datetime.now().isoformat(),
                    "version": "1.0.0"
                }
            }

        config = {
            "enabled": True,
            "domains": {"files": [], "data": [], "errors": []},
            "stacks": {"files": [], "data": [], "errors": []},
            "brand": {"enabled": False, "config": {}, "errors": []},
            "reasoning": {"enabled": False, "rules": [], "errors": []},
            "performance": {"max_entries": 1000, "current_entries": 0, "warnings": []},
            "metadata": {
                "config_path": str(self.config_path),
                "last_modified": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }

        try:
            # Load main configuration file
            main_config_path = self.config_path / "config.json"
            if main_config_path.exists():
                with open(main_config_path, 'r', encoding='utf-8') as f:
                    main_config = json.load(f)
                    config["metadata"]["version"] = main_config.get("version", "1.0.0")
                    config["performance"]["max_entries"] = main_config.get("performance", {}).get("max_entries", 1000)

                    # Load brand configuration
                    brand_config = main_config.get("brand", {})
                    if brand_config.get("enabled", False):
                        config["brand"]["enabled"] = True
                        brand_file = self.config_path / brand_config.get("file", "brand/brand.json")
                        if brand_file.exists():
                            try:
                                with open(brand_file, 'r', encoding='utf-8') as bf:
                                    config["brand"]["config"] = json.load(bf)
                            except json.JSONDecodeError as e:
                                config["brand"]["errors"].append(f"Invalid JSON in {brand_file}: {str(e)}")
                            except Exception as e:
                                config["brand"]["errors"].append(f"Error loading {brand_file}: {str(e)}")
                        else:
                            config["brand"]["errors"].append(f"Brand file not found: {brand_file}")

                    # Load reasoning configuration
                    reasoning_config = main_config.get("reasoning", {})
                    if reasoning_config.get("enabled", False):
                        config["reasoning"]["enabled"] = True
                        for rule_file in reasoning_config.get("files", []):
                            rule_path = self.config_path / rule_file
                            if rule_path.exists():
                                try:
                                    with open(rule_path, 'r', encoding='utf-8') as rf:
                                        rule_data = json.load(rf)
                                        config["reasoning"]["rules"].append(rule_data)
                                except json.JSONDecodeError as e:
                                    config["reasoning"]["errors"].append(f"Invalid JSON in {rule_path}: {str(e)}")
                                except Exception as e:
                                    config["reasoning"]["errors"].append(f"Error loading {rule_path}: {str(e)}")
                            else:
                                config["reasoning"]["errors"].append(f"Reasoning file not found: {rule_path}")

        except json.JSONDecodeError as e:
            config["domains"]["errors"].append(f"Invalid JSON in config.json: {str(e)}")
        except FileNotFoundError:
            # No main config file - proceed with defaults
            pass
        except Exception as e:
            config["domains"]["errors"].append(f"Error loading main config: {str(e)}")

        # Load domain CSV files
        domains_dir = self.config_path / "domains"
        if domains_dir.exists():
            for csv_file in domains_dir.glob("*.csv"):
                try:
                    domain_data = self._load_csv_file(csv_file)
                    config["domains"]["files"].append(str(csv_file))
                    config["domains"]["data"].extend(domain_data)
                except Exception as e:
                    config["domains"]["errors"].append(f"Error loading {csv_file}: {str(e)}")

        # Load stack CSV files
        stacks_dir = self.config_path / "stacks"
        if stacks_dir.exists():
            for csv_file in stacks_dir.glob("*.csv"):
                try:
                    stack_data = self._load_csv_file(csv_file)
                    config["stacks"]["files"].append(str(csv_file))
                    config["stacks"]["data"].extend(stack_data)
                except Exception as e:
                    config["stacks"]["errors"].append(f"Error loading {csv_file}: {str(e)}")

        # Calculate performance metrics
        total_entries = len(config["domains"]["data"]) + len(config["stacks"]["data"])
        config["performance"]["current_entries"] = total_entries

        if total_entries > config["performance"]["max_entries"]:
            config["performance"]["warnings"].append(
                f"External configuration has {total_entries} entries, "
                f"exceeding recommended limit of {config['performance']['max_entries']}"
            )

        # Update last modified timestamp
        if self.config_path.exists():
            config["metadata"]["last_modified"] = datetime.fromtimestamp(
                self.config_path.stat().st_mtime
            ).isoformat()

        return config

    def _load_csv_file(self, csv_path: Path) -> List[Dict]:
        """
        Load and parse CSV file with permissive validation (FR-004)
        Loads valid portions while providing clear warning messages for invalid entries
        """
        data = []
        warnings = []
        csv_type = self._detect_csv_type(csv_path)
        required_columns = self._get_required_columns(csv_type)

        with open(csv_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []

            # Check for missing required columns
            missing_columns = set(required_columns) - set(fieldnames)
            if missing_columns:
                warnings.append({
                    "type": "schema_warning",
                    "file": str(csv_path),
                    "message": f"Missing required columns: {', '.join(missing_columns)}. Rows with missing data will use default values.",
                    "severity": "warning"
                })

            for row_idx, row in enumerate(reader, 1):
                # Skip completely empty rows
                if not any(v.strip() for v in row.values() if v):
                    continue

                # Validate row with permissive approach
                row_valid = True
                row_warnings = []

                # Check required fields
                for col in required_columns:
                    if col not in row or not row[col].strip():
                        if col in ['name', 'title', 'description']:  # Critical fields
                            row_warnings.append(f"Missing required field '{col}' at row {row_idx}")
                            row_valid = False
                        else:
                            # Provide default value for non-critical fields
                            row[col] = f"default_{col}"
                            row_warnings.append(f"Using default value for missing field '{col}' at row {row_idx}")

                # Data type validation with permissive fallbacks
                if 'priority' in row:
                    try:
                        int(row['priority'])
                    except ValueError:
                        row['priority'] = '5'  # Default priority
                        row_warnings.append(f"Invalid priority value at row {row_idx}, using default: 5")

                # Length validation with truncation
                for col, value in row.items():
                    if isinstance(value, str) and len(value) > 1000:
                        row[col] = value[:1000] + "..."
                        row_warnings.append(f"Truncated long value in column '{col}' at row {row_idx}")

                # Only add valid rows to data
                if row_valid:
                    # Add metadata
                    row['_source'] = str(csv_path)
                    row['_row'] = row_idx
                    row['_warnings'] = row_warnings
                    data.append(row)

                    # Collect warnings for reporting
                    warnings.extend([{
                        "type": "row_warning",
                        "file": str(csv_path),
                        "row": row_idx,
                        "message": warning,
                        "severity": "warning"
                    } for warning in row_warnings])
                else:
                    # Report skipped rows
                    warnings.append({
                        "type": "row_error",
                        "file": str(csv_path),
                        "row": row_idx,
                        "message": f"Skipping invalid row: {'; '.join(row_warnings)}",
                        "severity": "error"
                    })

        # Store warnings for later retrieval
        if not hasattr(self, '_validation_warnings'):
            self._validation_warnings = []
        self._validation_warnings.extend(warnings)

        return data

    def _detect_csv_type(self, csv_path: Path) -> str:
        """Detect CSV file type based on path and content"""
        path_str = str(csv_path).lower()
        if '/domains/' in path_str:
            return 'domains'
        elif '/stacks/' in path_str:
            return 'stacks'
        else:
            # Try to detect from content
            try:
                with open(csv_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline().lower()
                    if 'stack' in first_line or 'framework' in first_line:
                        return 'stacks'
                    else:
                        return 'domains'
            except:
                return 'domains'  # Default fallback

    def merge_with_builtin(self, external_config: Dict, builtin_data: Dict) -> Dict:
        """
        Merge external configuration with built-in skill data with conflict resolution (FR-005)
        Combines valid fields from external configuration with built-in defaults,
        logs conflicts, and uses built-in values for conflicted fields

        Args:
            external_config: External configuration from load_external_config()
            builtin_data: Built-in CSV data from existing skill

        Returns:
            Merged data dictionary with combined built-in and external data
        """
        merged = {
            "domains": [],
            "stacks": [],
            "brand_config": external_config.get("brand", {}).get("config", {}),
            "reasoning_rules": external_config.get("reasoning", {}).get("rules", []),
            "conflicts": [],
            "statistics": {
                "builtin_entries": 0,
                "external_entries": 0,
                "total_entries": 0,
                "conflicts_resolved": 0,
                "duplicates_found": 0
            }
        }

        # Merge domain data with conflict detection
        builtin_domains = builtin_data.get("domains", [])
        external_domains = external_config.get("domains", {}).get("data", [])

        merged_domains, domain_conflicts = self._merge_with_conflict_resolution(
            builtin_domains, external_domains, "domains"
        )
        merged["domains"] = merged_domains
        merged["conflicts"].extend(domain_conflicts)

        # Merge stack data with conflict detection
        builtin_stacks = builtin_data.get("stacks", [])
        external_stacks = external_config.get("stacks", {}).get("data", [])

        merged_stacks, stack_conflicts = self._merge_with_conflict_resolution(
            builtin_stacks, external_stacks, "stacks"
        )
        merged["stacks"] = merged_stacks
        merged["conflicts"].extend(stack_conflicts)

        # Update statistics
        merged["statistics"]["builtin_entries"] = len(builtin_domains) + len(builtin_stacks)
        merged["statistics"]["external_entries"] = len(external_domains) + len(external_stacks)
        merged["statistics"]["total_entries"] = len(merged["domains"]) + len(merged["stacks"])
        merged["statistics"]["conflicts_resolved"] = len(merged["conflicts"])
        merged["statistics"]["duplicates_found"] = sum(1 for c in merged["conflicts"] if c["type"] == "duplicate")

        return merged

    def _merge_with_conflict_resolution(self, builtin_items: List[Dict], external_items: List[Dict], data_type: str) -> tuple[List[Dict], List[Dict]]:
        """
        Merge items with conflict detection and resolution

        Returns:
            Tuple of (merged_items, conflicts_found)
        """
        merged_items = []
        conflicts = []

        # Start with all built-in items (built-in takes precedence for conflicts)
        merged_items.extend(builtin_items)
        builtin_keys = set()

        # Build index of built-in items for conflict detection
        for item in builtin_items:
            key = self._generate_item_key(item)
            builtin_keys.add(key)

        # Add external items, detecting conflicts
        for ext_item in external_items:
            ext_key = self._generate_item_key(ext_item)

            # Check for conflicts
            if ext_key in builtin_keys:
                # Find the conflicting built-in item
                builtin_item = next((item for item in builtin_items if self._generate_item_key(item) == ext_key), None)

                # Log conflict and use built-in value (FR-005 requirement)
                conflicts.append({
                    "type": "duplicate",
                    "data_type": data_type,
                    "key": ext_key,
                    "builtin_source": builtin_item.get('_source', 'built-in'),
                    "external_source": ext_item.get('_source', 'external'),
                    "resolution": "used_builtin",
                    "message": f"Duplicate entry '{ext_key}' found in both built-in and external {data_type}. Using built-in version."
                })
            else:
                # No conflict, add external item
                merged_items.append(ext_item)

                # Check for field-level conflicts in similar items
                similar_conflicts = self._detect_field_conflicts(ext_item, builtin_items, data_type)
                conflicts.extend(similar_conflicts)

        return merged_items, conflicts

    def _generate_item_key(self, item: Dict) -> str:
        """Generate a unique key for an item for conflict detection"""
        # Use multiple fields to create a unique key
        key_fields = []

        # Primary identifiers
        for field in ['name', 'title', 'style', 'stack', 'framework']:
            if field in item and item[field]:
                key_fields.append(item[field].lower().strip())

        # Fallback to first non-empty field
        if not key_fields:
            for value in item.values():
                if value and isinstance(value, str) and not value.startswith('_'):
                    key_fields.append(value.lower().strip()[:50])  # Use first 50 chars
                    break

        return '|'.join(key_fields) if key_fields else 'unknown'

    def _detect_field_conflicts(self, external_item: Dict, builtin_items: List[Dict], data_type: str) -> List[Dict]:
        """Detect field-level conflicts between similar items"""
        conflicts = []
        ext_key = self._generate_item_key(external_item)

        # Look for items with similar names/titles that might have conflicting field values
        for builtin_item in builtin_items:
            builtin_key = self._generate_item_key(builtin_item)

            # Check for partial matches that might indicate related entries
            similarity = self._calculate_key_similarity(ext_key, builtin_key)
            if similarity > 0.7:  # 70% similarity threshold
                # Compare field values
                conflicting_fields = []
                for field in external_item:
                    if (field in builtin_item and
                        not field.startswith('_') and  # Skip metadata fields
                        external_item[field] != builtin_item[field]):
                        conflicting_fields.append(field)

                if conflicting_fields:
                    conflicts.append({
                        "type": "field_conflict",
                        "data_type": data_type,
                        "external_key": ext_key,
                        "builtin_key": builtin_key,
                        "conflicting_fields": conflicting_fields,
                        "similarity": similarity,
                        "resolution": "external_fields_used",
                        "message": f"Field conflicts detected between similar entries. External values used for fields: {', '.join(conflicting_fields)}"
                    })

        return conflicts

    def _calculate_key_similarity(self, key1: str, key2: str) -> float:
        """Calculate similarity between two keys (simple implementation)"""
        if not key1 or not key2:
            return 0.0

        # Simple word-based similarity
        words1 = set(key1.lower().split())
        words2 = set(key2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def validate_configuration(self, config: Dict) -> Dict:
        """
        Validate external configuration files against required schemas

        Args:
            config: Configuration dictionary to validate

        Returns:
            Validation result with detailed error information
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "file_validations": {}
        }

        # Validate main config.json
        config_json_path = self.config_path / "config.json"
        if config_json_path.exists():
            config_validation = self._validate_main_config(config_json_path)
            result["file_validations"]["config.json"] = config_validation
            if not config_validation["valid"]:
                result["valid"] = False
                result["errors"].extend(config_validation["errors"])

        # Validate brand configuration
        if config.get("brand", {}).get("enabled"):
            brand_path = self.config_path / "brand" / "brand.json"
            if brand_path.exists():
                brand_validation = self._validate_brand_config(brand_path)
                result["file_validations"]["brand/brand.json"] = brand_validation
                if not brand_validation["valid"]:
                    result["valid"] = False
                    result["errors"].extend(brand_validation["errors"])

        # Validate CSV files
        for csv_type in ["domains", "stacks"]:
            csv_dir = self.config_path / csv_type
            if csv_dir.exists():
                for csv_file in csv_dir.glob("*.csv"):
                    csv_validation = self._validate_csv_file(csv_file, csv_type)
                    key = f"{csv_type}/{csv_file.name}"
                    result["file_validations"][key] = csv_validation
                    if not csv_validation["valid"]:
                        result["valid"] = False
                        result["errors"].extend(csv_validation["errors"])

        # Performance validation
        total_entries = config.get("performance", {}).get("current_entries", 0)
        max_entries = config.get("performance", {}).get("max_entries", 1000)

        if total_entries > max_entries:
            result["warnings"].append({
                "type": "performance",
                "message": f"Configuration has {total_entries} entries, exceeding recommended limit of {max_entries}",
                "severity": "warning"
            })

        return result

    def _validate_main_config(self, config_path: Path) -> Dict:
        """Validate main configuration file"""
        validation = {
            "valid": True,
            "errors": [],
            "schema_version": "1.0.0"
        }

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)

            # Check required fields
            if "version" not in config_data:
                validation["errors"].append("Missing required field: version")
                validation["valid"] = False

            # Validate performance section
            if "performance" in config_data:
                perf = config_data["performance"]
                if "max_entries" in perf and not isinstance(perf["max_entries"], int):
                    validation["errors"].append("performance.max_entries must be an integer")
                    validation["valid"] = False

        except json.JSONDecodeError as e:
            validation["errors"].append(f"Invalid JSON: {str(e)}")
            validation["valid"] = False
        except Exception as e:
            validation["errors"].append(f"Validation error: {str(e)}")
            validation["valid"] = False

        return validation

    def _validate_brand_config(self, brand_path: Path) -> Dict:
        """Validate brand configuration file"""
        validation = {
            "valid": True,
            "errors": [],
            "required_fields": ["colors", "typography"],
            "missing_fields": []
        }

        try:
            with open(brand_path, 'r', encoding='utf-8') as f:
                brand_data = json.load(f)

            # Check required sections
            for field in validation["required_fields"]:
                if field not in brand_data:
                    validation["missing_fields"].append(field)
                    validation["errors"].append(f"Missing required section: {field}")
                    validation["valid"] = False

            # Validate colors section
            if "colors" in brand_data:
                colors = brand_data["colors"]
                if "primary" not in colors:
                    validation["errors"].append("Missing required color: primary")
                    validation["valid"] = False

                # Validate hex color format
                for color_name, color_value in colors.items():
                    if isinstance(color_value, str) and not re.match(r'^#[0-9A-Fa-f]{6}$', color_value):
                        validation["errors"].append(f"Invalid hex color format for {color_name}: {color_value}")
                        validation["valid"] = False

        except json.JSONDecodeError as e:
            validation["errors"].append(f"Invalid JSON: {str(e)}")
            validation["valid"] = False
        except Exception as e:
            validation["errors"].append(f"Validation error: {str(e)}")
            validation["valid"] = False

        return validation

    def _validate_csv_file(self, csv_path: Path, csv_type: str) -> Dict:
        """Validate CSV file format and content"""
        validation = {
            "valid": True,
            "errors": [],
            "row_count": 0,
            "column_validation": {}
        }

        try:
            with open(csv_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or []

                # Check for required columns based on type
                required_columns = self._get_required_columns(csv_type)
                missing_columns = set(required_columns) - set(fieldnames)

                if missing_columns:
                    validation["errors"].append(f"Missing required columns: {', '.join(missing_columns)}")
                    validation["valid"] = False

                # Count rows and validate content
                for row_idx, row in enumerate(reader, 1):
                    validation["row_count"] = row_idx

                    # Check for empty required fields
                    for col in required_columns:
                        if col in row and not row[col].strip():
                            validation["errors"].append(f"Empty required field '{col}' at row {row_idx}")
                            validation["valid"] = False

        except Exception as e:
            validation["errors"].append(f"CSV validation error: {str(e)}")
            validation["valid"] = False

        return validation

    def get_validation_warnings(self) -> List[Dict]:
        """
        Get validation warnings collected during permissive loading (FR-004)

        Returns:
            List of warning dictionaries with details about validation issues
        """
        return getattr(self, '_validation_warnings', [])

    def clear_validation_warnings(self) -> None:
        """Clear collected validation warnings"""
        self._validation_warnings = []

    def _get_required_columns(self, csv_type: str) -> List[str]:
        """Get required columns for CSV type"""
        if csv_type == "domains":
            return ["term", "description", "examples", "category"]
        elif csv_type == "stacks":
            return ["Category", "Guideline", "Description", "Do", "Don't"]
        return []

    def get_config_status(self) -> Dict:
        """
        Get current status of external configuration system

        Returns:
            Status information for debugging and monitoring
        """
        status = {
            "enabled": self.config_path.exists(),
            "config_path": str(self.config_path),
            "last_loaded": "",
            "auto_reload": False,  # Not implemented yet
            "performance": {
                "entries": 0,
                "memory_usage": "0 KB",
                "load_time": 0.0,
                "cache_hit_rate": 0.0
            },
            "health": {
                "status": "healthy",
                "issues": [],
                "recommendations": []
            }
        }

        if self.config_path.exists():
            try:
                # Get last modification time
                status["last_loaded"] = datetime.fromtimestamp(
                    self.config_path.stat().st_mtime
                ).isoformat()

                # Basic health checks
                config = self.load_external_config()
                status["performance"]["entries"] = config["performance"]["current_entries"]

                if config["domains"]["errors"] or config["stacks"]["errors"] or config["brand"]["errors"]:
                    status["health"]["status"] = "warning"
                    status["health"]["issues"].extend(config["domains"]["errors"])
                    status["health"]["issues"].extend(config["stacks"]["errors"])
                    status["health"]["issues"].extend(config["brand"]["errors"])

                if config["performance"]["warnings"]:
                    status["health"]["status"] = "warning"
                    status["health"]["issues"].extend(config["performance"]["warnings"])
                    status["health"]["recommendations"].append("Consider reducing external configuration size")

            except Exception as e:
                status["health"]["status"] = "error"
                status["health"]["issues"].append(f"Configuration loading error: {str(e)}")
        else:
            status["health"]["recommendations"].append("Create .ui-ux-pro-max-config/ directory to enable external configuration")

        return status

    def discover_config_files(self, config_path: Optional[str] = None) -> List[str]:
        """
        Discover available configuration files in directory structure

        Args:
            config_path: Custom path to search

        Returns:
            List of discovered configuration file paths
        """
        search_path = Path(config_path) if config_path else self.config_path
        discovered = []

        if not search_path.exists():
            return discovered

        # Find main config
        main_config = search_path / "config.json"
        if main_config.exists():
            discovered.append(str(main_config))

        # Find brand configs
        brand_dir = search_path / "brand"
        if brand_dir.exists():
            for json_file in brand_dir.glob("*.json"):
                discovered.append(str(json_file))

        # Find CSV files
        for csv_dir in ["domains", "stacks"]:
            dir_path = search_path / csv_dir
            if dir_path.exists():
                for csv_file in dir_path.glob("*.csv"):
                    discovered.append(str(csv_file))

        # Find reasoning files
        reasoning_dir = search_path / "reasoning"
        if reasoning_dir.exists():
            for json_file in reasoning_dir.glob("*.json"):
                discovered.append(str(json_file))

        return sorted(discovered)

    def cache_config(self, config: Dict, cache_key: str) -> None:
        """
        Cache validated configuration for performance

        Args:
            config: Configuration to cache
            cache_key: Key for cache storage
        """
        self.cache[cache_key] = {
            "config": config,
            "timestamp": datetime.now(),
            "path": str(self.config_path)
        }

    def get_cached_config(self, cache_key: str) -> Optional[Dict]:
        """
        Retrieve cached configuration if available and valid

        Args:
            cache_key: Key to retrieve from cache

        Returns:
            Cached configuration if valid, None otherwise
        """
        if cache_key not in self.cache:
            return None

        cached_data = self.cache[cache_key]
        cached_path = Path(cached_data["path"])

        # Check if configuration directory has been modified
        if cached_path.exists():
            current_mtime = cached_path.stat().st_mtime
            cached_mtime = cached_data["timestamp"].timestamp()

            if current_mtime <= cached_mtime:
                return cached_data["config"]

        # Cache is invalid, remove it
        del self.cache[cache_key]
        return None


# Convenience functions for backward compatibility
def load_external_config(config_path: Optional[str] = None) -> Dict:
    """Load external configuration (convenience function)"""
    loader = ConfigLoader(config_path)
    return loader.load_external_config()


def merge_with_builtin(external_config: Dict, builtin_data: Dict) -> Dict:
    """Merge external and built-in data (convenience function)"""
    loader = ConfigLoader()
    return loader.merge_with_builtin(external_config, builtin_data)


def validate_configuration(config: Dict) -> Dict:
    """Validate configuration (convenience function)"""
    loader = ConfigLoader()
    return loader.validate_configuration(config)


def get_config_status() -> Dict:
    """Get configuration status (convenience function)"""
    loader = ConfigLoader()
    return loader.get_config_status()