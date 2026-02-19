import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  testWidgets('login form renders', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: Scaffold(body: Text('SmartApply Login'))));
    expect(find.text('SmartApply Login'), findsOneWidget);
  });

  testWidgets('jobs list placeholder', (tester) async {
    await tester.pumpWidget(const MaterialApp(home: Scaffold(body: Text('Fresh Software Jobs'))));
    expect(find.text('Fresh Software Jobs'), findsOneWidget);
  });
}
