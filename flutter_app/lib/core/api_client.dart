import 'package:dio/dio.dart';

class ApiClient {
  ApiClient(this.baseUrl, {String? token}) {
    dio = Dio(BaseOptions(baseUrl: baseUrl, headers: token == null ? {} : {'Authorization': 'Bearer $token'}));
  }

  final String baseUrl;
  late Dio dio;

  Future<String> login(String email, String password) async {
    final res = await dio.post('/auth/login', data: {'email': email, 'password': password});
    return res.data['access_token'];
  }

  Future<String> register(String name, String email, String password) async {
    final res = await dio.post('/auth/register', data: {'name': name, 'email': email, 'password': password});
    return res.data['access_token'];
  }

  Future<List<dynamic>> jobs({int page = 1, bool remoteOnly = false, String? keyword}) async {
    final res = await dio.get('/jobs', queryParameters: {'page': page, 'remoteOnly': remoteOnly, 'keyword': keyword});
    return res.data['items'];
  }

  Future<void> syncJobs(Map<String, dynamic> filters) async {
    await dio.post('/jobs/sync', data: {'filters': filters});
  }

  Future<Map<String, dynamic>> jobDetail(int id) async {
    final res = await dio.get('/jobs/$id');
    return res.data;
  }

  Future<Map<String, dynamic>> tailor(int id) async {
    final res = await dio.post('/jobs/$id/tailor');
    return res.data;
  }
}
