import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'alert_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  String _currentStatus = 'Safe';

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
        title: const Text('FloodGuard', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.error_outline),
            onPressed: () {},
          ),
        ],
        // The drawer icon will be added automatically by the Scaffold when a drawer is provided
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
                ElevatedButton(
                  onPressed: () {
                    // Optional: open a modal to change status, but since we have buttons below, this could just scroll down
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white.withOpacity(0.2),
                    foregroundColor: Colors.white,
                    elevation: 0,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  child: const Text('Change Status'),
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
                            MarkerLayer(
                              markers: [
                                Marker(
                                  point: const LatLng(45.4353, 28.0080),
                                  width: 40,
                                  height: 40,
                                  child: Icon(
                                    Icons.location_on,
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
                  Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Update Your Status:',
                          style: TextStyle(fontSize: 16, color: Colors.black54),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Expanded(child: _buildStatusCard('Safe', Icons.check, const Color(0xFF00C853), Colors.black87)),
                            const SizedBox(width: 8),
                            Expanded(child: _buildStatusCard('Monitor', Icons.bolt, const Color(0xFFFF6D00), Colors.black87)),
                            const SizedBox(width: 8),
                            Expanded(child: _buildStatusCard('Need Help', Icons.warning_amber_rounded, const Color(0xFFFFB300), Colors.black87)),
                            const SizedBox(width: 8),
                            Expanded(child: _buildStatusCard('Emergency', Icons.campaign_outlined, const Color(0xFFD50000), Colors.black87)),
                          ],
                        ),
                        const SizedBox(height: 24),
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
                        Text('John Doe', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        Text('john@example.com', style: TextStyle(color: Colors.grey)),
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
              onTap: () {},
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
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(context); // Close the drawer first
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const AlertScreen()),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFD50000), // Emergency Red
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 50),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text('Test Emergency Alert', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
