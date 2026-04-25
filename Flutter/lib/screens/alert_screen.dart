import 'package:flutter/material.dart';
import 'package:audioplayers/audioplayers.dart';

class AlertScreen extends StatefulWidget {
  const AlertScreen({super.key});

  @override
  State<AlertScreen> createState() => _AlertScreenState();
}

class _AlertScreenState extends State<AlertScreen> {
  final AudioPlayer _audioPlayer = AudioPlayer();

  @override
  void initState() {
    super.initState();
    _playSiren();
  }

  Future<void> _playSiren() async {
    // Play a siren sound. In a real app we'd bundle an asset. 
    // Here we can use a generated beep or an asset if we have one.
    // For the hackathon, we'll try to play a high pitched beep or just mock the sound player.
    // We'll set a loop mode.
    await _audioPlayer.setReleaseMode(ReleaseMode.loop);
    // As a mock for the demo, we will just use a beep asset or skip if not available,
    // assuming there's an asset or we will just let it be silent if missing.
    // Let's assume there is an asset "siren.mp3" eventually, for now we will just mock the call.
    // _audioPlayer.play(AssetSource('siren.mp3')); 
  }

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

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
                  Navigator.pop(context, true); // Go back and indicate evacuation started
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
                  'START EVACUATION',
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
