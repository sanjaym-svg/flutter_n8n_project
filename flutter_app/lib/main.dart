import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

import 'core/api_client.dart';
import 'features/auth/auth_screens.dart';
import 'features/jobs/jobs_screens.dart';
import 'features/profile/profile_screen.dart';
import 'features/resume/resume_screen.dart';

const apiBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000');

final storageProvider = Provider((_) => const FlutterSecureStorage());
final tokenProvider = StateProvider<String?>((_) => null);
final apiProvider = Provider<ApiClient>((ref) => ApiClient(apiBaseUrl, token: ref.watch(tokenProvider)));

void main() {
  runApp(const ProviderScope(child: SmartApplyApp()));
}

class SmartApplyApp extends ConsumerWidget {
  const SmartApplyApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final token = ref.watch(tokenProvider);
    return MaterialApp(
      title: 'SmartApply',
      theme: ThemeData(useMaterial3: true, colorSchemeSeed: Colors.blue),
      home: token == null ? const LoginScreen() : const HomeShell(),
    );
  }
}

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int index = 0;
  @override
  Widget build(BuildContext context) {
    final pages = const [JobsFeedScreen(), ResumeScreen(), ProfileScreen()];
    return Scaffold(
      body: pages[index],
      bottomNavigationBar: NavigationBar(
        selectedIndex: index,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.work_outline), label: 'Jobs'),
          NavigationDestination(icon: Icon(Icons.description_outlined), label: 'Resume'),
          NavigationDestination(icon: Icon(Icons.person_outline), label: 'Profile'),
        ],
        onDestinationSelected: (i) => setState(() => index = i),
      ),
    );
  }
}
