import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color primaryBlue = Color(0xFF3B82F6);
  static const Color darkText = Color(0xFF111827);
  static const Color lightText = Color(0xFF6B7280);
  static const Color background = Colors.white;
  static const Color inputBackground = Color(0xFFF3F4F6);
  
  static const Color safeGreen = Color(0xFF10B981);
  static const Color monitorYellow = Color(0xFFF59E0B);
  static const Color riskOrange = Color(0xFFF97316);
  static const Color emergencyRed = Color(0xFFEF4444);

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(
        seedColor: primaryBlue,
        background: background,
      ),
      textTheme: GoogleFonts.interTextTheme().copyWith(
        displayLarge: GoogleFonts.inter(color: darkText, fontWeight: FontWeight.bold),
        titleLarge: GoogleFonts.inter(color: darkText, fontWeight: FontWeight.w600),
        bodyLarge: GoogleFonts.inter(color: darkText),
        bodyMedium: GoogleFonts.inter(color: lightText),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF0F172A), // Dark color for buttons
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 50),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          textStyle: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: inputBackground,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: primaryBlue, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        hintStyle: const TextStyle(color: Color(0xFF9CA3AF)),
      ),
    );
  }
}
