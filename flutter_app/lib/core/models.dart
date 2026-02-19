class Job {
  final int id;
  final String title;
  final String company;
  final String location;
  final String description;
  final String applyUrl;
  final int? atsScore;

  Job({
    required this.id,
    required this.title,
    required this.company,
    required this.location,
    required this.description,
    required this.applyUrl,
    this.atsScore,
  });

  factory Job.fromJson(Map<String, dynamic> json) => Job(
        id: json['id'],
        title: json['title'],
        company: json['company'],
        location: json['location'],
        description: json['description'],
        applyUrl: json['apply_url'],
      );
}
