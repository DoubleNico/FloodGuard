import 'dart:convert';
import 'dart:async';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:latlong2/latlong.dart';

class BackendService {
  static final BackendService _instance = BackendService._internal();
  factory BackendService() => _instance;
  BackendService._internal();

  final String baseUrl = 'http://10.0.2.2:8000/api';
  final String apiV1Url = 'http://10.0.2.2:8000/api/v1';
  final String wsUrl = 'ws://10.0.2.2:8000/api/v1/stream';

  String? _token;
  String? _userId;
  String? _userName;
  WebSocketChannel? _channel;

  // Stream controller to broadcast events from the WebSocket
  final _eventController = StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get eventStream => _eventController.stream;
  String? get userId => _userId;

  Future<void> initialize() async {
    await _authenticateDummyUser();
    _connectWebSocket();
  }

  Future<void> _authenticateDummyUser() async {
    final loginPayload = {
      "email": "andrei.ionescu@hydralis.com",
      "password": "secure_password"
    };

    try {
      // Try login first
      final loginRes = await http.post(
        Uri.parse('$baseUrl/auth/login'),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode(loginPayload),
      );

      if (loginRes.statusCode == 200) {
        final data = jsonDecode(loginRes.body);
        _token = data['token'];
        _userId = data['user']['user_id'];
        _userName = data['user']['full_name'];
      } else {
        // If login fails, try signup
        final signupPayload = {
          "full_name": "Andrei Ionescu",
          "email": "andrei.ionescu@hydralis.com",
          "password": "secure_password",
          "birthday": "1985-06-15",
          "primary_location": "Galati Port Facility",
          "safety_level": 3
        };

        final signupRes = await http.post(
          Uri.parse('$baseUrl/auth/signup'),
          headers: {"Content-Type": "application/json"},
          body: jsonEncode(signupPayload),
        );

        if (signupRes.statusCode == 201) {
          final data = jsonDecode(signupRes.body);
          _token = data['token'];
          _userId = data['user_id'];
          _userName = "Andrei Ionescu"; // Default for new signup in demo
        } else {
          print("Failed to authenticate dummy user: ${signupRes.body}");
        }
      }
    } catch (e) {
      print("Authentication error: $e");
    }
  }

  void _connectWebSocket() {
    print("Attempting to connect to WebSocket: $wsUrl");
    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _channel!.stream.listen(
        (message) {
          print("WebSocket RECEIVED: $message");
          try {
            final data = jsonDecode(message);
            _eventController.add(data);
          } catch (e) {
            print("WebSocket parse error: $e");
          }
        },
        onError: (e) {
          print("WebSocket ERROR: $e");
          _reconnectWebSocket();
        },
        onDone: () {
          print("WebSocket CLOSED");
          _reconnectWebSocket();
        },
      );
    } catch (e) {
      print("WebSocket connection error: $e");
      _reconnectWebSocket();
    }
  }

  void _reconnectWebSocket() {
    Future.delayed(const Duration(seconds: 5), () {
      _connectWebSocket();
    });
  }

  Future<Map<String, dynamic>?> fetchMapData(LatLng location) async {
    try {
      final res = await http.get(
        Uri.parse('$baseUrl/map/data?lat=${location.latitude}&lng=${location.longitude}&radius=10km'),
        headers: _token != null ? {"Authorization": "Bearer $_token"} : {},
      );

      if (res.statusCode == 200) {
        return jsonDecode(res.body);
      } else {
        print("Failed to fetch map data: ${res.body}");
        return null;
      }
    } catch (e) {
      print("Fetch map data error: $e");
      return null;
    }
  }

  Future<void> postUserStatus(LatLng location, String status) async {
    if (_userId == null) return;
    
    try {
      final payload = {
        "user_id": _userId,
        "status": status,
        "current_location": {
          "lat": location.latitude,
          "lng": location.longitude
        }
      };

      await http.post(
        Uri.parse('$baseUrl/user/status'),
        headers: {
          "Content-Type": "application/json",
          if (_token != null) "Authorization": "Bearer $_token"
        },
        body: jsonEncode(payload),
      );
    } catch (e) {
      print("Post user status error: $e");
    }
  }

  Future<String?> triggerManDown(
    LatLng location, {
    Map<String, dynamic>? mobilityInfo,
    String userStatus = "Man Down",
  }) async {
    if (_userId == null || _token == null) return null;

    try {
      final payload = {
        "user_id": _userId,
        "user_name": _userName ?? "Unknown Worker",
        "user_status": userStatus,
        "mobility_info": mobilityInfo,
        "current_location": {
          "lat": location.latitude,
          "lng": location.longitude
        },
        "message": "MAN-DOWN DETECTED: Zero movement for 60 seconds."
      };

      final response = await http.post(
        Uri.parse('$baseUrl/alerts/trigger'),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $_token"
        },
        body: jsonEncode(payload),
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['alert_id'];
      }
    } catch (e) {
      print("Trigger alert error: $e");
    }
    return null;
  }

  Future<void> cancelAlert(String alertId) async {
    try {
      // Mark the dispatch alert as accidental instead of closing it silently.
      await http.patch(
        Uri.parse('$apiV1Url/alerts/$alertId/message'),
        headers: {
          "Content-Type": "application/json",
          if (_token != null) "Authorization": "Bearer $_token",
        },
        body: jsonEncode({"message": "Accidental alert: worker confirmed safe from the mobile app."}),
      );
      await http.patch(
        Uri.parse('$apiV1Url/alerts/$alertId/status'),
        headers: {
          "Content-Type": "application/json",
          if (_token != null) "Authorization": "Bearer $_token",
        },
        body: jsonEncode({"status": "accidental"}),
      );
    } catch (e) {
      print("Cancel alert error: $e");
    }
  }

  Future<void> cancelLatestAlert() async {
    if (_token == null) return;

    try {
      await http.post(
        Uri.parse('$baseUrl/alerts/accidental'),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $_token",
        },
      );
    } catch (e) {
      print("Cancel latest alert error: $e");
    }
  }
}
