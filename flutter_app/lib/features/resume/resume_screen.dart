import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

class ResumeScreen extends StatefulWidget {
  const ResumeScreen({super.key});

  @override
  State<ResumeScreen> createState() => _ResumeScreenState();
}

class _ResumeScreenState extends State<ResumeScreen> {
  String? fileName;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Master Resume')),
      body: Center(
        child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
          Text(fileName == null ? 'No resume uploaded yet' : 'Selected: $fileName'),
          const SizedBox(height: 12),
          ElevatedButton(
            onPressed: () async {
              final result = await FilePicker.platform.pickFiles(
                type: FileType.custom,
                allowedExtensions: ['pdf', 'docx'],
              );
              if (result != null) setState(() => fileName = result.files.single.name);
            },
            child: const Text('Upload / Replace Resume'),
          )
        ]),
      ),
    );
  }
}
