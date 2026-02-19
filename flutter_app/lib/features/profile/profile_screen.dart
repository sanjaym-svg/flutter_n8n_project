import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../main.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    bool remoteOnly = true;
    String postedWithin = '72h';
    return Scaffold(
      appBar: AppBar(title: const Text('Profile & Settings')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Filters'),
          Wrap(spacing: 8, children: const [Chip(label: Text('Flutter')), Chip(label: Text('Backend')), Chip(label: Text('Python'))]),
          SwitchListTile(value: remoteOnly, onChanged: (_) {}, title: const Text('Remote only')),
          DropdownButtonFormField<String>(value: postedWithin, items: const [
            DropdownMenuItem(value: '24h', child: Text('24h')),
            DropdownMenuItem(value: '72h', child: Text('72h')),
            DropdownMenuItem(value: '7d', child: Text('7d')),
          ], onChanged: (_) {}, decoration: const InputDecoration(labelText: 'Posted within')),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () => ref.read(tokenProvider.notifier).state = null,
            child: const Text('Logout'),
          )
        ],
      ),
    );
  }
}
