import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme/app_theme.dart';

class ChatbotScreen extends StatefulWidget {
  @override
  _ChatbotScreenState createState() => _ChatbotScreenState();
}

class _ChatbotScreenState extends State<ChatbotScreen> {
  final List<Map<String, String>> _messages = [
    {"sender": "bot", "text": "Hi there! I'm JANDENY Buddy. How can I help you understand your product ingredients today?"},
  ];

  final TextEditingController _controller = TextEditingController();

  String _getBotResponse(String input) {
    input = input.toLowerCase();

    if (input.contains("hi") || input.contains("hello") || input.contains("hey")) {
      return "Hello! I am your Cosmetic Safety Assistant. I can help you check if ingredients are safe, identify your skin type, or suggest home remedies. How can I help you today?";
    } else if (input.contains("what do you do")) {
      return "I analyze cosmetic ingredients for safety and provide skincare tips based on your skin type. Just type an ingredient name or ask for a remedy!";
    } else if (input.contains("know my skin type") || input.contains("identify my skin type")) {
      return "Wash your face with a gentle cleanser, wait 30 minutes, and don't apply products. If it’s shiny all over, you're Oily; if it’s tight/flaky, you're Dry; if it's only shiny in the T-zone (forehead/nose), you're Combination.";
    } else if (input.contains("thank")) {
      return "You're very welcome! Stay glowing and stay safe. Is there anything else you'd like to check?";
    } else if (input.contains("tips for oily skin") || input.contains("oily skin tips")) {
      return "Stick to \"Non-Comedogenic\" (won't clog pores) products. Use a foaming cleanser, don't skip moisturizer (use a gel-based one), and look for ingredients like Niacinamide or Salicylic Acid.";
    } else if (input.contains("stop my face from getting shiny") || input.contains("shiny during the day")) {
      return "Use blotting papers to soak up oil without ruining makeup, and look for a \"Matte\" finish sunscreen or primer.";
    } else if (input.contains("use oil on oily skin")) {
      return "Yes, but only specific ones! Lightweight oils like Jojoba or Squalane can actually help balance your skin's natural oil production.";
    } else if (input.contains("treat combination skin") || input.contains("combination skin tips")) {
      return "Use \"Multi-masking\": apply a clay mask on your oily T-zone and a hydrating mask on your dry cheeks.";
    } else if (input.contains("oily but also dehydrated") || input.contains("oily and dehydrated")) {
      return "This happens when your skin barrier is damaged. You might be over-washing, causing your skin to produce extra oil to compensate for the lack of water.";
    } else if (input.contains("tips for dry skin") || input.contains("dry skin tips")) {
      return "Avoid harsh soaps. Use creamy cleansers and look for \"Humectants\" like Hyaluronic Acid and \"Occlusives\" like Shea Butter to lock in moisture.";
    } else if (input.contains("best for sensitive skin") || input.contains("sensitive skin tips")) {
      return "Less is more. Avoid \"Fragrance,\" \"Alcohol,\" and \"Sulfates.\" Always do a patch test on your neck before trying a new product.";
    } else if (input.contains("fix flaky skin") || input.contains("flaky skin")) {
      return "Don't scrub it! Use a very gentle chemical exfoliant like Lactic Acid and apply a thick moisturizer while your skin is still damp.";
    } else if (input.contains("home remedy for oily skin") || input.contains("remedy for acne")) {
      return "A Multani Mitti (Fuller's Earth) and Rose Water mask is excellent for absorbing excess oil and tightening pores.";
    } else if (input.contains("home remedy for dry skin") || input.contains("remedy for dry skin")) {
      return "Apply a thin layer of Honey for 15 minutes. It’s a natural humectant that draws moisture into the skin.";
    } else if (input.contains("dark circles naturally") || input.contains("rid of dark circles")) {
      return "Place chilled Cucumber slices or used Green Tea bags (caffeine helps) over your eyes for 10 minutes to reduce puffiness and brighten the area.";
    } else if (input.contains("remedy for glowing skin") || input.contains("natural glowing skin")) {
      return "Mix a pinch of Turmeric with Besan (Gram Flour) and yogurt. It brightens the skin and acts as a gentle cleanser.";
    } else if (input.contains("treat sunburn at home") || input.contains("sunburn")) {
      return "Apply fresh Aloe Vera gel. It cools the skin and reduces inflammation immediately.";
    } else if (input.contains("exfoliate naturally")) {
      return "Mix Fine Sugar with Coconut Oil for a gentle body scrub. For the face, use Oatmeal mixed with honey for a softer exfoliation.";
    } else if (input.contains("remedy for pigmentation") || input.contains("pigmentation")) {
      return "Potato juice or Lemon juice (diluted!) can help lighten spots over time due to their natural bleaching properties. Note: Always wear sunscreen after using lemon.";
    } else if (input.contains("home remedy for blackheads") || input.contains("blackheads")) {
      return "Use a Steam facial to open pores, then apply a paste of Baking Soda and water to the nose area for 5 minutes (rinse thoroughly).";
    }

    return "Based on my database, that ingredient can act as an irritant for sensitive skin profiles. Can I help you cross-reference another?";
  }

  void _sendMessage() {
    if (_controller.text.trim().isEmpty) return;
    
    String userText = _controller.text.trim();
    setState(() {
      _messages.add({"sender": "user", "text": userText});
    });
    
    // Simulate thinking delay
    Future.delayed(Duration(seconds: 1), () {
      setState(() {
        _messages.add({
          "sender": "bot", 
          "text": _getBotResponse(userText)
        });
      });
    });
    
    _controller.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Row(
          children: [
            CircleAvatar(
              backgroundColor: AppTheme.navyBlue.withOpacity(0.1),
              child: Icon(Icons.smart_toy_outlined, color: AppTheme.navyBlue),
            ),
            SizedBox(width: 12),
            Text("JANDENY Buddy", style: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: AppTheme.navyBlue)),
          ],
        ),
        centerTitle: false,
        elevation: 0,
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: EdgeInsets.all(20),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                final isUser = msg['sender'] == 'user';
                return Align(
                  alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: EdgeInsets.only(bottom: 20, left: isUser ? 50 : 0, right: isUser ? 0 : 50),
                    padding: EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: isUser ? AppTheme.navyBlue : Colors.white,
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(20),
                        topRight: Radius.circular(20),
                        bottomLeft: isUser ? Radius.circular(20) : Radius.circular(0),
                        bottomRight: isUser ? Radius.circular(0) : Radius.circular(20),
                      ),
                      boxShadow: [
                        if (!isUser) BoxShadow(color: AppTheme.navyBlue.withOpacity(0.05), blurRadius: 20, offset: Offset(0, 10))
                      ]
                    ),
                    child: Text(
                      msg['text']!, 
                      style: GoogleFonts.outfit(
                        color: isUser ? Colors.white : AppTheme.textPrimary,
                        fontSize: 16,
                      ),
                    ),
                  ).animate().fadeIn(duration: 400.ms).slideY(begin: 0.1, end: 0, curve: Curves.easeOut),
                );
              },
            ),
          ),
          Container(
            padding: EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            decoration: BoxDecoration(color: Colors.white, boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 10, offset: Offset(0, -2))]),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: InputDecoration(
                        hintText: "Ask about an ingredient...",
                        filled: true,
                        fillColor: AppTheme.background,
                        contentPadding: EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(30), borderSide: BorderSide.none),
                      ),
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),
                  SizedBox(width: 12),
                  CircleAvatar(
                    radius: 25,
                    backgroundColor: AppTheme.saffron,
                    child: IconButton(
                      icon: Icon(Icons.send, color: Colors.white),
                      onPressed: _sendMessage,
                    ),
                  )
                ],
              ),
            ),
          )
        ],
      ),
    );
  }
}
