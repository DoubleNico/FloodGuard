import 'package:flutter/material.dart';

class AlertScreen extends StatelessWidget {
  const AlertScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFE50014), // Strong red background
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 40.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 40),
              // White circular icon with red warning
              Container(
                width: 100,
                height: 100,
                decoration: const BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                ),
                child: const Center(
                  child: Icon(
                    Icons.warning_amber_rounded,
                    color: Color(0xFFE50014),
                    size: 60,
                  ),
                ),
              ),
              const SizedBox(height: 32),
              // Warning Title
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: const [
                  Text('⚠️', style: TextStyle(fontSize: 32)),
                  SizedBox(width: 12),
                  Text(
                    'FLOOD\nWARNING',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      height: 1.2,
                    ),
                  ),
                  SizedBox(width: 12),
                  Text('⚠️', style: TextStyle(fontSize: 32)),
                ],
              ),
              const SizedBox(height: 40),
              // Info Box
              Container(
                padding: const EdgeInsets.all(24.0),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: Colors.white, width: 1.5),
                ),
                child: Column(
                  children: [
                    RichText(
                      textAlign: TextAlign.center,
                      text: const TextSpan(
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          height: 1.4,
                        ),
                        children: [
                          TextSpan(text: 'There is a '),
                          TextSpan(
                            text: 'HIGH RISK',
                            style: TextStyle(decoration: TextDecoration.underline),
                          ),
                          TextSpan(text: ' of flooding\nin your area.'),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'Please seek higher ground\nor a safe place\nimmediately.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 22,
                        fontWeight: FontWeight.w600,
                        height: 1.4,
                      ),
                    ),
                    const SizedBox(height: 24),
                    const Text(
                      'Check the map for safe locations\nmarked nearby.',
                      textAlign: TextAlign.center,
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
              const Spacer(),
              // Buttons
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(context); // Go back to map
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: const Color(0xFFE50014),
                  minimumSize: const Size(double.infinity, 56),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'View Map & Safe Locations',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(height: 16),
              OutlinedButton(
                onPressed: () {
                  // Logic to call emergency services
                },
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Colors.white, width: 2),
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 56),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text(
                  'Call Emergency Services',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
