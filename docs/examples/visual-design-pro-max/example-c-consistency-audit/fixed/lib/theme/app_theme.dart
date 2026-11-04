// FIXTURE: token definitions — every literal here matches tokens.json (clean file)
import 'package:flutter/material.dart';

class AppColors {
  static const primary = Color(0xFF3B5BDB);
  static const onPrimary = Color(0xFFFFFFFF);
  static const accent = Color(0xFFFF8A4C);
  static const background = Color(0xFFFFF8F0);
  static const surface = Color(0xFFFFFFFF);
  static const text = Color(0xFF1A1A2E);
  static const textMuted = Color(0xFF6B6B80);
  static const reward = Color(0xFFFFD43B);
  static const danger = Color(0xFFE03E3E);
}

class AppRadius {
  static final sm = BorderRadius.circular(4);
  static final md = BorderRadius.circular(8);
  static final lg = BorderRadius.circular(16);
  static final pill = BorderRadius.circular(9999);
}

class AppText {
  static const body = TextStyle(fontFamily: 'Nunito', fontSize: 16, color: AppColors.text);
  static const caption = TextStyle(fontFamily: 'Nunito', fontSize: 12, color: AppColors.textMuted);
  static const title = TextStyle(fontFamily: 'Fredoka', fontSize: 24, color: AppColors.text);
}

class AppShadows {
  static const card = BoxShadow(color: Color(0x1A000000), blurRadius: 8, offset: Offset(0, 2));
  static const button = BoxShadow(color: Color(0x33000000), blurRadius: 4, offset: Offset(0, 4));
}

class AppMotion {
  static const fast = Duration(milliseconds: 120);
  static const base = Duration(milliseconds: 200);
  static const slow = Duration(milliseconds: 350);
}
