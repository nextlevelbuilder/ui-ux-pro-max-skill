// FIXTURE: canonical button widget (clean). Participates in component.duplicate-implementation
// because lib/screens/rewards.dart re-implements the same component as MainButton.
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class PrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const PrimaryButton({super.key, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.primary,
      borderRadius: AppRadius.pill,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          child: Text(label, style: AppText.body.copyWith(color: AppColors.onPrimary)),
        ),
      ),
    );
  }
}
