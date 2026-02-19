import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/models.dart';
import '../../main.dart';

final jobsProvider = FutureProvider.autoDispose<List<Job>>((ref) async {
  final items = await ref.read(apiProvider).jobs();
  return items.map((e) => Job.fromJson(e)).toList();
});

class JobsFeedScreen extends ConsumerWidget {
  const JobsFeedScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final jobsAsync = ref.watch(jobsProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('Fresh Software Jobs'),
        actions: [
          IconButton(
            onPressed: () async {
              await ref.read(apiProvider).syncJobs({
                'role_keywords': ['flutter', 'backend', 'python'],
                'location': 'remote',
                'remoteOnly': true,
                'postedWithinHours': 72,
              });
              ref.invalidate(jobsProvider);
            },
            icon: const Icon(Icons.sync),
          )
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => ref.invalidate(jobsProvider),
        child: jobsAsync.when(
          data: (jobs) => jobs.isEmpty
              ? const Center(child: Text('No jobs found. Sync to fetch new roles.'))
              : ListView.builder(
                  itemCount: jobs.length,
                  itemBuilder: (_, i) {
                    final j = jobs[i];
                    return ListTile(
                      title: Text(j.title),
                      subtitle: Text('${j.company} • ${j.location}'),
                      onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => JobDetailScreen(job: j))),
                    );
                  },
                ),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (e, _) => Center(child: Text('Error: $e')),
        ),
      ),
    );
  }
}

class JobDetailScreen extends ConsumerStatefulWidget {
  const JobDetailScreen({super.key, required this.job});
  final Job job;

  @override
  ConsumerState<JobDetailScreen> createState() => _JobDetailScreenState();
}

class _JobDetailScreenState extends ConsumerState<JobDetailScreen> {
  Map<String, dynamic>? tailored;

  @override
  Widget build(BuildContext context) {
    final j = widget.job;
    return Scaffold(
      appBar: AppBar(title: Text(j.title)),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: ListView(children: [
          Text(j.company, style: Theme.of(context).textTheme.titleMedium),
          Text(j.location),
          const SizedBox(height: 12),
          Text(j.description),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => launchUrl(Uri.parse(j.applyUrl), mode: LaunchMode.externalApplication),
            child: const Text('Open Apply Link'),
          ),
          ElevatedButton(
            onPressed: () async {
              final data = await ref.read(apiProvider).tailor(j.id);
              setState(() => tailored = data);
            },
            child: const Text('Generate ATS Resume'),
          ),
          if (tailored != null) ...[
            Text('ATS Score: ${tailored!['ats_score']}'),
            Text('Matched: ${(tailored!['matched_keywords'] as List).join(', ')}'),
            Text('Missing: ${(tailored!['missing_keywords'] as List).join(', ')}'),
          ]
        ]),
      ),
    );
  }
}
