import 'package:flutter/material.dart';

import '../theme.dart';

class RiskStyle {
  RiskStyle._();

  static const _classes = {
    'extreme': _Style(
      label: 'EXTREME',
      color: AppTheme.emergencyRed,
      icon: Icons.dangerous,
      gradient: [Color(0xFFEF4444), Color(0xFFB91C1C)],
    ),
    'high': _Style(
      label: 'HIGH',
      color: AppTheme.riskOrange,
      icon: Icons.warning_amber_rounded,
      gradient: [Color(0xFFF97316), Color(0xFFC2410C)],
    ),
    'medium': _Style(
      label: 'MEDIUM',
      color: AppTheme.monitorYellow,
      icon: Icons.error_outline,
      gradient: [Color(0xFFF59E0B), Color(0xFFB45309)],
    ),
    'low': _Style(
      label: 'LOW',
      color: AppTheme.safeGreen,
      icon: Icons.check_circle_outline,
      gradient: [Color(0xFF10B981), Color(0xFF047857)],
    ),
    'minimal': _Style(
      label: 'MINIMAL',
      color: Color(0xFF6B7280),
      icon: Icons.shield_outlined,
      gradient: [Color(0xFF94A3B8), Color(0xFF475569)],
    ),
  };

  static Color color(String? riskClass) => _classes[riskClass]?.color ?? AppTheme.lightText;
  static IconData icon(String? riskClass) => _classes[riskClass]?.icon ?? Icons.help_outline;
  static String label(String? riskClass) => _classes[riskClass]?.label ?? 'UNKNOWN';
  static List<Color> gradient(String? riskClass) =>
      _classes[riskClass]?.gradient ?? const [Color(0xFF94A3B8), Color(0xFF475569)];
}

class _Style {
  const _Style({
    required this.label,
    required this.color,
    required this.icon,
    required this.gradient,
  });

  final String label;
  final Color color;
  final IconData icon;
  final List<Color> gradient;
}
