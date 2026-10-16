// SYNTHETIC FIXTURE — NOT RUNNABLE. The one canonical primary button (component.button.primary).
import 'package:flutter/material.dart';
import '../theme/app_tokens.dart';

class PrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const PrimaryButton({super.key, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: OgColors.primary,                                   // component.button.primary.bg
      borderRadius: BorderRadius.circular(OgRadius.control),     // component.button.primary.radius -> 16
      child: InkWell(
        onTap: onTap,
        child: Container(
          height: 56,                                            // component.button.primary.height
          padding: const EdgeInsets.symmetric(horizontal: 24),   // component.button.primary.paddingX = spacing.6
          decoration: BoxDecoration(
            border: Border.all(color: OgColors.primaryOutline, width: 3), // semantic.outline.control = 3
            borderRadius: BorderRadius.circular(OgRadius.control),
          ),
          alignment: Alignment.center,
          child: Text(label, style: OgText.label.copyWith(color: OgColors.onPrimary)),
        ),
      ),
    );
  }
}
