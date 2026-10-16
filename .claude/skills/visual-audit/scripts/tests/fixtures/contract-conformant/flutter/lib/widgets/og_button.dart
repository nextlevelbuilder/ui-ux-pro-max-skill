import 'package:flutter/material.dart';
class OgButton extends StatelessWidget {
  const OgButton({super.key});
  @override
  Widget build(BuildContext context) => AnimatedContainer(
        duration: const Duration(milliseconds: 90),
        decoration: BoxDecoration(color: const Color(0xFFBA4A66), borderRadius: BorderRadius.circular(16)),
        child: const Text('Play', style: TextStyle(color: Color(0xFFFFFFFF), fontSize: 22)),
      );
}
