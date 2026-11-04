// FIXTURE: primary screen with intentional drift (see expected-findings.md)
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart'; // icon.mixed-libraries (material + font_awesome)
import '../theme/app_theme.dart';

class ShopScreen extends StatelessWidget {
  const ShopScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFFE91E63), // color.off-palette (pink, nowhere in tokens)
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 10), // spacing.off-scale x2
      child: Column(
        children: [
          Container(
            decoration: BoxDecoration(
              color: const Color(0xFFFF8B4D), // color.near-duplicate of accent #FF8A4C
              borderRadius: BorderRadius.circular(13), // radius.off-scale
              boxShadow: const [
                BoxShadow(color: Color(0x40000000), blurRadius: 13, offset: Offset(0, 5)), // 3rd distinct shadow
              ],
            ),
            child: Text(
              'Daily deal',
              style: const TextStyle(fontFamily: 'Comic Sans MS', fontSize: 15), // font-family.unlisted + font-size.off-scale
            ),
          ),
          const Icon(FontAwesomeIcons.cartShopping),
          SizedBox(
            width: 32, height: 32, // touch.target-too-small (heuristic)
            child: IconButton(icon: const Icon(Icons.close), onPressed: () {}),
          ),
          Container(color: const Color(0x66000000)), // translucent black scrim: NOT a finding
          AnimatedOpacity(opacity: 1, duration: const Duration(milliseconds: 337)), // duration.off-scale
        ],
      ),
    );
  }
}
