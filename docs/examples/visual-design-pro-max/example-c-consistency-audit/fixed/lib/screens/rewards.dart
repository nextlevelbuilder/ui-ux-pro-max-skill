// FIXED COPY (Example C): MainButton removed; the screen reuses the canonical PrimaryButton.
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/primary_button.dart';

class RewardsScreen extends StatelessWidget {
  const RewardsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Rewards', style: AppText.title),
        PrimaryButton(label: 'Claim', onTap: () {}),
      ],
    );
  }
}
