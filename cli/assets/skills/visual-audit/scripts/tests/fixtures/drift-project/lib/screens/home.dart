// FIXTURE: clean primary screen — uses only theme references. Expected findings: none
// (the only icon library in this file is Material; mixing is introduced by shop.dart).
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/primary_button.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text('Home', style: AppText.title),
        leading: const Icon(Icons.home), // see https://example.com/not-a-comment-trap
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const SizedBox(height: 24),
            Text('Welcome back', style: AppText.body),
            const SizedBox(height: 8),
            PrimaryButton(label: 'Play', onTap: () {}),
          ],
        ),
      ),
    );
  }
}
