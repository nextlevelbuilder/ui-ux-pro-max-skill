// SYNTHETIC FIXTURE — NOT RUNNABLE. Clean screen: tokens + the shared PrimaryButton only.
import 'package:flutter/material.dart';
import '../theme/app_tokens.dart';
import '../widgets/primary_button.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: OgColors.background,
      padding: const EdgeInsets.all(16), // semantic.spacing.screenGutter = spacing.4
      child: Column(
        children: [
          Text('Onet Garden', style: OgText.title),
          PrimaryButton(label: 'Play', onTap: () {}),
        ],
      ),
    );
  }
}
