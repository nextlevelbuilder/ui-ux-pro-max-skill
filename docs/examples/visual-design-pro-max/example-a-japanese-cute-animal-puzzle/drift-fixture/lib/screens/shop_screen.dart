// SYNTHETIC FIXTURE — NOT RUNNABLE. Planted drift for the Example A audit demo:
//   (1) an off-palette purple promo colour, used twice on this primary screen
//   (2) a 13 px radius that is on no scale step (tile 12 / control 16)
//   (3) CtaButton: a second, divergent implementation of PrimaryButton
import 'package:flutter/material.dart';
import '../theme/app_tokens.dart';

class CtaButton extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const CtaButton({super.key, required this.label, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 56,
        decoration: BoxDecoration(
          color: const Color(0xFF8E24AA),                 // off-palette: purple is nowhere in tokens.json
          borderRadius: BorderRadius.circular(13),        // off-scale radius
        ),
        alignment: Alignment.center,
        child: Text(label, style: OgText.label.copyWith(color: OgColors.surface)),
      ),
    );
  }
}

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
              color: const Color(0xFF8E24AA),             // off-palette purple again (2nd occurrence)
              borderRadius: BorderRadius.circular(13),    // off-scale radius again
              border: Border.all(color: OgColors.primaryOutline, width: 3),
            ),
            child: Text('Starter pack', style: OgText.body.copyWith(color: OgColors.surface)),
          ),
          CtaButton(label: 'Buy', onTap: () {}),
        ],
      ),
    );
  }
}
