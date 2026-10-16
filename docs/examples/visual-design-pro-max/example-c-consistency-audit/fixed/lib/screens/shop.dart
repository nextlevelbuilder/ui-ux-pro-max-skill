// FIXED COPY (Example C): every literal from the drift version replaced by a theme reference.
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class ShopScreen extends StatelessWidget {
  const ShopScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: AppColors.primary,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        children: [
          Container(
            decoration: BoxDecoration(
              color: AppColors.accent,
              borderRadius: AppRadius.lg,
              boxShadow: const [AppShadows.card],
            ),
            child: Text('Daily deal', style: AppText.body),
          ),
          const Icon(Icons.shopping_cart),
          SizedBox(
            width: 48, height: 48,
            child: IconButton(icon: const Icon(Icons.close), onPressed: () {}),
          ),
          Container(color: const Color(0x66000000)), // translucent black scrim: allowed
          AnimatedOpacity(opacity: 1, duration: AppMotion.slow),
        ],
      ),
    );
  }
}
