import 'dart:async';
import 'dart:math' as math;

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:latlong2/latlong.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../services/backend_service.dart';
import '../theme.dart';
import '../utils/risk_style.dart';
import 'alert_screen.dart';
import 'demo_controls_screen.dart';
import 'man_down_screen.dart';
import 'profile_screen.dart';
import 'site_list_screen.dart';

enum DemoState {
  safe,
  smsReceived,
  crisis,
  evacuation,
  reroute,
  manDown,
  sosTriggered,
}

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen>
    with SingleTickerProviderStateMixin {
  String _currentStatus = 'Safe';
  DemoState _demoState = DemoState.safe;
  final bool _showSmsBanner = false;
  final FlutterTts _flutterTts = FlutterTts();
  String? _lastTriggeredBroadcastKey;

  String _copernicusRisk = 'LOADING';
  List<Map<String, dynamic>> _safeLocations = const [];
  String? _activeAlertMessage;
  String? _activeAlertTitle;
  String? _activeAlertRiskClass;
  bool _activeAlertSimulated = false;
  Timer? _alertBannerTimer;

  Map<String, dynamic>? _currentForecast;
  String? _currentSiteName;
  Map<String, dynamic>? _currentInundation;

  StreamSubscription? _wsSubscription;
  Timer? _telemetryTimer;
  String? _currentAlertId;

  LatLng _workerPosition = const LatLng(45.4353, 28.0080);
  Timer? _movementTimer;
  Timer? _manDownTimer;
  final int _manDownCountdown = 30;
  late final AnimationController _pulseController;

  final List<LatLng> _routeA = [
    const LatLng(45.4353, 28.0080),
    const LatLng(45.4365, 28.0090),
    const LatLng(45.4380, 28.0120),
    const LatLng(45.4400, 28.0150),
  ];

  final List<LatLng> _routeB = [
    const LatLng(45.4353, 28.0080),
    const LatLng(45.4360, 28.0060),
    const LatLng(45.4385, 28.0050),
    const LatLng(45.4410, 28.0100),
    const LatLng(45.4400, 28.0150),
  ];

  static const LatLng _safePoint = LatLng(45.4400, 28.0150);

  final Map<String, Color> _statusColors = {
    'Safe': const Color(0xFF10B981),
    'Monitor': const Color(0xFFF59E0B),
    'Need Help': const Color(0xFFF97316),
    'Emergency': const Color(0xFFEF4444),
  };

  final Map<String, IconData> _statusIcons = {
    'Safe': Icons.check_circle_rounded,
    'Monitor': Icons.bolt_rounded,
    'Need Help': Icons.warning_amber_rounded,
    'Emergency': Icons.campaign_rounded,
  };

  final MapController _mapController = MapController();
  bool _showFloodLayer = true;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      duration: const Duration(milliseconds: 1400),
      vsync: this,
    )..repeat(reverse: true);
    _initTts();
    _initBackend();
  }

  @override
  void dispose() {
    _movementTimer?.cancel();
    _manDownTimer?.cancel();
    _telemetryTimer?.cancel();
    _alertBannerTimer?.cancel();
    _wsSubscription?.cancel();
    _pulseController.dispose();
    super.dispose();
  }

  Future<void> _initTts() async {
    await _flutterTts.setLanguage("en-US");
    await _flutterTts.setPitch(1.0);
  }

  Future<void> _initBackend() async {
    await BackendService().initialize();
    _fetchMapData();
    _loadDefaultSiteForecast();

    _telemetryTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      BackendService().postUserStatus(_workerPosition, _currentStatus);
    });

    _wsSubscription = BackendService().eventStream.listen(_handleEvent);
  }

  Future<void> _loadDefaultSiteForecast() async {
    final sites = await BackendService().fetchSites();
    if (!mounted || sites.isEmpty) return;
    final first = sites.first;
    final id = first['id'] as int;
    final forecast = await BackendService().fetchSiteForecast(id);
    final inundation = await BackendService().fetchSiteInundation(id);
    if (!mounted) return;
    setState(() {
      _currentSiteName = first['name'] as String?;
      _currentForecast = forecast;
      _currentInundation = inundation;
    });
  }

  Future<void> _fetchMapData() async {
    final data = await BackendService().fetchMapData(_workerPosition);
    if (!mounted || data == null) return;
    final copernicus = data['flood_warning']?['copernicus'];
    String label = 'UNKNOWN';
    if (copernicus != null && copernicus['error'] == null) {
      switch (copernicus['status']) {
        case 'likely_flooding':
          label = 'HIGH RISK';
          break;
        case 'possible_flooding':
          label = 'MEDIUM RISK';
          break;
        case 'no_flood_signal':
          label = 'LOW RISK';
          break;
      }
    }
    final rawLocations = (data['safe_locations'] as List?) ?? const [];
    final locations = rawLocations
        .whereType<Map>()
        .map((e) => e.cast<String, dynamic>())
        .toList();
    locations.sort((a, b) => _distanceMeters(a).compareTo(_distanceMeters(b)));
    setState(() {
      _copernicusRisk = label;
      _safeLocations = locations;
    });
  }

  double _distanceMeters(Map<String, dynamic> location) {
    final lat = (location['lat'] as num?)?.toDouble();
    final lng = (location['lng'] as num?)?.toDouble();
    if (lat == null || lng == null) return double.infinity;
    final dLat = (lat - _workerPosition.latitude) * 111320.0;
    final dLng = (lng - _workerPosition.longitude) *
        111320.0 *
        math.cos(_workerPosition.latitude * math.pi / 180.0);
    return math.sqrt(dLat * dLat + dLng * dLng);
  }

  String _formatDistance(double meters) {
    if (meters.isInfinite || meters.isNaN) return '—';
    if (meters < 1000) return '${meters.toStringAsFixed(0)} m';
    return '${(meters / 1000).toStringAsFixed(1)} km';
  }

  void _handleEvent(Map<String, dynamic> data) {
    if (!mounted) return;
    final event = (data['event'] ?? data['type'])?.toString();
    final payload = data['payload'] is Map ? data['payload'] as Map : data;

    switch (event) {
      case 'user:status_update':
        if (payload['user_id'] == BackendService().userId) {
          setState(
            () => _currentStatus = payload['status']?.toString() ?? 'Safe',
          );
        }
        break;

      case 'forecast:updated':
        _onForecastUpdated(payload);
        break;

      case 'alert:new':
      case 'alert:mobile_emergency':
        _onAlertNew(payload);
        break;

      case 'alert:updated':
        _onAlertUpdated(payload);
        break;
    }
  }

  void _onForecastUpdated(Map payload) {
    final siteId = payload['site_id'];
    if (siteId is! int) return;
    BackendService().fetchSiteForecast(siteId).then((forecast) {
      if (!mounted || forecast == null) return;
      setState(() {
        _currentForecast = forecast;
        _currentSiteName =
            (payload['site_name'] as String?) ?? _currentSiteName;
      });
    });
    BackendService().fetchSiteInundation(siteId).then((geojson) {
      if (!mounted) return;
      setState(() => _currentInundation = geojson);
    });
  }

  void _onAlertNew(Map payload) {
    final riskClass = payload['risk_class']?.toString();
    final title = payload['title']?.toString() ?? 'Flood alert';
    final message = payload['message']?.toString() ?? '';
    final simulated = payload['simulated'] == true;

    setState(() {
      _activeAlertTitle = title;
      _activeAlertMessage = message;
      _activeAlertRiskClass = riskClass;
      _activeAlertSimulated = simulated;
    });

    _alertBannerTimer?.cancel();
    _alertBannerTimer = Timer(const Duration(seconds: 30), () {
      if (mounted) setState(() => _activeAlertMessage = null);
    });

    if (riskClass == 'high' || riskClass == 'extreme') {
      _flutterTts.speak(
        'Flood alert. ${riskClass!.toUpperCase()} risk detected.',
      );
      if (_demoState == DemoState.safe || _demoState == DemoState.smsReceived) {
        setState(() => _demoState = DemoState.crisis);
        _triggerCrisis();
      }
    }
  }

  void _onAlertUpdated(Map payload) {
    final broadcastSentRaw =
        payload['broadcastSent'] ?? payload['broadcast_sent'];
    final broadcastSent =
        broadcastSentRaw == true ||
        broadcastSentRaw == 1 ||
        broadcastSentRaw == '1';
    final status = (payload['status'] ?? '').toString().toLowerCase();
    final isPublished = status == 'published';
    final alertId = payload['id']?.toString();
    final createdBy = (payload['createdBy'] ?? payload['created_by'] ?? '')
        .toString();
    final title = (payload['title'] ?? '').toString();
    final isMobileEmergencyRaw =
        payload['isMobileEmergency'] ?? payload['is_mobile_emergency'];
    final isMobileEmergency =
        isMobileEmergencyRaw == true ||
        title.startsWith('SOS:') ||
        createdBy.startsWith('mob-');
    final broadcastMoment =
        (payload['publishedAt'] ??
                payload['published_at'] ??
                payload['updatedAt'] ??
                payload['updated_at'] ??
                '')
            .toString();
    final broadcastKey = alertId != null ? '$alertId:$broadcastMoment' : null;

    if (payload['type'] == 'evacuation' &&
        broadcastSent &&
        isPublished &&
        !isMobileEmergency &&
        alertId != null &&
        broadcastKey != null &&
        broadcastKey != _lastTriggeredBroadcastKey) {
      _activeAlertMessage = payload['message']?.toString();
      if (_demoState == DemoState.safe || _demoState == DemoState.smsReceived) {
        _lastTriggeredBroadcastKey = broadcastKey;
        setState(() => _demoState = DemoState.crisis);
        _triggerCrisis();
      }
    }
  }

  void _triggerCrisis() async {
    _currentStatus = 'Emergency';
    final startedEvac = await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const AlertScreen()),
    );
    if (startedEvac == true && mounted) {
      setState(() {
        _demoState = DemoState.evacuation;
        _startSimulatedMovement();
      });
    }
  }

  void _startSimulatedMovement() {
    _movementTimer?.cancel();
    int ticks = 0;
    _movementTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      ticks++;
      setState(() {
        _workerPosition = LatLng(
          _workerPosition.latitude + 0.0002,
          _workerPosition.longitude + 0.0002,
        );
      });
      if (ticks == 8 && _demoState == DemoState.evacuation) {
        setState(() => _demoState = DemoState.reroute);
        _triggerReroute();
      }
      if (ticks == 16 && _demoState == DemoState.reroute) {
        setState(() => _demoState = DemoState.manDown);
        _triggerManDown();
      }
    });
  }

  void _triggerReroute() {
    _flutterTts.speak(
      "Route A flooded. Proceed to Assembly Point North via the elevated walkway.",
    );
  }

  void _triggerManDown() async {
    _movementTimer?.cancel();
    setState(() {
      _demoState = DemoState.sosTriggered;
      _currentStatus = 'Emergency';
    });
    _currentAlertId = await _notifyManDown();
    if (!mounted) return;
    final result = await Navigator.of(context).push<ManDownResult>(
      MaterialPageRoute(
        fullscreenDialog: true,
        builder: (_) => ManDownScreen(
          workerPosition: _workerPosition,
          alertId: _currentAlertId,
        ),
      ),
    );
    if (!mounted) return;
    if (result == ManDownResult.cleared) {
      setState(() {
        _demoState = DemoState.safe;
        _currentStatus = 'Safe';
        _activeAlertMessage = null;
      });
      _currentAlertId = null;
    } else {
      setState(() => _demoState = DemoState.safe);
    }
  }

  Future<String?> _notifyManDown() async {
    final prefs = await SharedPreferences.getInstance();
    final hasIssues = prefs.getBool('hasMobilityIssues') ?? false;
    final gravity = prefs.getString('mobilityGravity') ?? 'Low';
    return BackendService().triggerManDown(
      _workerPosition,
      mobilityInfo: {
        "has_issues": hasIssues,
        "gravity": gravity,
        "level": gravity,
      },
      userStatus: "Man Down",
    );
  }

  List<Polygon> _inundationPolygons() {
    final geo = _currentInundation;
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
          color: RiskStyle.color(riskClass).withOpacity(0.25),
          borderColor: RiskStyle.color(riskClass),
          borderStrokeWidth: 2,
        ),
      );
    }
    return polygons;
  }

  void _recenter() {
    _mapController.move(_workerPosition, 15.0);
  }

  @override
  Widget build(BuildContext context) {
    final activeColor = _statusColors[_currentStatus]!;
    final activeIcon = _statusIcons[_currentStatus]!;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      drawer: _buildDrawer(context),
      body: SafeArea(
        child: Column(
          children: [
            _buildTopBar(activeColor, activeIcon),
            if (_showSmsBanner) _buildSmsBanner(),
            if (_activeAlertMessage != null) _buildAlertBanner(),
            Expanded(
              child: CustomScrollView(
                slivers: [
                  SliverToBoxAdapter(child: _buildLiveDataStrip()),
                  SliverToBoxAdapter(child: _buildMapHero()),
                  SliverToBoxAdapter(child: _buildForecastCard()),
                  SliverToBoxAdapter(child: _buildQuickActions()),
                  if (_demoState == DemoState.manDown)
                    SliverToBoxAdapter(child: _buildManDownIndicator()),
                  SliverToBoxAdapter(child: _buildSafeLocations()),
                  const SliverToBoxAdapter(child: SizedBox(height: 24)),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopBar(Color statusColor, IconData statusIcon) {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.fromLTRB(8, 8, 16, 12),
      child: Row(
        children: [
          Builder(
            builder: (context) => IconButton(
              icon: const Icon(Icons.menu),
              onPressed: () => Scaffold.of(context).openDrawer(),
            ),
          ),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'FloodGuard',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.w800,
                    color: AppTheme.darkText,
                  ),
                ),
                Text(
                  'Industrial flood watch',
                  style: TextStyle(fontSize: 12, color: AppTheme.lightText),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: statusColor.withOpacity(0.12),
              borderRadius: BorderRadius.circular(999),
              border: Border.all(color: statusColor.withOpacity(0.4)),
            ),
            child: Row(
              children: [
                Icon(statusIcon, size: 16, color: statusColor),
                const SizedBox(width: 6),
                Text(
                  _currentStatus,
                  style: TextStyle(
                    color: statusColor,
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSmsBanner() {
    return Container(
      margin: const EdgeInsets.fromLTRB(16, 8, 16, 0),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.primaryBlue.withOpacity(0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.primaryBlue.withOpacity(0.3)),
      ),
      child: const Row(
        children: [
          Icon(Icons.sms, color: AppTheme.primaryBlue),
          SizedBox(width: 10),
          Expanded(
            child: Text(
              'PRE-ALERT: storm forecast in 3 days. Prepare for evacuation.',
              style: TextStyle(
                fontWeight: FontWeight.w600,
                color: AppTheme.primaryBlue,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertBanner() {
    final color = RiskStyle.color(_activeAlertRiskClass);
    return AnimatedBuilder(
      animation: _pulseController,
      builder: (context, child) {
        final glow = 0.25 + 0.15 * _pulseController.value;
        return Container(
          margin: const EdgeInsets.fromLTRB(16, 8, 16, 0),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: RiskStyle.gradient(_activeAlertRiskClass),
            ),
            borderRadius: BorderRadius.circular(16),
            boxShadow: [
              BoxShadow(
                color: color.withOpacity(glow),
                blurRadius: 24,
                offset: const Offset(0, 6),
              ),
            ],
          ),
          child: child,
        );
      },
      child: Row(
        children: [
          Icon(
            RiskStyle.icon(_activeAlertRiskClass),
            color: Colors.white,
            size: 28,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      _activeAlertTitle ?? 'Flood Alert',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.w800,
                        fontSize: 14,
                      ),
                    ),
                    if (_activeAlertSimulated) ...[
                      const SizedBox(width: 6),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 6,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.25),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text(
                          'DEMO',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 10,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
                if (_activeAlertMessage != null &&
                    _activeAlertMessage!.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(
                      _activeAlertMessage!,
                      style: const TextStyle(color: Colors.white, fontSize: 13),
                    ),
                  ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.close, color: Colors.white70),
            onPressed: () => setState(() => _activeAlertMessage = null),
          ),
        ],
      ),
    );
  }

  Widget _buildMapHero() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(20),
        child: SizedBox(
          height: 320,
          child: Stack(
            children: [
              FlutterMap(
                mapController: _mapController,
                options: MapOptions(
                  initialCenter: _workerPosition,
                  initialZoom: 14.0,
                ),
                children: [
                  TileLayer(
                    urlTemplate:
                        'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                    userAgentPackageName: 'com.example.floodguard',
                  ),
                  if (_showFloodLayer)
                    PolygonLayer(polygons: _inundationPolygons()),
                  if (_demoState == DemoState.evacuation ||
                      _demoState == DemoState.reroute ||
                      _demoState == DemoState.manDown)
                    PolylineLayer(
                      polylines: [
                        if (_demoState == DemoState.evacuation)
                          Polyline(
                            points: _routeA,
                            color: AppTheme.primaryBlue,
                            strokeWidth: 5,
                          ),
                        if (_demoState == DemoState.reroute ||
                            _demoState == DemoState.manDown) ...[
                          Polyline(
                            points: _routeA,
                            color: AppTheme.emergencyRed.withOpacity(0.7),
                            strokeWidth: 4,
                          ),
                          Polyline(
                            points: _routeB,
                            color: AppTheme.primaryBlue,
                            strokeWidth: 5,
                          ),
                        ],
                      ],
                    ),
                  MarkerLayer(
                    markers: [
                      ..._safeLocations
                          .where((l) => l['lat'] != null && l['lng'] != null)
                          .take(8)
                          .map(
                            (l) => Marker(
                              point: LatLng(
                                (l['lat'] as num).toDouble(),
                                (l['lng'] as num).toDouble(),
                              ),
                              width: 38,
                              height: 38,
                              child: _safeMarker(),
                            ),
                          ),
                      if (_safeLocations.isEmpty)
                        Marker(
                          point: _safePoint,
                          width: 38,
                          height: 38,
                          child: _safeMarker(),
                        ),
                      Marker(
                        point: _workerPosition,
                        width: 56,
                        height: 56,
                        child: _workerMarker(),
                      ),
                    ],
                  ),
                ],
              ),
              Positioned(top: 12, left: 12, child: _mapBadge()),
              Positioned(top: 12, right: 12, child: _riskBadge()),
              Positioned(bottom: 12, left: 12, child: _mapLegend()),
              Positioned(
                bottom: 12,
                right: 12,
                child: Column(
                  children: [
                    _mapButton(Icons.my_location, _recenter),
                    const SizedBox(height: 8),
                    _mapButton(
                      _showFloodLayer ? Icons.layers : Icons.layers_outlined,
                      () => setState(() => _showFloodLayer = !_showFloodLayer),
                      tint: _showFloodLayer
                          ? AppTheme.primaryBlue
                          : AppTheme.lightText,
                    ),
                    const SizedBox(height: 8),
                    _mapButton(Icons.science_outlined, () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => const DemoControlsScreen(),
                        ),
                      );
                    }),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLiveDataStrip() {
    final drivers = (_currentForecast?['drivers'] as Map?)?.cast<String, dynamic>() ?? const {};
    final precip24 = drivers['precip_mm_24h'] as num?;
    final precip48 = drivers['precip_mm_48h'] as num?;
    final efas = drivers['efas_probability'] as num?;
    final glofas = drivers['glofas_probability'] as num?;
    final discharge = drivers['river_discharge_max_m3s'] as num?;
    final baseline = drivers['river_discharge_baseline_m3s'] as num?;
    final overflow = (discharge != null && baseline != null && baseline > 0)
        ? ((discharge / baseline) * 100).round()
        : null;

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: SizedBox(
        height: 86,
        child: ListView(
          scrollDirection: Axis.horizontal,
          children: [
            _dataChip(
              icon: Icons.cloud_outlined,
              label: 'Rain 24h',
              value: precip24 == null ? '—' : '${precip24.toStringAsFixed(0)} mm',
              tint: AppTheme.primaryBlue,
            ),
            _dataChip(
              icon: Icons.water_drop,
              label: 'Rain 48h',
              value: precip48 == null ? '—' : '${precip48.toStringAsFixed(0)} mm',
              tint: AppTheme.primaryBlue,
            ),
            _dataChip(
              icon: Icons.waves,
              label: 'River',
              value: discharge == null ? '—' : '${discharge.toStringAsFixed(0)} m³/s',
              tint: const Color(0xFF06B6D4),
            ),
            if (overflow != null)
              _dataChip(
                icon: Icons.trending_up,
                label: 'vs baseline',
                value: '$overflow%',
                tint: overflow >= 200
                    ? AppTheme.emergencyRed
                    : overflow >= 130
                        ? AppTheme.riskOrange
                        : AppTheme.safeGreen,
              ),
            _dataChip(
              icon: Icons.flood_outlined,
              label: 'EFAS',
              value: efas == null ? '—' : '${(efas * 100).toStringAsFixed(0)}%',
              tint: AppTheme.monitorYellow,
            ),
            _dataChip(
              icon: Icons.public,
              label: 'GloFAS',
              value: glofas == null ? '—' : '${(glofas * 100).toStringAsFixed(0)}%',
              tint: const Color(0xFF8B5CF6),
            ),
          ],
        ),
      ),
    );
  }

  Widget _dataChip({
    required IconData icon,
    required String label,
    required String value,
    required Color tint,
  }) {
    return Container(
      width: 130,
      margin: const EdgeInsets.only(right: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE5E7EB)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: tint),
              const SizedBox(width: 6),
              Text(
                label,
                style: const TextStyle(
                  fontSize: 11,
                  color: AppTheme.lightText,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w800,
              color: tint,
            ),
          ),
        ],
      ),
    );
  }

  Widget _riskBadge() {
    final riskClass = _currentForecast?['risk_class'] as String?;
    if (riskClass == null) return const SizedBox.shrink();
    final color = RiskStyle.color(riskClass);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(999),
        boxShadow: [
          BoxShadow(color: color.withOpacity(0.4), blurRadius: 12),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(RiskStyle.icon(riskClass), color: Colors.white, size: 14),
          const SizedBox(width: 6),
          Text(
            RiskStyle.label(riskClass),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 11,
              fontWeight: FontWeight.w800,
              letterSpacing: 0.6,
            ),
          ),
        ],
      ),
    );
  }

  Widget _mapLegend() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(10),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 8)],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _legendDot(AppTheme.emergencyRed),
          const SizedBox(width: 4),
          const Text('You', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600)),
          const SizedBox(width: 10),
          _legendDot(AppTheme.safeGreen),
          const SizedBox(width: 4),
          const Text('Safe', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600)),
          const SizedBox(width: 10),
          Container(
            width: 12,
            height: 6,
            decoration: BoxDecoration(
              color: AppTheme.riskOrange.withOpacity(0.4),
              border: Border.all(color: AppTheme.riskOrange),
            ),
          ),
          const SizedBox(width: 4),
          const Text('Flood', style: TextStyle(fontSize: 10, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _legendDot(Color c) {
    return Container(
      width: 10,
      height: 10,
      decoration: BoxDecoration(color: c, shape: BoxShape.circle),
    );
  }

  Widget _safeMarker() {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.safeGreen,
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(color: AppTheme.safeGreen.withOpacity(0.5), blurRadius: 12),
        ],
      ),
      child: const Icon(Icons.shield, color: Colors.white, size: 22),
    );
  }

  Widget _workerMarker() {
    final color = _statusColors[_currentStatus]!;
    return AnimatedBuilder(
      animation: _pulseController,
      builder: (context, _) {
        final scale = 1.0 + 0.18 * _pulseController.value;
        return Stack(
          alignment: Alignment.center,
          children: [
            Transform.scale(
              scale: scale,
              child: Container(
                decoration: BoxDecoration(
                  color: color.withOpacity(0.25),
                  shape: BoxShape.circle,
                ),
              ),
            ),
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                border: Border.all(color: color, width: 3),
                boxShadow: [
                  BoxShadow(color: color.withOpacity(0.4), blurRadius: 12),
                ],
              ),
              child: Icon(_statusIcons[_currentStatus], color: color, size: 18),
            ),
          ],
        );
      },
    );
  }

  Widget _mapBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(999),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 8),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.satellite_alt,
            size: 14,
            color: AppTheme.primaryBlue,
          ),
          const SizedBox(width: 6),
          Text(
            'Copernicus: $_copernicusRisk',
            style: const TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: AppTheme.darkText,
            ),
          ),
        ],
      ),
    );
  }

  Widget _mapButton(IconData icon, VoidCallback onTap, {Color? tint}) {
    return Material(
      color: Colors.white,
      shape: const CircleBorder(),
      elevation: 4,
      child: InkWell(
        customBorder: const CircleBorder(),
        onTap: onTap,
        child: SizedBox(
          width: 44,
          height: 44,
          child: Icon(icon, color: tint ?? AppTheme.darkText, size: 20),
        ),
      ),
    );
  }

  Widget _buildForecastCard() {
    final forecast = _currentForecast;
    final riskClass = forecast?['risk_class'] as String?;
    final score = (forecast?['risk_score'] as num?)?.toDouble();
    final drivers =
        (forecast?['drivers'] as Map?)?.cast<String, dynamic>() ?? const {};
    final precip48h = drivers['precip_mm_48h'] as num?;
    final efas = drivers['efas_probability'] as num?;
    final glofas = drivers['glofas_probability'] as num?;

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFE5E7EB)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: RiskStyle.color(riskClass).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    RiskStyle.icon(riskClass),
                    color: RiskStyle.color(riskClass),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _currentSiteName ?? 'No site selected',
                        style: const TextStyle(
                          fontWeight: FontWeight.w800,
                          fontSize: 15,
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                      Text(
                        forecast == null
                            ? 'Forecast loading…'
                            : '48h ${RiskStyle.label(riskClass)} · score ${(score ?? 0).toStringAsFixed(2)}',
                        style: TextStyle(
                          color: RiskStyle.color(riskClass),
                          fontWeight: FontWeight.w600,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.open_in_new, size: 20),
                  onPressed: () => Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const SiteListScreen()),
                  ),
                ),
              ],
            ),
            if (forecast != null) ...[
              const SizedBox(height: 12),
              ClipRRect(
                borderRadius: BorderRadius.circular(8),
                child: LinearProgressIndicator(
                  value: (score ?? 0).clamp(0.0, 1.0),
                  minHeight: 6,
                  backgroundColor: const Color(0xFFE5E7EB),
                  valueColor: AlwaysStoppedAnimation(
                    RiskStyle.color(riskClass),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _miniDriver('Precip 48h', precip48h, 'mm', 0),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _miniDriver(
                      'EFAS',
                      efas == null ? null : efas * 100,
                      '%',
                      0,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _miniDriver(
                      'GloFAS',
                      glofas == null ? null : glofas * 100,
                      '%',
                      0,
                    ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _miniDriver(String label, num? value, String unit, int decimals) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0xFFF3F4F6),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 11, color: AppTheme.lightText),
          ),
          const SizedBox(height: 2),
          Text(
            value == null ? '—' : '${value.toStringAsFixed(decimals)}$unit',
            style: const TextStyle(
              fontWeight: FontWeight.w700,
              fontSize: 14,
              color: AppTheme.darkText,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: Row(
        children: [
          Expanded(
            child: _actionTile(
              icon: Icons.medical_services,
              label: 'Test Man-Down',
              color: AppTheme.emergencyRed,
              onTap: () {
                _triggerManDown();
              },
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _actionTile(
              icon: Icons.health_and_safety,
              label: 'Mark Safe',
              color: AppTheme.safeGreen,
              onTap: () async {
                setState(() {
                  _currentStatus = 'Safe';
                  _demoState = DemoState.safe;
                  _activeAlertMessage = null;
                });
                await BackendService().postUserStatus(_workerPosition, 'Safe');
                await BackendService().cancelLatestAlert();
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _actionTile({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Material(
      color: color.withOpacity(0.10),
      borderRadius: BorderRadius.circular(14),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Column(
            children: [
              Icon(icon, color: color, size: 24),
              const SizedBox(height: 6),
              Text(
                label,
                style: TextStyle(
                  color: color,
                  fontWeight: FontWeight.w700,
                  fontSize: 13,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildManDownIndicator() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: AppTheme.emergencyRed.withOpacity(0.10),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: AppTheme.emergencyRed.withOpacity(0.4)),
        ),
        child: Row(
          children: [
            const Icon(
              Icons.warning_amber_rounded,
              color: AppTheme.emergencyRed,
              size: 32,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Movement watchdog',
                    style: TextStyle(
                      fontWeight: FontWeight.w700,
                      color: AppTheme.emergencyRed,
                    ),
                  ),
                  Text(
                    'Zero movement detected. SOS in $_manDownCountdown s.',
                    style: const TextStyle(
                      color: AppTheme.emergencyRed,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSafeLocations() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text(
                'NEARBY SAFE LOCATIONS',
                style: TextStyle(
                  fontSize: 11,
                  letterSpacing: 1.2,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.lightText,
                ),
              ),
              const Spacer(),
              if (_safeLocations.isNotEmpty)
                Text(
                  '${_safeLocations.length} found',
                  style: const TextStyle(fontSize: 11, color: AppTheme.lightText),
                ),
            ],
          ),
          const SizedBox(height: 8),
          if (_safeLocations.isEmpty)
            _safeLocationPlaceholder()
          else
            ..._safeLocations.take(4).map(_buildSafeLocationFromBackend),
        ],
      ),
    );
  }

  Widget _safeLocationPlaceholder() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE5E7EB)),
      ),
      child: const Row(
        children: [
          Icon(Icons.location_searching, color: AppTheme.lightText),
          SizedBox(width: 12),
          Expanded(
            child: Text(
              'Searching for shelters and assembly points within 10 km…',
              style: TextStyle(color: AppTheme.lightText, fontSize: 13),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSafeLocationFromBackend(Map<String, dynamic> location) {
    final type = (location['type'] as String?)?.toLowerCase() ?? '';
    final iconAndColor = _safeLocationIcon(type);
    final distance = _formatDistance(_distanceMeters(location));
    final capacity = location['capacity'] as int?;
    final occupancy = location['current_occupancy'] as int?;
    final status = location['status']?.toString();

    final subtitleParts = <String>[
      distance,
      if (type.isNotEmpty) type,
      if (capacity != null) 'cap. $capacity',
      if (occupancy != null && capacity != null && capacity > 0)
        '${(occupancy / capacity * 100).toStringAsFixed(0)}% full',
      if (status != null && status.isNotEmpty && status != 'active') status,
    ];

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: _safeLocationCard(
        icon: iconAndColor.$1,
        title: location['name']?.toString() ?? 'Safe location',
        subtitle: subtitleParts.join(' · '),
        color: iconAndColor.$2,
      ),
    );
  }

  (IconData, Color) _safeLocationIcon(String type) {
    if (type.contains('medical') || type.contains('hospital')) {
      return (Icons.local_hospital, AppTheme.primaryBlue);
    }
    if (type.contains('shelter')) {
      return (Icons.house, AppTheme.safeGreen);
    }
    if (type.contains('supplies') || type.contains('supply')) {
      return (Icons.inventory_2, AppTheme.monitorYellow);
    }
    if (type.contains('assembly')) {
      return (Icons.groups, AppTheme.safeGreen);
    }
    return (Icons.shield, AppTheme.safeGreen);
  }

  Widget _safeLocationCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE5E7EB)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: color),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.w700,
                    color: AppTheme.darkText,
                  ),
                ),
                Text(
                  subtitle,
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppTheme.lightText,
                  ),
                ),
              ],
            ),
          ),
          const Icon(Icons.navigation, color: AppTheme.lightText, size: 20),
        ],
      ),
    );
  }

  Widget _buildDrawer(BuildContext context) {
    return Drawer(
      backgroundColor: Colors.white,
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 20, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF1E3A8A), Color(0xFF2C74FF)],
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(Icons.water_drop, color: Colors.white),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'FloodGuard',
                    style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
                  ),
                  const Text(
                    'Industrial flood prediction',
                    style: TextStyle(color: AppTheme.lightText, fontSize: 12),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            _drawerTile(Icons.factory, 'Industrial Sites', () {
              Navigator.pop(context);
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SiteListScreen()),
              );
            }),
            _drawerTile(Icons.science_outlined, 'Demo Controls', () {
              Navigator.pop(context);
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const DemoControlsScreen()),
              );
            }),
            _drawerTile(Icons.person_outline, 'Profile Settings', () {
              Navigator.pop(context);
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const ProfileScreen()),
              );
            }),
            _drawerTile(Icons.contacts_outlined, 'Emergency Contacts', () {}),
            _drawerTile(Icons.tips_and_updates_outlined, 'Safety Tips', () {}),
            _drawerTile(Icons.info_outline, 'About', () {}),
            const Spacer(),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(
                'v0.1 · ${BackendService().userId ?? "demo"}',
                style: const TextStyle(color: AppTheme.lightText, fontSize: 11),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _drawerTile(IconData icon, String label, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon, color: AppTheme.darkText),
      title: Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
      onTap: onTap,
    );
  }
}
