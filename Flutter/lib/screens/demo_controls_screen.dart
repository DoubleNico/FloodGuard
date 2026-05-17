import 'package:flutter/material.dart';
import 'package:latlong2/latlong.dart';

import '../services/backend_service.dart';
import '../theme.dart';
import '../utils/risk_style.dart';

class DemoControlsScreen extends StatefulWidget {
  const DemoControlsScreen({super.key});

  @override
  State<DemoControlsScreen> createState() => _DemoControlsScreenState();
}

class _DemoControlsScreenState extends State<DemoControlsScreen> {
  final BackendService _backend = BackendService();
  bool _loadingSites = true;
  bool _busy = false;
  List<Map<String, dynamic>> _sites = const [];
  int? _selectedSiteId;

  @override
  void initState() {
    super.initState();
    _loadSites();
  }

  Future<void> _loadSites() async {
    final sites = await _backend.fetchSites();
    if (!mounted) return;
    setState(() {
      _sites = sites;
      _selectedSiteId = sites.isNotEmpty ? sites.first['id'] as int : null;
      _loadingSites = false;
    });
  }

  Future<void> _simulateRisk(String level) async {
    final id = _selectedSiteId;
    if (id == null) return;
    setState(() => _busy = true);
    final result = await _backend.simulateSite(id, level);
    if (!mounted) return;
    setState(() => _busy = false);
    if (result == null) {
      _toast('Simulation failed — backend unreachable?', tint: AppTheme.emergencyRed);
      return;
    }
    final cls = result['risk_class'] as String?;
    _toast(
      level == 'reset'
          ? 'Reset to live forecast'
          : 'Simulated ${RiskStyle.label(cls)} risk',
      tint: RiskStyle.color(cls),
    );
  }

  Future<void> _triggerManDown() async {
    setState(() => _busy = true);
    final id = await _backend.triggerManDown(
      const LatLng(45.4385, 28.0112),
      mobilityInfo: const {
        'has_issues': true,
        'level': 'High',
        'gravity': 'High',
      },
    );
    if (!mounted) return;
    setState(() => _busy = false);
    _toast(
      id == null ? 'Man-down failed — auth?' : 'Man-down triggered (alert $id)',
      tint: id == null ? AppTheme.emergencyRed : AppTheme.riskOrange,
    );
  }

  Future<void> _markSafe() async {
    setState(() => _busy = true);
    await _backend.cancelLatestAlert();
    if (!mounted) return;
    setState(() => _busy = false);
    _toast('Cleared latest SOS', tint: AppTheme.safeGreen);
  }

  void _toast(String message, {Color tint = AppTheme.primaryBlue}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: tint,
        behavior: SnackBarBehavior.floating,
        content: Text(message),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Demo Controls'),
        backgroundColor: Colors.white,
        elevation: 0,
      ),
      body: _loadingSites
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _banner(),
                const SizedBox(height: 20),
                _section('Target site'),
                const SizedBox(height: 8),
                _siteSelector(),
                const SizedBox(height: 24),
                _section('Simulate flood forecast'),
                const SizedBox(height: 8),
                _riskGrid(),
                const SizedBox(height: 24),
                _section('Worker safety'),
                const SizedBox(height: 8),
                _safetyButtons(),
                const SizedBox(height: 24),
                if (_busy)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.all(16),
                      child: CircularProgressIndicator(),
                    ),
                  ),
              ],
            ),
    );
  }

  Widget _banner() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF0F172A), Color(0xFF1E3A8A)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: const Row(
        children: [
          Icon(Icons.bolt, color: Colors.white, size: 32),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Demo mode',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'Trigger fake forecasts and worker emergencies to validate alerts, push, and evacuation flow end-to-end.',
                  style: TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _section(String label) {
    return Text(
      label.toUpperCase(),
      style: const TextStyle(
        fontSize: 11,
        letterSpacing: 1.2,
        fontWeight: FontWeight.w700,
        color: AppTheme.lightText,
      ),
    );
  }

  Widget _siteSelector() {
    if (_sites.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE5E7EB)),
        ),
        child: const Text('No sites configured'),
      );
    }
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE5E7EB)),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12),
        child: DropdownButtonHideUnderline(
          child: DropdownButton<int>(
            isExpanded: true,
            value: _selectedSiteId,
            items: _sites
                .map(
                  (site) => DropdownMenuItem<int>(
                    value: site['id'] as int,
                    child: Text(site['name'] as String),
                  ),
                )
                .toList(),
            onChanged: (value) => setState(() => _selectedSiteId = value),
          ),
        ),
      ),
    );
  }

  Widget _riskGrid() {
    final levels = const [
      ('low', 'Low', Icons.check_circle_outline),
      ('medium', 'Medium', Icons.error_outline),
      ('high', 'High', Icons.warning_amber_rounded),
      ('extreme', 'Extreme', Icons.dangerous),
    ];
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.6,
      children: [
        for (final (level, label, icon) in levels)
          _riskTile(level: level, label: label, icon: icon),
        _resetTile(),
      ],
    );
  }

  Widget _riskTile({required String level, required String label, required IconData icon}) {
    final color = RiskStyle.color(level);
    return InkWell(
      borderRadius: BorderRadius.circular(16),
      onTap: _busy || _selectedSiteId == null ? null : () => _simulateRisk(level),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: RiskStyle.gradient(level),
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.25),
              offset: const Offset(0, 6),
              blurRadius: 16,
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Icon(icon, color: Colors.white, size: 28),
            Text(
              label,
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.w800,
                fontSize: 16,
              ),
            ),
            const Text(
              'Tap to simulate',
              style: TextStyle(color: Colors.white70, fontSize: 11),
            ),
          ],
        ),
      ),
    );
  }

  Widget _resetTile() {
    return InkWell(
      borderRadius: BorderRadius.circular(16),
      onTap: _busy || _selectedSiteId == null ? null : () => _simulateRisk('reset'),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFE5E7EB)),
        ),
        child: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Icon(Icons.refresh, color: AppTheme.primaryBlue, size: 28),
            Text(
              'Reset',
              style: TextStyle(
                color: AppTheme.darkText,
                fontWeight: FontWeight.w800,
                fontSize: 16,
              ),
            ),
            Text(
              'Re-run live forecast',
              style: TextStyle(color: AppTheme.lightText, fontSize: 11),
            ),
          ],
        ),
      ),
    );
  }

  Widget _safetyButtons() {
    return Row(
      children: [
        Expanded(
          child: _bigButton(
            color: AppTheme.emergencyRed,
            icon: Icons.medical_services,
            label: 'Trigger Man-Down',
            onTap: _busy ? null : _triggerManDown,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _bigButton(
            color: AppTheme.safeGreen,
            icon: Icons.health_and_safety,
            label: 'Mark Safe',
            onTap: _busy ? null : _markSafe,
          ),
        ),
      ],
    );
  }

  Widget _bigButton({
    required Color color,
    required IconData icon,
    required String label,
    required VoidCallback? onTap,
  }) {
    return InkWell(
      borderRadius: BorderRadius.circular(16),
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 18, horizontal: 12),
        decoration: BoxDecoration(
          color: color.withOpacity(0.12),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.4)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
