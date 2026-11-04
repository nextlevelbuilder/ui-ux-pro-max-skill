// FIXTURE: duplicate component implementation. MainButton below re-implements
// lib/widgets/primary_button.dart (PrimaryButton) with a different body.
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class MainButton extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const MainButton({super.key, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(color: AppColors.primary, borderRadius: AppRadius.lg),
        padding: const EdgeInsets.all(16),
        child: Text(label, style: AppText.body),
      ),
    );
  }
}

class RewardsScreen extends StatelessWidget {
  const RewardsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Rewards', style: AppText.title),
        MainButton(label: 'Claim', onTap: () {}),
      ],
    );
  }
}
