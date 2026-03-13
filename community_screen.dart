import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/app_theme.dart';

class CommunityScreen extends StatelessWidget {
  final List<Map<String, dynamic>> _discussions = [
    {
      "topic": "Skincare Addicts",
      "members": 1240,
      "lastActive": "2m ago",
      "tags": ["Acne", "Retinoids"],
      "color": Colors.blue
    },
    {
      "topic": "Packaged Foods Reality",
      "members": 3410,
      "lastActive": "15m ago",
      "tags": ["Preservatives", "Vegan"],
      "color": AppTheme.deepRed
    },
    {
      "topic": "Sensitive Skin Club",
      "members": 890,
      "lastActive": "1h ago",
      "tags": ["Allergies", "Fragrance-Free"],
      "color": Colors.orange
    },
    {
      "topic": "Pregnancy Safe Cosmetics",
      "members": 4500,
      "lastActive": "5h ago",
      "tags": ["Safe Ingredients"],
      "color": Colors.purple
    }
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text("JNEYAH Community", style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: AppTheme.navyBlue)),
        centerTitle: false,
        elevation: 0,
        actions: [
          IconButton(icon: Icon(Icons.search, color: AppTheme.navyBlue), onPressed: () {}),
          IconButton(icon: Icon(Icons.add_circle, color: AppTheme.saffron), onPressed: () {}),
        ],
      ),
      body: ListView.separated(
        padding: EdgeInsets.all(20),
        itemCount: _discussions.length,
        separatorBuilder: (_, __) => SizedBox(height: 16),
        itemBuilder: (context, index) {
          final room = _discussions[index];
          return GestureDetector(
            onTap: () {
              showModalBottomSheet(
                context: context,
                isScrollControlled: true,
                backgroundColor: Colors.transparent,
                builder: (context) => Container(
                  height: MediaQuery.of(context).size.height * 0.8,
                  padding: EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: AppTheme.background,
                    borderRadius: BorderRadius.vertical(top: Radius.circular(30))
                  ),
                  child: Column(
                    children: [
                      Container(width: 40, height: 5, decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(10))),
                      SizedBox(height: 20),
                      Row(
                        children: [
                          Icon(Icons.forum, color: room['color']),
                          SizedBox(width: 12),
                          Text(room['topic'], style: GoogleFonts.outfit(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.navyBlue)),
                        ],
                      ),
                      Divider(height: 30),
                      Expanded(
                        child: Center(
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.cloud_sync_outlined, size: 60, color: AppTheme.saffron.withOpacity(0.5)),
                              SizedBox(height: 16),
                              Text("Connected to Backend Server...", style: GoogleFonts.outfit(color: AppTheme.textSecondary, fontSize: 16)),
                              SizedBox(height: 8),
                              Text("Loading recent messages for ${room['topic']}", textAlign: TextAlign.center, style: GoogleFonts.outfit(color: AppTheme.navyBlue, fontSize: 14)),
                            ],
                          ).animate().fadeIn(duration: 800.ms).shimmer(delay: 400.ms),
                        )
                      ),
                      Container(
                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20), border: Border.all(color: Colors.grey.shade200)),
                        child: Row(
                          children: [
                            Expanded(child: Text("Type a message...", style: TextStyle(color: Colors.grey))),
                            Icon(Icons.send, color: AppTheme.saffron)
                          ],
                        ),
                      )
                    ],
                  ),
                )
              );
            },
            child: Container(
              padding: EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(24),
                boxShadow: [BoxShadow(color: AppTheme.navyBlue.withOpacity(0.04), blurRadius: 20, offset: Offset(0, 10))],
                border: Border.all(color: AppTheme.saffron.withOpacity(0.1), width: 1),
              ),
              child: Row(
                children: [
                  Container(
                    width: 50,
                    height: 50,
                    decoration: BoxDecoration(color: room['color'].withOpacity(0.1), shape: BoxShape.circle),
                    child: Icon(Icons.forum_outlined, color: room['color']),
                  ),
                  SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(room['topic'], style: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.bold, color: AppTheme.navyBlue)),
                        SizedBox(height: 4),
                        Text("${room['members']} members • Active ${room['lastActive']}", style: GoogleFonts.outfit(fontSize: 12, color: AppTheme.textSecondary)),
                        SizedBox(height: 8),
                        Row(
                          children: (room['tags'] as List).map((t) => Padding(
                            padding: const EdgeInsets.only(right: 8.0),
                            child: Container(
                              padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                              decoration: BoxDecoration(color: AppTheme.background, borderRadius: BorderRadius.circular(8)),
                              child: Text(t, style: GoogleFonts.outfit(fontSize: 10, color: AppTheme.saffron, fontWeight: FontWeight.w600)),
                            ),
                          )).toList(),
                        )
                      ],
                    ),
                  ),
                  Icon(Icons.chevron_right, color: AppTheme.saffron)
                ],
              ),
            ),
          ).animate().fadeIn(delay: Duration(milliseconds: 100 * index)).slideX(begin: 0.1, end: 0);
        },
      ),
    );
  }
}
