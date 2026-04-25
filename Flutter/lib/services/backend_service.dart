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
  final String wsUrl = 'ws://10.0.2.2:8000/api/v1/stream';

  String? _token;
  String? _userId;
  WebSocketChannel? _channel;

  // Stream controller to broadcast events from the WebSocket
  final _eventController = StreamController<Map<String, dynamic>>.broadcast();
  Stream<Map<String, dynamic>> get eventStream => _eventController.stream;

  Future<void> initialize() async {
    await _authenticateDummyUser();
    _connectWebSocket();
  }

  Future<void> _authenticateDummyUser() async {
    final loginPayload = {
      "email": "dummy_worker@example.com",
      "password": "dummy_password"
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
      } else {
        // If login fails, try signup
        final signupPayload = {
          "full_name": "Dummy Worker",
          "email": "dummy_worker@example.com",
          "password": "dummy_password",
          "birthday": "1990-01-01",
          "primary_location": "Main Facility",
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

  Future<void> triggerManDown(LatLng location) async {
    if (_userId == null || _token == null) return;

    try {
      final payload = {
        "user_id": _userId,
        "current_location": {
          "lat": location.latitude,
          "lng": location.longitude
        },
        "message": "MAN-DOWN DETECTED: Zero movement for 60 seconds."
      };

      await http.post(
        Uri.parse('$baseUrl/alerts/trigger'),
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer $_token"
        },
        body: jsonEncode(payload),
      );
    } catch (e) {
      print("Trigger alert error: $e");
    }
  }
}
