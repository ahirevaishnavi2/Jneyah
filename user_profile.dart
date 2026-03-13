class UserProfile {
  String name;
  int age;
  String gender;
  List<String> allergies;
  String bloodGroup;
  bool isPregnant;
  String medicalHistory;

  UserProfile({
    this.name = '',
    this.age = 0,
    this.gender = '',
    this.allergies = const [],
    this.bloodGroup = '',
    this.isPregnant = false,
    this.medicalHistory = '',
  });
}
