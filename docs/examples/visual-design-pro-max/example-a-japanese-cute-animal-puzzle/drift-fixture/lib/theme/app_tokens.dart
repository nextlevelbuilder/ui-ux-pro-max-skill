// SYNTHETIC FIXTURE — NOT RUNNABLE. Hand-written mirror of design-system/onet-garden/tokens.json
// (clean file: every literal here equals a contract value; the scanner must report nothing).
import 'package:flutter/material.dart';

class OgColors {
  static const primary = Color(0xFFFF8FAB);        // semantic.color.primary  = primitive.color.brand.500
  static const onPrimary = Color(0xFF2E2A32);      // semantic.color.onPrimary = primitive.color.neutral.900
  static const primaryOutline = Color(0xFF972743); // primitive.color.brand.800 (component.button.primary.outlineColor)
  static const accent = Color(0xFFFFD23F);         // semantic.color.accent = primitive.color.accent.500
  static const reward = Color(0xFFFFC83D);         // semantic.color.reward (split from warning #F5A524)
  static const background = Color(0xFFFFF6E9);     // semantic.color.background (palette.surfaces.background)
  static const surface = Color(0xFFFFFFFF);        // semantic.color.surface
  static const border = Color(0xFFFFDDAC);         // semantic.color.border (follows the outline rule)
  static const text = Color(0xFF4A3B5C);           // semantic.color.text (palette.surfaces.text)
  static const textMuted = Color(0xFF6B6274);      // semantic.color.textMuted
  static const neutralOutline = Color(0xFF56505E); // primitive.color.neutral.700 (tile / chip outline)
}

class OgRadius {
  static const tile = 12.0;      // semantic.radius.tile      = primitive.radius.lg
  static const control = 16.0;   // semantic.radius.control   = primitive.radius.xl
  static const container = 24.0; // semantic.radius.container = primitive.radius.2xl
  static const popup = 32.0;     // semantic.radius.popup     = primitive.radius.3xl
  static const chip = 9999.0;    // semantic.radius.chip      = primitive.radius.full
}

class OgText {
  static const title = TextStyle(fontFamily: 'Fredoka', fontSize: 28, fontWeight: FontWeight.w700, color: OgColors.text);
  static const body = TextStyle(fontFamily: 'Nunito', fontSize: 16, fontWeight: FontWeight.w500, color: OgColors.text);
  static const label = TextStyle(fontFamily: 'Nunito', fontSize: 14, fontWeight: FontWeight.w600, color: OgColors.text);
  static const caption = TextStyle(fontFamily: 'Nunito', fontSize: 12, fontWeight: FontWeight.w500, color: OgColors.textMuted);
}

class OgMotion {
  static const fast = Duration(milliseconds: 120); // primitive.duration.fast
  static const base = Duration(milliseconds: 200); // primitive.duration.base
  static const slow = Duration(milliseconds: 350); // primitive.duration.slow
}
