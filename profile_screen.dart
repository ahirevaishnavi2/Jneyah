import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../models/user_profile.dart';
import '../providers/user_provider.dart';
import '../theme/app_theme.dart';
import 'main_layout.dart';

class ProfileScreen extends StatefulWidget {
  @override
  _ProfileScreenState createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _nameController = TextEditingController();
  final _ageController = TextEditingController();
  final _allergiesController = TextEditingController();
  final _medicalHistoryController = TextEditingController();
  String _gender = 'Female';
  String _bloodGroup = 'A+';
  bool _isPregnant = false;

  final List<String> genders = ['Male', 'Female', 'Other'];
  final List<String> bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

  void _saveProfile() {
    final profile = UserProfile(
      name: _nameController.text,
      age: int.tryParse(_ageController.text) ?? 0,
      gender: _gender,
      allergies: _allergiesController.text.split(',').map((e) => e.trim()).where((e) => e.isNotEmpty).toList(),
      bloodGroup: _bloodGroup,
      isPregnant: _isPregnant,
      medicalHistory: _medicalHistoryController.text,
    );

    Provider.of<UserProvider>(context, listen: false).updateProfile(profile);
    Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => MainLayout()));
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 16.0),
      child: Text(
        title, 
        style: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.navyBlue)
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text("Medical Profile"),
        centerTitle: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text("Complete your health profile to get customized ingredient safety alerts.",
                 style: TextStyle(color: AppTheme.textSecondary, fontSize: 16)),
            SizedBox(height: 24),

            _buildSectionTitle("Basic Details"),
            TextField(
              controller: _nameController, 
              decoration: InputDecoration(labelText: "Full Name", prefixIcon: Icon(Icons.person, color: AppTheme.navyBlue)),
            ),
            SizedBox(height: 16),
            TextField(
              controller: _ageController, 
              decoration: InputDecoration(labelText: "Age", prefixIcon: Icon(Icons.calendar_today, color: AppTheme.navyBlue)), 
              keyboardType: TextInputType.number
            ),
            
            _buildSectionTitle("Gender & Blood"),
            Wrap(
              spacing: 12,
              children: genders.map((g) => ChoiceChip(
                label: Text(g),
                selected: _gender == g,
                onSelected: (selected) => setState(() => _gender = g),
                selectedColor: AppTheme.navyBlue,
                labelStyle: TextStyle(color: _gender == g ? Colors.white : AppTheme.textPrimary),
                backgroundColor: Colors.white,
              )).toList(),
            ),
            SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: bloodGroups.map((b) => ChoiceChip(
                label: Text(b),
                selected: _bloodGroup == b,
                onSelected: (selected) => setState(() => _bloodGroup = b),
                selectedColor: AppTheme.deepRed,
                labelStyle: TextStyle(color: _bloodGroup == b ? Colors.white : AppTheme.textPrimary),
                backgroundColor: Colors.white,
              )).toList(),
            ),

            if (_gender == 'Female') ...[
              SizedBox(height: 16),
              Container(
                decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(16)),
                child: SwitchListTile(
                  title: Text("Are you pregnant?", style: TextStyle(fontWeight: FontWeight.w600)),
                  subtitle: Text("Certain ingredients are not pregnancy-safe."),
                  value: _isPregnant,
                  activeColor: AppTheme.deepRed,
                  onChanged: (val) => setState(() => _isPregnant = val),
                ),
              ).animate().fade().slideY(),
            ],

            _buildSectionTitle("Medical Info"),
            TextField(
              controller: _medicalHistoryController, 
              decoration: InputDecoration(labelText: "Medical History (e.g. Sensitive Skin)"),
              maxLines: 2,
            ),
            SizedBox(height: 16),
            TextField(
              controller: _allergiesController, 
              decoration: InputDecoration(labelText: "Allergies (comma separated)"),
              maxLines: 2,
            ),
            
            SizedBox(height: 40),
            ElevatedButton(
              onPressed: _saveProfile,
              child: Center(child: Text("Save & Continue to Dashboard")),
            ).animate().fade(delay: 400.ms).slideY(begin: 0.2),
            SizedBox(height: 40),
          ],
        ),
      ),
    );
  }
}
