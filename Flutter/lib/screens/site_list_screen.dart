import 'package:flutter/material.dart';

import '../services/backend_service.dart';
import '../theme.dart';
import '../utils/risk_style.dart';
import 'demo_controls_screen.dart';
import 'site_forecast_screen.dart';

class SiteListScreen extends StatefulWidget {
  const SiteListScreen({super.key});

  @override
  State<SiteListScreen> createState() => _SiteListScreenState();
}

class _SiteListScreenState extends State<SiteListScreen> {
  final BackendService _backend = BackendService();
  bool _loading = true;
  List<Map<String, dynamic>> _sites = const [];
  final Map<int, Map<String, dynamic>> _forecasts = {};

  @override
  void initState() {
    super.initState();
    _load();
    _backend.eventStream.listen(_onEvent);
  }

  void _onEvent(Map<String, dynamic> event) {
    final type = event['event'] ?? event['type'];
    if (type == 'forecast:updated') {
      final payload = event['payload'] is Map ? event['payload'] as Map : event;
      final id = payload['site_id'];
      if (id is int) {
        _refreshForecast(id);
      }
    }
  }

  Future<void> _refreshForecast(int siteId) async {
    final forecast = await _backend.fetchSiteForecast(siteId);
    if (!mounted || forecast == null) return;
    setState(() => _forecasts[siteId] = forecast);
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    final sites = await _backend.fetchSites();
    final results = await Future.wait(
      sites.map((site) => _backend.fetchSiteForecast(site['id'] as int)),
    );
    if (!mounted) return;
    setState(() {
      _sites = sites;
      _forecasts.clear();
      for (var i = 0; i < sites.length; i++) {
        final forecast = results[i];
        if (forecast != null) {
          _forecasts[sites[i]['id'] as int] = forecast;
        }
      }
      _loading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Industrial Sites'),
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.science_outlined),
            tooltip: 'Demo controls',
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const DemoControlsScreen()),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _load,
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _sites.isEmpty
              ? _buildEmptyState()
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.separated(
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                    itemCount: _sites.length + 1,
                    separatorBuilder: (_, _) => const SizedBox(height: 12),
                    itemBuilder: (context, index) {
                      if (index == 0) return _buildSummaryHeader();
                      final site = _sites[index - 1];
                      final id = site['id'] as int;
                      final forecast = _forecasts[id];
                      return _SiteCard(
                        site: site,
                        forecast: forecast,
                        onTap: () => Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => SiteForecastScreen(site: site),
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.factory_outlined, size: 64, color: AppTheme.lightText),
            const SizedBox(height: 16),
            const Text(
              'No sites configured',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
            const SizedBox(height: 8),
            const Text(
              'Add an industrial site through the backend API to start receiving flood-risk forecasts.',
              textAlign: TextAlign.center,
              style: TextStyle(color: AppTheme.lightText),
            ),
            const SizedBox(height: 16),
            FilledButton.tonal(onPressed: _load, child: const Text('Reload')),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryHeader() {
    int extreme = 0, high = 0, medium = 0, calm = 0;
    for (final f in _forecasts.values) {
      switch (f['risk_class']) {
        case 'extreme':
          extreme++;
          break;
        case 'high':
          high++;
          break;
        case 'medium':
          medium++;
          break;
        default:
          calm++;
      }
    }
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1E3A8A), Color(0xFF2C74FF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF1E3A8A).withOpacity(0.18),
            offset: const Offset(0, 6),
            blurRadius: 18,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: Colors.white.withOpacity(0.18),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.shield_moon, color: Colors.white),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Site portfolio',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                    Text(
                      'Live flood risk overview',
                      style: TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w700,
                        fontSize: 18,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(child: _summaryStat('Extreme', extreme, AppTheme.emergencyRed)),
              Expanded(child: _summaryStat('High', high, AppTheme.riskOrange)),
              Expanded(child: _summaryStat('Medium', medium, AppTheme.monitorYellow)),
              Expanded(child: _summaryStat('Calm', calm, AppTheme.safeGreen)),
            ],
          ),
        ],
      ),
    );
  }

  Widget _summaryStat(String label, int count, Color tint) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 4),
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.10),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white.withOpacity(0.18)),
      ),
      child: Column(
        children: [
          Text(
            '$count',
            style: TextStyle(
              color: tint,
              fontSize: 22,
              fontWeight: FontWeight.w800,
            ),
          ),
          Text(
            label,
            style: const TextStyle(color: Colors.white70, fontSize: 11),
          ),
        ],
      ),
    );
  }
}

class _SiteCard extends StatelessWidget {
  const _SiteCard({
    required this.site,
    required this.forecast,
    required this.onTap,
  });

  final Map<String, dynamic> site;
  final Map<String, dynamic>? forecast;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final riskClass = forecast?['risk_class'] as String?;
    final score = forecast?['risk_score'] as num?;
    final drivers = (forecast?['drivers'] as Map?)?.cast<String, dynamic>() ?? const {};
    final precip48h = drivers['precip_mm_48h'] as num?;
    final color = RiskStyle.color(riskClass);

    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(16),
      elevation: 0,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE5E7EB)),
          ),
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 4,
                height: 60,
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            site['name'] as String,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                              color: AppTheme.darkText,
                            ),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        Text(
                          site['country'] as String? ?? '',
                          style: const TextStyle(
                            fontSize: 12,
                            color: AppTheme.lightText,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        Icon(RiskStyle.icon(riskClass), color: color, size: 16),
                        const SizedBox(width: 4),
                        Text(
                          forecast == null
                              ? 'Forecast pending'
                              : '${RiskStyle.label(riskClass)} · score ${(score ?? 0).toStringAsFixed(2)}',
                          style: TextStyle(
                            color: color,
                            fontWeight: FontWeight.w600,
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                    if (precip48h != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        '48h precipitation: ${precip48h.toStringAsFixed(0)} mm',
                        style: const TextStyle(fontSize: 12, color: AppTheme.lightText),
                      ),
                    ],
                  ],
                ),
              ),
              const Icon(Icons.chevron_right, color: AppTheme.lightText),
            ],
          ),
        ),
      ),
    );
  }
}
