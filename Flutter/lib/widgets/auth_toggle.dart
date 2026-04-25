import 'package:flutter/material.dart';

class AuthToggle extends StatelessWidget {
  final bool isLogin;
  final VoidCallback onLoginPressed;
  final VoidCallback onSignUpPressed;

  const AuthToggle({
    super.key,
    required this.isLogin,
    required this.onLoginPressed,
    required this.onSignUpPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE0E0E0)),
      ),
      child: Row(
        children: [
          Expanded(
            child: GestureDetector(
              onTap: onLoginPressed,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: isLogin ? const Color(0xFF000B2B) : Colors.transparent,
                  borderRadius: const BorderRadius.horizontal(left: Radius.circular(7)),
                ),
                child: Center(
                  child: Text(
                    'Login',
                    style: TextStyle(
                      color: isLogin ? Colors.white : Colors.black87,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            ),
          ),
          Expanded(
            child: GestureDetector(
              onTap: onSignUpPressed,
              child: Container(
                padding: const EdgeInsets.symmetric(vertical: 12),
                decoration: BoxDecoration(
                  color: !isLogin ? const Color(0xFF000B2B) : Colors.transparent,
                  borderRadius: const BorderRadius.horizontal(right: Radius.circular(7)),
                ),
                child: Center(
                  child: Text(
                    'Sign Up',
                    style: TextStyle(
                      color: !isLogin ? Colors.white : Colors.black87,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
