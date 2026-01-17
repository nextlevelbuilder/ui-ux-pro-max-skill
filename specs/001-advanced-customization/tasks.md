# Tasks: Advanced Customization Architecture

**Input**: Design documents from `/specs/001-advanced-customization/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the feature specification. Focus on implementation tasks that deliver user value.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **CLI skill extension**: `.claude/skills/ui-ux-pro-max/scripts/`, `.claude/skills/ui-ux-pro-max/data/`
- **External configuration**: `.ui-ux-pro-max-config/` directory structure
- **Examples**: `.claude/skills/ui-ux-pro-max/examples/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure extending existing UI/UX Pro Max skill

- [ ] T001 Create new data CSV files for platforms: data/stacks/htmx-alpine-axum.csv
- [ ] T002 [P] Create new data CSV files for platforms: data/stacks/tauri.csv
- [ ] T003 [P] Create new domain CSV file: data/ai-chat.csv
- [ ] T004 [P] Create new domain CSV file: data/architecture.csv
- [ ] T005 [P] Create examples directory structure: examples/external-config/.ui-ux-pro-max-config/
- [ ] T006 [P] Create example brand configuration: examples/external-config/.ui-ux-pro-max-config/brand/brand.json
- [ ] T007 [P] Create example main configuration: examples/external-config/.ui-ux-pro-max-config/config.json
- [ ] T008 [P] Create README for examples: examples/external-config/README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core modules that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Create config_loader.py module: .claude/skills/ui-ux-pro-max/scripts/config_loader.py
- [ ] T010 [P] Create brand_processor.py module: .claude/skills/ui-ux-pro-max/scripts/brand_processor.py
- [ ] T011 [P] Create a2ui_exporter.py module: .claude/skills/ui-ux-pro-max/scripts/a2ui_exporter.py (for FR-015)
- [ ] T012 Extend core.py to support external configuration loading: .claude/skills/ui-ux-pro-max/scripts/core.py
- [ ] T013 Extend search.py CLI to support external configuration options: .claude/skills/ui-ux-pro-max/scripts/search.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - External Configuration Management (Priority: P1) 🎯 MVP

**Goal**: Developers can customize the UI/UX Pro Max skill without modifying core files by placing configuration files in an external directory structure

**Independent Test**: Can be fully tested by creating a `.ui-ux-pro-max-config/` directory with custom CSV files and verifying the skill loads and uses these external configurations while preserving core functionality

### Implementation for User Story 1

- [ ] T014 [P] [US1] Implement load_external_config() function in .claude/skills/ui-ux-pro-max/scripts/config_loader.py
- [ ] T015 [P] [US1] Implement validate_configuration() function in .claude/skills/ui-ux-pro-max/scripts/config_loader.py
- [ ] T016 [US1] Implement merge_with_builtin() function in .claude/skills/ui-ux-pro-max/scripts/config_loader.py (depends on T014, T015)
- [ ] T017 [US1] Implement get_config_status() function in .claude/skills/ui-ux-pro-max/scripts/config_loader.py
- [ ] T018 [P] [US1] Implement discover_config_files() utility function in .claude/skills/ui-ux-pro-max/scripts/config_loader.py
- [ ] T019 [P] [US1] Implement cache_config() and get_cached_config() functions in .claude/skills/ui-ux-pro-max/scripts/config_loader.py
- [ ] T020 [US1] Integrate external configuration loading into search_domains() in .claude/skills/ui-ux-pro-max/scripts/core.py
- [ ] T021 [US1] Add external configuration CLI options to .claude/skills/ui-ux-pro-max/scripts/search.py
- [ ] T022 [US1] Implement permissive validation with clear warning messages (FR-004)
- [ ] T023 [US1] Implement merge strategy for configuration conflicts (FR-005)

**Checkpoint**: At this point, User Story 1 should be fully functional - users can place custom domains/stacks in external configuration and see them in search results

---

## Phase 4: User Story 2 - New Platform Support (Priority: P2)

**Goal**: Developers working with modern web stacks can receive platform-specific UI/UX guidance for HTMX + Alpine.js + Axum applications and Tauri desktop applications

**Independent Test**: Can be fully tested by requesting design guidance for "HTMX application" or "Tauri desktop app" and receiving platform-specific recommendations

### Implementation for User Story 2

- [ ] T024 [P] [US2] Populate HTMX + Alpine.js + Axum platform data in data/stacks/htmx-alpine-axum.csv (72 guidelines from research)
- [ ] T025 [P] [US2] Populate Tauri desktop platform data in data/stacks/tauri.csv (60 guidelines from research)
- [ ] T026 [US2] Add HTMX stack support to stack search logic in .claude/skills/ui-ux-pro-max/scripts/core.py
- [ ] T027 [US2] Add Tauri stack support to stack search logic in .claude/skills/ui-ux-pro-max/scripts/core.py
- [ ] T028 [US2] Validate platform coverage meets SC-003 requirement (40+ guidelines per platform)
- [ ] T029 [US2] Add platform-specific code examples and anti-patterns (FR-006, FR-007)

**Checkpoint**: At this point, HTMX and Tauri platform searches should return comprehensive platform-specific guidance

---

## Phase 5: User Story 3 - Personal Brand Integration (Priority: P2)

**Goal**: Developers and designers can define their personal or company brand preferences and have all design system recommendations automatically incorporate these brand elements

**Independent Test**: Can be fully tested by creating a brand configuration file, requesting design recommendations, and verifying all suggestions use the specified brand colors, fonts, and style preferences

### Implementation for User Story 3

- [ ] T030 [P] [US3] Implement apply_brand_config() function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py
- [ ] T031 [P] [US3] Implement extract_brand_colors() function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py
- [ ] T032 [P] [US3] Implement apply_brand_typography() function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py
- [ ] T033 [P] [US3] Implement filter_by_style_preferences() function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py
- [ ] T034 [US3] Implement generate_brand_aware_examples() function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py
- [ ] T035 [US3] Implement validate_brand_config() function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py
- [ ] T036 [P] [US3] Implement calculate_color_variants() utility function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py
- [ ] T037 [P] [US3] Implement check_color_accessibility() utility function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py
- [ ] T038 [P] [US3] Implement generate_css_variables() utility function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py
- [ ] T039 [US3] Integrate brand processing into search workflow in .claude/skills/ui-ux-pro-max/scripts/core.py
- [ ] T040 [US3] Add brand configuration support to CLI in .claude/skills/ui-ux-pro-max/scripts/search.py
- [ ] T041 [US3] Implement required colors and typography sections validation (FR-008)
- [ ] T042 [US3] Ensure brand affects 100% of design system generations (SC-002)

**Checkpoint**: At this point, brand configuration should automatically modify all design recommendations with user's brand elements

---

## Phase 6: User Story 4 - AI Chat Interface Components (Priority: P3)

**Goal**: Developers building AI-powered applications can access specialized UI patterns for chat interfaces, including thinking displays, tool call visualizations, and citation displays

**Independent Test**: Can be fully tested by requesting "AI chat interface" design guidance and receiving specific components like thinking bubbles, tool execution displays, and confidence indicators

### Implementation for User Story 4

- [ ] T043 [P] [US4] Populate AI chat interface components in data/ai-chat.csv (25 patterns from research)
- [ ] T044 [US4] Add ai-chat domain support to domain search logic in .claude/skills/ui-ux-pro-max/scripts/core.py
- [ ] T045 [US4] Implement AI-specific search terms and categorization (FR-010)
- [ ] T046 [US4] Validate AI component coverage meets SC-004 requirement (15+ specialized patterns)
- [ ] T047 [US4] Add thinking displays and tool call visualization patterns

**Checkpoint**: At this point, AI chat interface searches should return 15+ specialized patterns not available elsewhere

---

## Phase 7: User Story 5 - Advanced State Management Integration (Priority: P3)

**Goal**: Developers using modern state management libraries can receive specific guidance for Zustand, Riverpod, Jotai, and other advanced state management patterns

**Independent Test**: Can be fully tested by requesting React state management guidance and receiving specific recommendations for Zustand global state patterns or Flutter guidance with Riverpod integration

### Implementation for User Story 5

- [ ] T048 [P] [US5] Add advanced state management patterns for Zustand in data/stacks/react.csv
- [ ] T049 [P] [US5] Add advanced state management patterns for Riverpod in data/stacks/flutter.csv
- [ ] T050 [P] [US5] Add advanced state management patterns for Jotai in data/stacks/react.csv
- [ ] T051 [US5] Enhance state management search logic in .claude/skills/ui-ux-pro-max/scripts/core.py
- [ ] T052 [US5] Validate state management coverage meets SC-005 requirement (3+ libraries per framework)
- [ ] T053 [US5] Add specific code examples for advanced patterns (FR-011)

**Checkpoint**: At this point, state management searches should return specific guidance for modern state management libraries

---

## Phase 8: User Story 6 - Clean Architecture Pattern Integration (Priority: P3)

**Goal**: Developers implementing clean architecture can receive guidance on feature-based organization, hexagonal architecture, and domain-driven design patterns

**Independent Test**: Can be fully tested by requesting guidance for "feature-based architecture" and receiving recommendations for organizing UI components within feature slices

### Implementation for User Story 6

- [ ] T054 [P] [US6] Populate clean architecture patterns in data/architecture.csv
- [ ] T055 [US6] Add architecture domain support to domain search logic in .claude/skills/ui-ux-pro-max/scripts/core.py
- [ ] T056 [US6] Implement feature-based organization patterns (FR-012)
- [ ] T057 [US6] Implement hexagonal architecture patterns (FR-012)
- [ ] T058 [US6] Validate architecture coverage meets SC-006 requirement
- [ ] T059 [US6] Add UI integration guidance for architecture patterns

**Checkpoint**: At this point, clean architecture searches should return comprehensive guidance for feature-based, hexagonal, and DDD patterns

---

## Phase 9: A2UI Export Support (Cross-Cutting)

**Goal**: Support export to A2UI protocol format for declarative UI specification and cross-platform rendering (FR-015)

### Implementation for A2UI Export

- [ ] T060 [P] Implement export_to_a2ui() function in .claude/skills/ui-ux-pro-max/scripts/a2ui_exporter.py
- [ ] T061 [P] Implement extract_design_system() function in .claude/skills/ui-ux-pro-max/scripts/a2ui_exporter.py
- [ ] T062 [P] Implement convert_components_to_a2ui() function in .claude/skills/ui-ux-pro-max/scripts/a2ui_exporter.py
- [ ] T063 [P] Implement generate_responsive_specifications() function in .claude/skills/ui-ux-pro-max/scripts/a2ui_exporter.py
- [ ] T064 [P] Implement generate_accessibility_specs() function in .claude/skills/ui-ux-pro-max/scripts/a2ui_exporter.py
- [ ] T065 [P] Implement export_for_platform() function for React, Vue, Flutter platforms in .claude/skills/ui-ux-pro-max/scripts/a2ui_exporter.py
- [ ] T066 Integrate A2UI export into CLI with --export-a2ui option in .claude/skills/ui-ux-pro-max/scripts/search.py
- [ ] T067 Add A2UI validation and optimization functions in .claude/skills/ui-ux-pro-max/scripts/a2ui_exporter.py

**Checkpoint**: A2UI export functionality should be available via CLI option

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [ ] T068 [P] Implement backward compatibility validation (SC-007)
- [ ] T069 [P] Implement performance monitoring and warnings for large configurations (SC-008)
- [ ] T070 [P] Add comprehensive error handling and logging across all modules
- [ ] T071 [P] Validate sub-second response times for configurations under 1000 entries
- [ ] T072 Create comprehensive documentation updates in examples/external-config/README.md
- [ ] T073 [P] Implement hyperpersonalization session tracking (FR-014)
- [ ] T074 [P] Add file watching for configuration changes
- [ ] T075 Run quickstart.md validation scenarios
- [ ] T076 Final integration testing across all user stories
- [ ] T077 Performance optimization and caching improvements

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P2 → P3 → P3 → P3)
- **A2UI Export (Phase 9)**: Can run in parallel with user stories after Foundational
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - FOUNDATION for all customization
- **User Story 2 (P2)**: Can start after Foundational - Independent of other stories
- **User Story 3 (P2)**: Can start after Foundational - Independent of other stories
- **User Story 4 (P3)**: Can start after Foundational - Independent of other stories
- **User Story 5 (P3)**: Can start after Foundational - Independent of other stories
- **User Story 6 (P3)**: Can start after Foundational - Independent of other stories

### Within Each User Story

- Core module functions before integration
- Validation before implementation
- CLI integration after core functionality
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel
- Within each user story, tasks marked [P] can run in parallel
- A2UI export tasks marked [P] can run in parallel

---

## Parallel Example: User Story 3 (Brand Integration)

```bash
# Launch core brand processing functions in parallel:
Task: "Implement extract_brand_colors() function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py"
Task: "Implement apply_brand_typography() function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py"
Task: "Implement filter_by_style_preferences() function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py"

# Launch utility functions in parallel:
Task: "Implement calculate_color_variants() utility function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py"
Task: "Implement check_color_accessibility() utility function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py"
Task: "Implement generate_css_variables() utility function in .claude/skills/ui-ux-pro-max/scripts/brand_processor.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (External Configuration Management)
4. **STOP and VALIDATE**: Test external configuration loading independently
5. Deploy/demo with basic external configuration support

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Stories 2 & 3 (P2) → Test independently → Deploy/Demo
4. Add User Stories 4, 5 & 6 (P3) → Test independently → Deploy/Demo
5. Add A2UI Export → Deploy/Demo
6. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (External Configuration)
   - Developer B: User Story 2 (Platform Support)
   - Developer C: User Story 3 (Brand Integration)
   - Developer D: A2UI Export (can start early)
3. Stories complete and integrate independently

---

## Success Criteria Validation

### Key Measurements

- **SC-001**: External configuration setup time < 5 minutes (validate via quickstart.md)
- **SC-002**: Brand configuration affects 100% of design system generations (validate in T042)
- **SC-003**: 40+ guidelines per platform (validate in T028 for HTMX/Tauri)
- **SC-004**: 15+ AI-specific patterns (validate in T046)
- **SC-005**: 3+ libraries per framework (validate in T052)
- **SC-006**: Architecture guidance coverage (validate in T058)
- **SC-007**: 100% backward compatibility (validate in T068)
- **SC-008**: Sub-second response times <1000 entries (validate in T071)

### Independent Test Criteria

Each user story includes specific acceptance scenarios that can be validated independently without requiring other stories to be complete.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are not explicitly requested - focus on implementation that delivers user value
- Maintain Python 3.7+ compatibility and zero external dependencies throughout