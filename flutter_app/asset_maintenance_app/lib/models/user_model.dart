class User {
  final String username;
  final String email;
  final String fullName;
  final String role;
  final String branch;
  final String? token;
  final DateTime loginTime;

  User({
    required this.username,
    required this.email,
    required this.fullName,
    required this.role,
    required this.branch,
    this.token,
    required this.loginTime,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      username: json['user'] ?? '',
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? '',
      role: json['role'] ?? '',
      branch: json['branch'] ?? '',
      token: json['token'],
      loginTime: DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user': username,
      'email': email,
      'full_name': fullName,
      'role': role,
      'branch': branch,
      'token': token,
    };
  }

  User copyWith({
    String? username,
    String? email,
    String? fullName,
    String? role,
    String? branch,
    String? token,
  }) {
    return User(
      username: username ?? this.username,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      role: role ?? this.role,
      branch: branch ?? this.branch,
      token: token ?? this.token,
      loginTime: loginTime,
    );
  }
}
