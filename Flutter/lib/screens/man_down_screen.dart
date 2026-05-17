import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:latlong2/latlong.dart';

import '../services/backend_service.dart';
import '../theme.dart';

class ManDownScreen extends StatefulWidget {
  const ManDownScreen({
    super.key,
    required this.workerPosition,
    required this.alertId,
  });

  final LatLng workerPosition;
  final String? alertId;

  @override
  State<ManDownScreen> createState() => _ManDownScreenState();
}

class _ManDownScreenState extends State<ManDownScreen>
    with SingleTickerProviderStateMixin {
  static const int _initialCountdown = 30;
  int _remaining = _initialCountdown;
  Timer? _ticker;
  late final AnimationController _pulse;
  bool _resolved = false;
  final FlutterTts _tts = FlutterTts();

  @override
  void initState() {
    super.initState();
    _pulse = AnimationController(
      duration: const Duration(milliseconds: 900),
      vsync: this,
    )..repeat(reverse: true);
    _tts.setLanguage('en-US');
    _tts.setPitch(1.0);
    _speakSos();
    _vibrate();
    _ticker = Timer.periodic(const Duration(seconds: 1), _onTick);
  }

  @override
  void dispose() {
    _ticker?.cancel();
    _pulse.dispose();
    _tts.stop();
    super.dispose();
  }

  Future<void> _speakSos() async {
    await _tts.speak(
      'Man-down detected. SOS will be transmitted in 30 seconds. Tap I am fine to cancel.',
    );
  }

  Future<void> _vibrate() async {
    HapticFeedback.heavyImpact();
    await Future.delayed(const Duration(milliseconds: 200));
    HapticFeedback.heavyImpact();
  }

  void _onTick(Timer timer) {
    if (!mounted) return;
    setState(() {
      if (_remaining > 0) {
        _remaining--;
        if (_remaining == 0) {
          _vibrate();
        }
      }
    });
  }

  Future<void> _markFine() async {
    if (_resolved) return;
    _resolved = true;
    _ticker?.cancel();
    final backend = BackendService();
    await backend.postUserStatus(widget.workerPosition, 'Safe');
    if (widget.alertId != null) {
      await backend.cancelAlert(widget.alertId!);
    } else {
      await backend.cancelLatestAlert();
    }
    if (!mounted) return;
    Navigator.of(context).pop(ManDownResult.cleared);
  }

  Future<void> _dismiss() async {
    _ticker?.cancel();
    if (!mounted) return;
    Navigator.of(context).pop(ManDownResult.dismissed);
  }

  @override
  Widget build(BuildContext context) {
    final lat = widget.workerPosition.latitude.toStringAsFixed(5);
    final lng = widget.workerPosition.longitude.toStringAsFixed(5);
    final dispatched = _remaining == 0;

    return PopScope(
      canPop: false,
      child: Scaffold(
        backgroundColor: const Color(0xFF7F1D1D),
        body: SafeArea(
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.white.withOpacity(0.12),
                        borderRadius: BorderRadius.circular(999),
                      ),
                      child: const Text(
                        'EMERGENCY',
                        style: TextStyle(
                          color: Colors.white,
                          letterSpacing: 1.4,
                          fontWeight: FontWeight.w800,
                          fontSize: 11,
                        ),
                      ),
                    ),
                    const Spacer(),
                    IconButton(
                      icon: const Icon(Icons.close, color: Colors.white70),
                      onPressed: _dismiss,
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      _pulseHalo(),
                      const SizedBox(height: 32),
                      const Text(
                        'MAN-DOWN ALERT',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 28,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 0.5,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        dispatched
                            ? 'SOS dispatched. Help is on the way.'
                            : 'Zero movement detected.',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.85),
                          fontSize: 15,
                        ),
                      ),
                      const SizedBox(height: 32),
                      _countdownRing(dispatched),
                      const SizedBox(height: 32),
                      _locationCard(lat, lng),
                    ],
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
                child: Column(
                  children: [
                    SizedBox(
                      width: double.infinity,
                      height: 64,
                      child: FilledButton.icon(
                        style: FilledButton.styleFrom(
                          backgroundColor: AppTheme.safeGreen,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(20),
                          ),
                        ),
                        onPressed: _markFine,
                        icon: const Icon(Icons.health_and_safety, size: 28),
                        label: const Text(
                          "I'M FINE — CANCEL SOS",
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextButton(
                      onPressed: _dismiss,
                      child: const Text(
                        'Dismiss screen (keep alert)',
                        style: TextStyle(color: Colors.white70),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _pulseHalo() {
    return AnimatedBuilder(
      animation: _pulse,
      builder: (context, _) {
        final scale = 1.0 + 0.25 * _pulse.value;
        return Stack(
          alignment: Alignment.center,
          children: [
            Transform.scale(
              scale: scale * 1.6,
              child: Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.06),
                  shape: BoxShape.circle,
                ),
              ),
            ),
            Transform.scale(
              scale: scale * 1.25,
              child: Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.12),
                  shape: BoxShape.circle,
                ),
              ),
            ),
            Container(
              width: 96,
              height: 96,
              decoration: const BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.medical_services,
                color: Color(0xFF7F1D1D),
                size: 48,
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _countdownRing(bool dispatched) {
    final progress = dispatched ? 1.0 : (_initialCountdown - _remaining) / _initialCountdown;
    return SizedBox(
      width: 160,
      height: 160,
      child: Stack(
        alignment: Alignment.center,
        children: [
          SizedBox(
            width: 160,
            height: 160,
            child: CircularProgressIndicator(
              value: progress,
              strokeWidth: 10,
              backgroundColor: Colors.white.withOpacity(0.15),
              valueColor: const AlwaysStoppedAnimation(Colors.white),
            ),
          ),
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                dispatched ? 'SENT' : '$_remaining',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 56,
                  fontWeight: FontWeight.w900,
                ),
              ),
              if (!dispatched)
                Text(
                  'seconds',
                  style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 13),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _locationCard(String lat, String lng) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 24),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.10),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: Colors.white.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          const Icon(Icons.location_on, color: Colors.white),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Last known position',
                  style: TextStyle(color: Colors.white70, fontSize: 11),
                ),
                Text(
                  '$lat, $lng',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ],
            ),
          ),
          if (widget.alertId != null)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.15),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                widget.alertId!.substring(0, widget.alertId!.length.clamp(0, 8)),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
        ],
      ),
    );
  }
}

enum ManDownResult { cleared, dismissed }
