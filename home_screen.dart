import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../providers/user_provider.dart';
import '../services/ocr_service.dart';
import '../services/safety_service.dart';
import '../theme/app_theme.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _manualInputController = TextEditingController();
  final IngredientSafetyService _safetyService = IngredientSafetyService();
  CameraController? _controller;
  bool _isAnalyzing = false;

  @override
  void initState() {
    super.initState();
    _safetyService.loadDatabase();
    _initCamera();
  }

  Future<void> _initCamera() async {
    final cameras = await availableCameras();
    if (cameras.isNotEmpty) {
      _controller = CameraController(cameras.first, ResolutionPreset.medium, imageFormatGroup: ImageFormatGroup.jpeg);
      await _controller!.initialize();
      if (mounted) setState(() {});
    }
  }

  void _analyze(List<String> ingredients) {
    setState(() => _isAnalyzing = false);
    if (ingredients.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("No ingredients provided")));
      return;
    }
    final profile = Provider.of<UserProvider>(context, listen: false).profile;
    if (profile == null) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text("Profile incomplete.")));
      return;
    }

    final result = _safetyService.checkSafety2(ingredients, profile);
    _showResult(result);
  }

  void _analyzeManual() {
    List<String> ingredients = _manualInputController.text.split(',').map((e) => e.trim()).where((e) => e.isNotEmpty).toList();
    _analyze(ingredients);
  }

  void _scanCamera() async {
    if (_controller == null || !_controller!.value.isInitialized) return;
    setState(() => _isAnalyzing = true);
    try {
      final image = await _controller!.takePicture();
      final ocrService = OCRService();
      final ingredients = await ocrService.processImage(image);
      _analyze(ingredients);
      ocrService.dispose();
    } catch (e) {
      print(e);
      setState(() => _isAnalyzing = false);
    }
  }

  void _showResult(SafetyResult result) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) {
        Color statusColor;
        IconData statusIcon;
        if (result.scale < 3) {
          statusColor = Colors.green.shade600;
          statusIcon = Icons.check_circle_outline;
        } else if (result.scale < 7) {
          statusColor = Colors.orange.shade700;
          statusIcon = Icons.warning_amber_rounded;
        } else {
          statusColor = AppTheme.deepRed;
          statusIcon = Icons.dangerous_outlined;
        }

        return Container(
          padding: EdgeInsets.all(32),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.vertical(top: Radius.circular(40)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(width: 40, height: 5, decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(10))),
              SizedBox(height: 30),
              Container(
                padding: EdgeInsets.all(20),
                decoration: BoxDecoration(color: statusColor.withOpacity(0.1), shape: BoxShape.circle),
                child: Icon(statusIcon, color: statusColor, size: 60),
              ).animate().scale(curve: Curves.easeOutBack, duration: 500.ms),
              SizedBox(height: 20),
              Text(
                result.status, 
                style: GoogleFonts.outfit(fontSize: 28, fontWeight: FontWeight.bold, color: statusColor)
              ),
              SizedBox(height: 8),
              Text(
                "Danger Scale: ${result.scale}/10", 
                style: GoogleFonts.outfit(fontSize: 16, fontWeight: FontWeight.w600, color: AppTheme.textSecondary)
              ),
              SizedBox(height: 20),
              Text(
                result.message, 
                textAlign: TextAlign.center, 
                style: GoogleFonts.outfit(fontSize: 18, color: AppTheme.textPrimary)
              ),
              SizedBox(height: 24),
              if (result.triggers.isNotEmpty)
                Container(
                  width: double.infinity,
                  padding: EdgeInsets.all(16),
                  decoration: BoxDecoration(color: Colors.red.shade50, borderRadius: BorderRadius.circular(16)),
                  child: Column(
                    children: [
                      Text("Problematic Ingredients:", style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: AppTheme.deepRed)),
                      SizedBox(height: 8),
                      Text(result.triggers.join(', '), textAlign: TextAlign.center, style: GoogleFonts.outfit(color: Colors.red.shade900, fontSize: 16)),
                    ],
                  ),
                ).animate().fade().slideY(),
              SizedBox(height: 40),
            ],
          ),
        );
      }
    );
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Row(
          children: [
            Icon(Icons.spa_rounded, color: AppTheme.saffron, size: 28), // Leaf-like logo icon
            SizedBox(width: 8),
            RichText(
              text: TextSpan(
                children: [
                  TextSpan(text: 'JNEYAH ', style: GoogleFonts.outfit(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.navyBlue)),
                  TextSpan(text: 'Scanner', style: GoogleFonts.outfit(fontSize: 20, color: AppTheme.saffron, fontWeight: FontWeight.w600)),
                ]
              )
            ),
          ],
        ),
        centerTitle: false,
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Camera Card
            Container(
              height: 350,
              decoration: BoxDecoration(
                color: Colors.black,
                borderRadius: BorderRadius.circular(32),
                boxShadow: [BoxShadow(color: AppTheme.navyBlue.withOpacity(0.15), blurRadius: 30, offset: Offset(0, 15))],
              ),
              clipBehavior: Clip.antiAlias,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  _controller != null && _controller!.value.isInitialized
                      ? Transform.scale(scale: 1.1, child: CameraPreview(_controller!))
                      : Center(child: CircularProgressIndicator(color: Colors.white)),
                  
                  // Scanning Overlay
                  if (_isAnalyzing)
                    Container(
                      color: Colors.black54,
                      child: Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            CircularProgressIndicator(color: Colors.white),
                            SizedBox(height: 16),
                            Text("Analyzing Ingredients...", style: GoogleFonts.outfit(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w600))
                          ],
                        ),
                      )
                    ),

                  // Button Overlay
                  Positioned(
                    bottom: 24,
                    left: 40,
                    right: 40,
                    child: ElevatedButton.icon(
                      onPressed: _isAnalyzing ? null : _scanCamera,
                      icon: Icon(Icons.camera_alt, size: 28),
                      label: Text("Scan Label", style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
                      style: ElevatedButton.styleFrom(
                        padding: EdgeInsets.symmetric(vertical: 18),
                        backgroundColor: AppTheme.saffron,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
                        elevation: 10,
                      ),
                    ).animate().shimmer(duration: 2000.ms, delay: 1000.ms).slideY(begin: 1, end: 0, curve: Curves.easeOutBack),
                  )
                ],
              ),
            ),
            
            SizedBox(height: 32),
            Row(
              children: [
                Expanded(child: Divider(color: Colors.grey.shade300)),
                Padding(padding: EdgeInsets.symmetric(horizontal: 16), child: Text("OR", style: GoogleFonts.outfit(color: AppTheme.textSecondary, fontWeight: FontWeight.w600))),
                Expanded(child: Divider(color: Colors.grey.shade300)),
              ],
            ),
            SizedBox(height: 32),

            // Manual Typist Card
            Container(
              padding: EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(32),
                border: Border.all(color: Colors.grey.shade200),
              ),
              child: Column(
                children: [
                  Text("Type Ingredients Manually", style: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.w600, color: AppTheme.navyBlue)),
                  SizedBox(height: 16),
                  TextField(
                    controller: _manualInputController,
                    maxLines: 3,
                    decoration: InputDecoration(
                      hintText: "E.g. Water, Parfum, Retinol...",
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(16)),
                    ),
                  ),
                  SizedBox(height: 20),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      icon: Icon(Icons.analytics_outlined),
                      label: Text("Analyze Typed List"),
                      onPressed: _analyzeManual,
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppTheme.navyBlue,
                        side: BorderSide(color: AppTheme.navyBlue, width: 2),
                        padding: EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        textStyle: GoogleFonts.outfit(fontSize: 16, fontWeight: FontWeight.bold)
                      ),
                    ),
                  )
                ],
              ),
            )
          ],
        ),
      ),
    );
  }
}
