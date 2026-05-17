import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../services/backend_service.dart';
import '../theme.dart';
import '../utils/risk_style.dart';

class SiteForecastScreen extends StatefulWidget {
  const SiteForecastScreen({super.key, required this.site});

  final Map<String, dynamic> site;

  @override
  State<SiteForecastScreen> createState() => _SiteForecastScreenState();
}

class _SiteForecastScreenState extends State<SiteForecastScreen>
    with SingleTickerProviderStateMixin {
  final BackendService _backend = BackendService();
  bool _loading = true;
  bool _simulating = false;
  Map<String, dynamic>? _forecast;
  Map<String, dynamic>? _inundation;
  late final AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1400),
      vsync: this,
    )..repeat(reverse: true);
    _refresh();
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  Future<void> _refresh({bool force = false}) async {
    setState(() => _loading = true);
    final id = widget.site['id'] as int;
    final forecast = await _backend.fetchSiteForecast(id, refresh: force);
    final inundation = await _backend.fetchSiteInundation(id);
    if (!mounted) return;
    setState(() {
      _forecast = forecast;
      _inundation = inundation;
      _loading = false;
    });
  }

  Future<void> _simulate(String level) async {
    setState(() => _simulating = true);
    final id = widget.site['id'] as int;
    final result = await _backend.simulateSite(id, level);
    if (!mounted) return;
    if (result != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: RiskStyle.color(result['risk_class'] as String?),
          content: Text(
            level == 'reset'
                ? 'Restored live forecast for site'
                : 'Simulated ${RiskStyle.label(result['risk_class'] as String?)} risk',
          ),
        ),
      );
    }
    await _refresh();
    setState(() => _simulating = false);
  }

  List<Polygon> _polygonsFromGeoJson() {
    final geo = _inundation;
    if (geo == null) return const [];
    final features = (geo['features'] as List?) ?? const [];
    final polygons = <Polygon>[];
    for (final feature in features) {
      final geometry = feature['geometry'];
      if (geometry == null || geometry['type'] != 'Polygon') continue;
      final coords = geometry['coordinates'] as List;
      if (coords.isEmpty) continue;
      final ring = (coords.first as List)
          .map((p) => LatLng((p as List)[1].toDouble(), p[0].toDouble()))
          .toList();
      final riskClass = feature['properties']?['risk_class'] as String?;
      polygons.add(
        Polygon(
          points: ring,
          color: RiskStyle.color(riskClass).withOpacity(0.3),
          borderColor: RiskStyle.color(riskClass),
          borderStrokeWidth: 2,
        ),
      );
    }
    return polygons;
  }

  @override
  Widget build(BuildContext context) {
    final location = widget.site['location'] as Map<String, dynamic>;
    final center = LatLng(
      (location['lat'] as num).toDouble(),
      (location['lng'] as num).toDouble(),
    );
    final riskClass = _forecast?['risk_class'] as String?;
    final score = (_forecast?['risk_score'] as num?)?.toDouble() ?? 0.0;
    final drivers = (_forecast?['drivers'] as Map?)?.cast<String, dynamic>() ?? const {};
    final isAlert = riskClass == 'high' || riskClass == 'extreme';

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: Text(widget.site['name'] as String),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => _refresh(force: true),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _simulating ? null : _showSimulateSheet,
        backgroundColor: AppTheme.primaryBlue,
        icon: _simulating
            ? const SizedBox(
                width: 18,
                height: 18,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
              )
            : const Icon(Icons.science_outlined),
        label: const Text('Simulate'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
              children: [
                _buildHeroRiskCard(riskClass, score, isAlert),
                const SizedBox(height: 16),
                _buildDriverGrid(drivers),
                const SizedBox(height: 16),
                _buildMapCard(center, riskClass),
              ],
            ),
    );
  }

  Widget _buildHeroRiskCard(String? riskClass, double score, bool isAlert) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: RiskStyle.gradient(riskClass),
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: RiskStyle.color(riskClass).withOpacity(0.25),
            offset: const Offset(0, 8),
            blurRadius: 24,
          ),
        ],
      ),
      child: Row(
        children: [
          AnimatedBuilder(
            animation: _pulseController,
            builder: (context, _) {
              final scale = isAlert ? 1.0 + 0.08 * _pulseController.value : 1.0;
              return Transform.scale(
                scale: scale,
                child: Container(
                  width: 84,
                  height: 84,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.18),
                    shape: BoxShape.circle,
                    border: Border.all(color: Colors.white.withOpacity(0.4), width: 2),
                  ),
                  child: Icon(
                    RiskStyle.icon(riskClass),
                    color: Colors.white,
                    size: 40,
                  ),
                ),
              );
            },
          ),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '48-HOUR FLOOD RISK',
                  style: TextStyle(
                    color: Colors.white.withOpacity(0.85),
                    fontSize: 11,
                    letterSpacing: 1.2,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  RiskStyle.label(riskClass),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 26,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 8),
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: LinearProgressIndicator(
                    value: score.clamp(0.0, 1.0),
                    minHeight: 8,
                    backgroundColor: Colors.white.withOpacity(0.25),
                    valueColor: const AlwaysStoppedAnimation(Colors.white),
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Score ${score.toStringAsFixed(2)}',
                  style: const TextStyle(color: Colors.white70, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDriverGrid(Map<String, dynamic> drivers) {
    Widget chip(IconData icon, String label, dynamic value, String unit) {
      return Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFE5E7EB)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 18, color: AppTheme.primaryBlue),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    label,
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppTheme.lightText,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value == null ? '—' : '$value $unit'.trim(),
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: AppTheme.darkText,
              ),
            ),
          ],
        ),
      );
    }

    String fmtNum(dynamic v, {int decimals = 0}) {
      if (v == null) return '—';
      if (v is num) return v.toStringAsFixed(decimals);
      return v.toString();
    }

    String fmtProb(dynamic v) {
      if (v == null) return '—';
      if (v is num) return '${(v * 100).toStringAsFixed(0)}%';
      return v.toString();
    }

    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 2.2,
      children: [
        chip(Icons.water_drop_outlined, 'Precip 24h', fmtNum(drivers['precip_mm_24h']), 'mm'),
        chip(Icons.water_drop, 'Precip 48h', fmtNum(drivers['precip_mm_48h']), 'mm'),
        chip(Icons.flood_outlined, 'EFAS prob.', fmtProb(drivers['efas_probability']), ''),
        chip(Icons.public, 'GloFAS prob.', fmtProb(drivers['glofas_probability']), ''),
        chip(Icons.waves, 'River max', fmtNum(drivers['river_discharge_max_m3s']), 'm³/s'),
        chip(Icons.show_chart, 'Baseline', fmtNum(drivers['river_discharge_baseline_m3s']), 'm³/s'),
      ],
    );
  }

  Widget _buildMapCard(LatLng center, String? riskClass) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(16),
      child: SizedBox(
        height: 280,
        child: FlutterMap(
          options: MapOptions(initialCenter: center, initialZoom: 13),
          children: [
            TileLayer(
              urlTemplate: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.example.floodguard',
            ),
            PolygonLayer(polygons: _polygonsFromGeoJson()),
            MarkerLayer(
              markers: [
                Marker(
                  point: center,
                  width: 48,
                  height: 48,
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      shape: BoxShape.circle,
                      border: Border.all(color: RiskStyle.color(riskClass), width: 3),
                      boxShadow: [
                        BoxShadow(
                          color: RiskStyle.color(riskClass).withOpacity(0.4),
                          blurRadius: 12,
                        ),
                      ],
                    ),
                    child: Icon(
                      Icons.factory,
                      color: RiskStyle.color(riskClass),
                      size: 24,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showSimulateSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (sheetContext) {
        Widget tile(String level, String label, String desc, IconData icon) {
          final color = RiskStyle.color(level);
          return ListTile(
            leading: CircleAvatar(
              backgroundColor: color.withOpacity(0.15),
              child: Icon(icon, color: color),
            ),
            title: Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
            subtitle: Text(desc),
            onTap: () {
              Navigator.pop(sheetContext);
              _simulate(level);
            },
          );
        }

        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 40,
                  height: 4,
                  margin: const EdgeInsets.only(bottom: 12),
                  decoration: BoxDecoration(
                    color: const Color(0xFFCBD5E1),
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 20),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Simulate forecast',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                    ),
                  ),
                ),
                const Padding(
                  padding: EdgeInsets.fromLTRB(20, 4, 20, 12),
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      'Inject a synthetic snapshot to test alerts and notifications.',
                      style: TextStyle(color: AppTheme.lightText),
                    ),
                  ),
                ),
                tile('low', 'Low risk', 'Calm conditions', Icons.check_circle_outline),
                tile('medium', 'Medium risk', 'Watch and prepare', Icons.error_outline),
                tile('high', 'High risk', 'Push alert + evacuate prep', Icons.warning_amber_rounded),
                tile('extreme', 'Extreme risk', 'Trigger evacuation', Icons.dangerous),
                const Divider(height: 1),
                tile('reset', 'Reset to live data', 'Re-run real forecast pipeline', Icons.refresh),
              ],
            ),
          ),
        );
      },
    );
  }
}
