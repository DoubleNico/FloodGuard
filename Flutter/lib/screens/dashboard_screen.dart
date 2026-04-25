import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'dart:async';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/backend_service.dart';
import 'alert_screen.dart';
import 'profile_screen.dart';

enum DemoState { safe, smsReceived, crisis, evacuation, reroute, manDown, sosTriggered }

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  String _currentStatus = 'Safe';
  DemoState _demoState = DemoState.safe;
  bool _showSmsBanner = false;
  final FlutterTts _flutterTts = FlutterTts();
  
  // Backend data
  String _copernicusRisk = 'LOADING...';
  String? _activeAlertMessage;
  StreamSubscription? _wsSubscription;
  Timer? _telemetryTimer;

  // Simulated movement state
  LatLng _workerPosition = const LatLng(45.4353, 28.0080);
  Timer? _movementTimer;
  Timer? _manDownTimer;
  int _manDownCountdown = 30;

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
    const LatLng(45.4400, 28.0150), // Assembly Point North
  ];

  @override
  void initState() {
    super.initState();
    _initTts();
    _initBackend();
  }

  Future<void> _initBackend() async {
    await BackendService().initialize();
    
    // Initial data fetch
    _fetchMapData();

    // Telemetry reporting
    _telemetryTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      BackendService().postUserStatus(_workerPosition, _currentStatus);
    });

    // Listen to WebSocket events from Dispatcher
    _wsSubscription = BackendService().eventStream.listen((data) {
      print("Dashboard received event: ${data['event']}");
      if (!mounted) return;
      final event = data['event'];
      
      // Update status from Web Dashboard
      if (event == 'user:status_update') {
        final payload = data['payload'];
        if (payload != null && payload['user_id'] == BackendService().userId) {
          setState(() {
            _currentStatus = payload['status'] ?? 'Safe';
          });
        }
      }

      if (event == 'alert:new' || event == 'alert:updated') {
        final payload = data['payload'];
        print("Alert payload type: ${payload?['type']}");
        if (payload != null && payload['type'] == 'evacuation') {
          _activeAlertMessage = payload['message'];
          if (_demoState == DemoState.safe || _demoState == DemoState.smsReceived) {
             print("TRIGGERING CRISIS from WebSocket!");
             // Dispatcher triggered an evacuation alert!
             setState(() {
               _demoState = DemoState.crisis;
             });
             _triggerCrisis();
          }
        }
      }
    });
  }

  Future<void> _fetchMapData() async {
    final data = await BackendService().fetchMapData(_workerPosition);
    if (data != null && mounted) {
      setState(() {
        if (data['flood_warning']?['copernicus']?['error'] == null) {
           _copernicusRisk = 'LOW RISK'; // Using LOW as placeholder since real Copernicus needs CDSE credentials
        } else {
           _copernicusRisk = 'LOW RISK (Mock)';
        }
      });
    }
  }

  Future<void> _initTts() async {
    await _flutterTts.setLanguage("en-US");
    await _flutterTts.setPitch(1.0);
  }

  @override
  void dispose() {
    _movementTimer?.cancel();
    _manDownTimer?.cancel();
    _telemetryTimer?.cancel();
    _wsSubscription?.cancel();
    super.dispose();
  }

  void _advanceDemo() async {
    setState(() {
      switch (_demoState) {
        case DemoState.safe:
          _demoState = DemoState.smsReceived;
          _showSmsBanner = true;
          Future.delayed(const Duration(seconds: 4), () {
            if (mounted) setState(() => _showSmsBanner = false);
          });
          break;
        case DemoState.smsReceived:
          _demoState = DemoState.crisis;
          _triggerCrisis();
          break;
        case DemoState.crisis:
          // Normally advances via AlertScreen
          break;
        case DemoState.evacuation:
          _demoState = DemoState.reroute;
          _triggerReroute();
          break;
        case DemoState.reroute:
          _demoState = DemoState.manDown;
          _triggerManDown();
          break;
        case DemoState.manDown:
          // SOS triggers automatically after 30s
          break;
        case DemoState.sosTriggered:
          // Reset
          _demoState = DemoState.safe;
          _workerPosition = const LatLng(45.4353, 28.0080);
          _currentStatus = 'Safe';
          break;
      }
    });
  }

  void _triggerCrisis() async {
    _currentStatus = 'Emergency';
    final startedEvac = await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const AlertScreen()),
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
        // Move worker slowly north-east
        _workerPosition = LatLng(
          _workerPosition.latitude + 0.0002,
          _workerPosition.longitude + 0.0002,
        );
      });
      
      // Auto-trigger reroute after 8 seconds of movement
      if (ticks == 8 && _demoState == DemoState.evacuation) {
        setState(() {
          _demoState = DemoState.reroute;
        });
        _triggerReroute();
      }
      
      // Auto-trigger man-down after 16 seconds (8 seconds after reroute)
      if (ticks == 16 && _demoState == DemoState.reroute) {
        setState(() {
          _demoState = DemoState.manDown;
        });
        _triggerManDown();
      }
    });
  }

  void _triggerReroute() {
    _flutterTts.speak("Route A flooded. Proceed to Assembly Point North via the elevated walkway.");
  }

  String? _currentAlertId;

  void _triggerManDown() async {
    _movementTimer?.cancel();
    setState(() {
      _demoState = DemoState.sosTriggered;
    });
    
    // Immediately send the SOS alert so it appears on the dashboard
    _currentAlertId = await _notifyManDown();
    
    // Show the dialog with the countdown
    _showSosDialog();
  }

  Future<String?> _notifyManDown() async {
    final prefs = await SharedPreferences.getInstance();
    final hasIssues = prefs.getBool('hasMobilityIssues') ?? false;
    final gravity = prefs.getString('mobilityGravity') ?? 'Low';

    final mobility = {
      "has_issues": hasIssues,
      "gravity": gravity,
      "level": gravity,
    };

    return await BackendService().triggerManDown(_workerPosition, mobilityInfo: mobility);
  }

  void _showSosDialog() {
    int countdown = 30;
    Timer? dialogTimer;
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            if (dialogTimer == null) {
              dialogTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
                if (mounted) {
                  setDialogState(() {
                    if (countdown > 0) {
                      countdown--;
                    } else {
                      timer.cancel();
                    }
                  });
                }
              });
            }

            return AlertDialog(
              backgroundColor: Colors.red[900],
              title: const Text('MAN-DOWN ALERT', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              content: Text(
                'Zero movement detected.\nAuto-SOS triggered. Precise coordinates sent to Dispatcher.\n\nTime remaining: $countdown seconds',
                style: const TextStyle(color: Colors.white),
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    dialogTimer?.cancel();
                    Navigator.pop(context);
                    if (mounted) {
                      setState(() {
                        _demoState = DemoState.safe;
                      });
                    }
                    BackendService().postUserStatus(_workerPosition, 'Safe');
                    if (_currentAlertId != null) {
                      BackendService().cancelAlert(_currentAlertId!);
                    }
                  },
                  child: const Text('I\'M FINE', style: TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold)),
                ),
                TextButton(
                  onPressed: () {
                    dialogTimer?.cancel();
                    Navigator.pop(context);
                    if (mounted) {
                      setState(() {
                        _demoState = DemoState.safe; // Reset for next demo run
                      });
                    }
                  },
                  child: const Text('DISMISS', style: TextStyle(color: Colors.white)),
                ),
              ],
            );
          },
        );
      },
    ).then((_) {
      dialogTimer?.cancel();
    });
  }

  final Map<String, Color> _statusColors = {
    'Safe': const Color(0xFF00C853),
    'Monitor': const Color(0xFFFF6D00),
    'Need Help': const Color(0xFFFFB300),
    'Emergency': const Color(0xFFD50000),
  };

  final Map<String, IconData> _statusIcons = {
    'Safe': Icons.check,
    'Monitor': Icons.bolt,
    'Need Help': Icons.warning_amber_rounded,
    'Emergency': Icons.campaign_outlined,
  };

  @override
  Widget build(BuildContext context) {
    Color activeColor = _statusColors[_currentStatus]!;
    IconData activeIcon = _statusIcons[_currentStatus]!;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Hydralis', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.error_outline),
            onPressed: () {},
          ),
        ],
      ),
      drawer: _buildDrawer(context),
      body: Column(
        children: [
          // Status Banner
          Container(
            color: activeColor,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(activeIcon, color: Colors.white),
                    const SizedBox(width: 8),
                    Text(
                      _currentStatus,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          
          // Active Alert Message Overlay
          if (_activeAlertMessage != null && (_demoState == DemoState.crisis || _demoState == DemoState.evacuation || _demoState == DemoState.reroute))
            Container(
              margin: const EdgeInsets.all(8),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.red.shade900,
                borderRadius: BorderRadius.circular(12),
                boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 8)],
              ),
              child: Row(
                children: [
                  const Icon(Icons.warning, color: Colors.white),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'DISPATCHER MESSAGE: $_activeAlertMessage',
                      style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white70, size: 20),
                    onPressed: () => setState(() => _activeAlertMessage = null),
                  )
                ],
              ),
            ),
          
          // SMS Banner Overlay Mock
          if (_showSmsBanner)
            Container(
              margin: const EdgeInsets.all(8),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.blue.shade900,
                borderRadius: BorderRadius.circular(12),
                boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 8)],
              ),
              child: Row(
                children: const [
                  Icon(Icons.message, color: Colors.white),
                  SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      'PRE-ALERT: Storm forecasted in 3 days. Prepare for potential evacuation.',
                      style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),

          // Scrollable Content
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Map Area
                  SizedBox(
                    height: 450,
                    child: Stack(
                      children: [
                        FlutterMap(
                          options: MapOptions(
                            initialCenter: const LatLng(45.4353, 28.0080),
                            initialZoom: 13.0,
                          ),
                          children: [
                            TileLayer(
                              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                              userAgentPackageName: 'com.hydralis.floodguard',
                            ),
                            if (_demoState == DemoState.evacuation || _demoState == DemoState.reroute || _demoState == DemoState.manDown)
                              PolylineLayer(
                                polylines: [
                                  if (_demoState == DemoState.evacuation)
                                    Polyline(
                                      points: _routeA,
                                      color: Colors.blue,
                                      strokeWidth: 5.0,
                                    ),
                                  if (_demoState == DemoState.reroute || _demoState == DemoState.manDown) ...[
                                    Polyline(
                                      points: _routeA,
                                      color: Colors.red,
                                      strokeWidth: 5.0,
                                    ),
                                    Polyline(
                                      points: _routeB,
                                      color: Colors.blue,
                                      strokeWidth: 5.0,
                                    ),
                                  ]
                                ],
                              ),
                            MarkerLayer(
                              markers: [
                                Marker(
                                  point: _workerPosition,
                                  width: 40,
                                  height: 40,
                                  child: Icon(
                                    Icons.person_pin_circle,
                                    color: activeColor,
                                    size: 40,
                                  ),
                                ),
                                Marker(
                                  point: const LatLng(45.4400, 28.0150),
                                  width: 40,
                                  height: 40,
                                  child: const Icon(
                                    Icons.location_on,
                                    color: Colors.green,
                                    size: 40,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                        // Overlay map data text
                        Positioned(
                          bottom: 8,
                          right: 8,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            color: Colors.white.withOpacity(0.7),
                            child: const Text(
                              'Map Data © FloodGuard',
                              style: TextStyle(fontSize: 12),
                            ),
                          ),
                        ),
                        // Overlay FAB
                        Positioned(
                          bottom: 30,
                          right: 16,
                          child: FloatingActionButton(
                            mini: true,
                            backgroundColor: const Color(0xFF000B2B),
                            child: const Icon(Icons.navigation, color: Colors.white, size: 20),
                            onPressed: () {},
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Passive Readiness Dashboard elements
                  if (_demoState == DemoState.safe || _demoState == DemoState.smsReceived)
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Column(
                        children: [
                          Row(
                            children: [
                              Expanded(
                                child: Container(
                                  padding: const EdgeInsets.all(16),
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(color: Colors.green.shade200, width: 2),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        children: const [
                                          Icon(Icons.satellite_alt, color: Colors.blue, size: 20),
                                          SizedBox(width: 8),
                                          Text('Copernicus', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                                        ],
                                      ),
                                      const SizedBox(height: 8),
                                      const Text('Site Risk Gauge', style: TextStyle(color: Colors.grey, fontSize: 12)),
                                      Text(_copernicusRisk, style: const TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 16)),
                                      const Text('10-day forecast', style: TextStyle(fontSize: 10, color: Colors.grey)),
                                    ],
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Container(
                                  padding: const EdgeInsets.all(16),
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    borderRadius: BorderRadius.circular(12),
                                    border: Border.all(color: Colors.blue.shade200, width: 2),
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        children: const [
                                          Icon(Icons.radar, color: Colors.blue, size: 20),
                                          SizedBox(width: 8),
                                          Text('Galileo+EGNOS', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                                        ],
                                      ),
                                      const SizedBox(height: 8),
                                      const Text('Precision Heartbeat', style: TextStyle(color: Colors.grey, fontSize: 12)),
                                      const Text('ACTIVE', style: TextStyle(color: Colors.blue, fontWeight: FontWeight.bold, fontSize: 16)),
                                      const Text('Within Geofence', style: TextStyle(fontSize: 10, color: Colors.grey)),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),

                  // Man Down Alert Indicator
                  if (_demoState == DemoState.manDown)
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: Colors.red.shade100,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: Colors.red, width: 2),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.warning_amber_rounded, color: Colors.red, size: 40),
                            const SizedBox(width: 16),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Text('Movement Watchdog', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.red)),
                                  Text('Zero movement detected. SOS in $_manDownCountdown seconds.', style: const TextStyle(color: Colors.red)),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                  Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Nearby Safe Locations (10km radius):',
                          style: TextStyle(fontSize: 16, color: Colors.black54),
                        ),
                        const SizedBox(height: 12),
                        Card(
                          color: const Color(0xFFF9F9F9),
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                            side: BorderSide(color: Colors.grey[300]!),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: ListTile(
                            leading: Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.green.withOpacity(0.1),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(Icons.security, color: Colors.green),
                            ),
                            title: const Text('City Hall Emergency Center', style: TextStyle(fontWeight: FontWeight.bold)),
                            trailing: const Icon(Icons.navigation, color: Colors.grey),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusCard(String text, IconData icon, Color iconColor, Color textColor) {
    bool isSelected = _currentStatus == text;
    return GestureDetector(
      onTap: () {
        setState(() {
          _currentStatus = text;
        });
      },
      child: Container(
        height: 90,
        decoration: BoxDecoration(
          color: isSelected ? iconColor : Colors.white,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isSelected ? iconColor : Colors.grey[300]!,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: isSelected ? Colors.white : iconColor, size: 32),
            const SizedBox(height: 8),
            Text(
              text,
              style: TextStyle(
                color: isSelected ? Colors.white : textColor,
                fontWeight: FontWeight.w600,
                fontSize: 12,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildDrawer(BuildContext context) {
    return Drawer(
      backgroundColor: Colors.white,
      shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero),
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
              child: Row(
                children: [
                  CircleAvatar(
                    radius: 30,
                    backgroundColor: Colors.blue,
                    child: const Icon(Icons.person_outline, color: Colors.white, size: 32),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: const [
                        Text('Andrei Ionescu', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        Text('andrei.ionescu@hydralis.com', style: TextStyle(color: Colors.grey)),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.black54),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            const SizedBox(height: 16),
            ListTile(
              title: const Text('Profile Settings', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const ProfileScreen()),
                );
              },
            ),
            ListTile(
              title: const Text('Emergency Contacts', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              onTap: () {},
            ),
            ListTile(
              title: const Text('Safety Tips', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              onTap: () {},
            ),
            ListTile(
              title: const Text('About', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
              onTap: () {},
            ),
            const Spacer(),
          ],
        ),
      ),
    );
  }
}
