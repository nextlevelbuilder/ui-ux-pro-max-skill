// SYNTHETIC FIXTURE — NOT RUNNABLE. Fixed copy of drift-fixture/lib/screens/shop_screen.dart:
//   (1) promo colour -> OgColors.accent (semantic.color.accent, the contract's saturated CTA/reward accent)
//   (2) 13 px radius -> OgRadius.control (semantic.radius.control = 16)
//   (3) CtaButton deleted; the screen uses the shared PrimaryButton
import 'package:flutter/material.dart';
import '../theme/app_tokens.dart';
import '../widgets/primary_button.dart';

class ShopScreen extends StatelessWidget {
  const ShopScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: OgColors.background,
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Text('Shop', style: OgText.title),
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: OgColors.accent,                                    // semantic.color.accent #FFD23F
              borderRadius: BorderRadius.circular(OgRadius.control),     // semantic.radius.control = 16
              border: Border.all(color: OgColors.primaryOutline, width: 3),
            ),
            child: Text('Starter pack', style: OgText.body),
          ),
          PrimaryButton(label: 'Buy', onTap: () {}),
        ],
      ),
    );
  }
}
