import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/app_theme.dart';
import 'profile_screen.dart';

class AuthScreen extends StatefulWidget {
  @override
  _AuthScreenState createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _nameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool isLogin = true;

  void _submit() {
    if (_nameController.text.isEmpty || _passwordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Please fill all fields', style: TextStyle(color: Colors.white)),
          backgroundColor: AppTheme.deepRed,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        )
      );
      return;
    }
    
    // Simulate auth & db connection
    Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => ProfileScreen()));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 28.0, vertical: 40.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(height: 40),
              // Modern Logo
              Column(
                children: [
                  Stack(
                    alignment: Alignment.center,
                    children: [
                      Icon(Icons.hub_outlined, size: 100, color: AppTheme.navyBlue.withOpacity(0.1)),
                      RichText(
                        text: TextSpan(
                          children: [
                            TextSpan(text: 'JNEY', style: GoogleFonts.outfit(fontSize: 60, fontWeight: FontWeight.bold, color: AppTheme.navyBlue, letterSpacing: 2)),
                            TextSpan(text: 'A', style: GoogleFonts.outfit(fontSize: 60, fontWeight: FontWeight.bold, color: AppTheme.deepRed, letterSpacing: 2)),
                            TextSpan(text: 'H', style: GoogleFonts.outfit(fontSize: 60, fontWeight: FontWeight.bold, color: AppTheme.navyBlue, letterSpacing: 2)),
                          ]
                        ),
                      ),
                    ],
                  ).animate().fade(duration: 800.ms).scale(curve: Curves.easeOutBack),
                  SizedBox(height: 10),
                  Text(
                    "WHERE TRUTH IS IDENTIFIED BEFORE BELIEF",
                    textAlign: TextAlign.center,
                    style: GoogleFonts.outfit(
                      fontSize: 12, 
                      fontWeight: FontWeight.w600, 
                      letterSpacing: 1.5,
                      color: AppTheme.navyBlue
                    ),
                  ).animate().fade(delay: 400.ms),
                ],
              ),
              SizedBox(height: 60),

              // Inputs Card
              Container(
                padding: EdgeInsets.all(28),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: [
                    BoxShadow(color: AppTheme.navyBlue.withOpacity(0.05), blurRadius: 20, offset: Offset(0, 10))
                  ]
                ),
                child: Column(
                  children: [
                    Text(
                      isLogin ? "Welcome Back" : "Create Account", 
                      style: GoogleFonts.outfit(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.navyBlue)
                    ),
                    SizedBox(height: 24),
                    TextField(
                      controller: _nameController,
                      decoration: InputDecoration(
                        labelText: "Username", 
                        prefixIcon: Icon(Icons.person_outline, color: AppTheme.navyBlue),
                      ),
                    ),
                    SizedBox(height: 16),
                    TextField(
                      controller: _passwordController,
                      decoration: InputDecoration(
                        labelText: "Password", 
                        prefixIcon: Icon(Icons.lock_outline, color: AppTheme.navyBlue),
                      ),
                      obscureText: true,
                    ),
                    SizedBox(height: 32),
                    ElevatedButton(
                      onPressed: _submit,
                      child: Center(child: Text(isLogin ? "Sign In" : "Sign Up")),
                    ),
                  ],
                ),
              ).animate().fade(delay: 600.ms).slideY(begin: 0.1, end: 0, curve: Curves.easeOut),
              
              SizedBox(height: 24),
              TextButton(
                onPressed: () => setState(() => isLogin = !isLogin),
                child: Text(
                  isLogin ? "Don't have an account? Sign Up" : "Already have an account? Sign In",
                  style: GoogleFonts.outfit(color: AppTheme.textSecondary, fontWeight: FontWeight.w600),
                ),
              ).animate().fade(delay: 800.ms)
            ],
          ),
        ),
      ),
    );
  }
}
