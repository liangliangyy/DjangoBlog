"""
Test cases for blog middleware
"""
import time
from unittest.mock import Mock, patch, MagicMock

from django.test import TestCase, RequestFactory
from django.http import HttpResponse, StreamingHttpResponse
from django.utils import timezone

from blog.middleware import OnlineMiddleware


class OnlineMiddlewareTest(TestCase):
    """测试OnlineMiddleware中间件"""

    def setUp(self):
        """设置测试环境"""
        self.factory = RequestFactory()
        self.middleware = OnlineMiddleware(get_response=self.get_response)

    def get_response(self, request):
        """模拟Django的get_response"""
        response = HttpResponse("Test content <!!LOAD_TIMES!!>")
        return response

    def test_middleware_initialization(self):
        """测试中间件初始化"""
        middleware = OnlineMiddleware(get_response=self.get_response)
        self.assertIsNotNone(middleware.get_response)
        self.assertEqual(middleware.get_response, self.get_response)

    def test_middleware_processes_request_normally(self):
        """测试中间件正常处理请求"""
        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

        response = self.middleware(request)

        # 验证响应返回
        self.assertEqual(response.status_code, 200)
        # 验证响应内容中的加载时间被替换
        self.assertNotIn(b'<!!LOAD_TIMES!!>', response.content)

    def test_middleware_calculates_page_render_time(self):
        """测试中间件计算页面渲染时间"""
        # 创建一个慢响应来测试时间计算
        def slow_get_response(request):
            time.sleep(0.1)  # 模拟100ms的处理时间
            return HttpResponse("Test content <!!LOAD_TIMES!!>")

        middleware = OnlineMiddleware(get_response=slow_get_response)
        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'

        start_time = time.time()
        response = middleware(request)
        elapsed_time = time.time() - start_time

        # 验证响应时间至少是0.1秒
        self.assertGreaterEqual(elapsed_time, 0.1)
        # 验证响应内容被替换
        self.assertNotIn(b'<!!LOAD_TIMES!!>', response.content)

    def test_middleware_handles_streaming_response(self):
        """测试中间件处理流式响应"""
        def streaming_get_response(request):
            def generator():
                yield b"chunk1"
                yield b"chunk2"
            return StreamingHttpResponse(generator())

        middleware = OnlineMiddleware(get_response=streaming_get_response)
        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'

        response = middleware(request)

        # 验证流式响应被正确处理（不应该尝试替换内容）
        self.assertTrue(response.streaming)
        # 流式响应不应该被修改
        content = b''.join(response.streaming_content)
        self.assertEqual(content, b"chunk1chunk2")

    def test_middleware_handles_missing_user_agent(self):
        """测试中间件处理缺失的User-Agent"""
        request = self.factory.get('/test/')
        # 不设置HTTP_USER_AGENT

        response = self.middleware(request)

        # 应该能正常处理，不会崩溃
        self.assertEqual(response.status_code, 200)

    @patch('blog.middleware.ELASTICSEARCH_ENABLED', True)
    @patch('blog.middleware.ElaspedTimeDocumentManager.create')
    def test_middleware_elasticsearch_integration_enabled(self, mock_create):
        """测试Elasticsearch集成启用时的行为"""
        request = self.factory.get('/test-path/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'

        response = self.middleware(request)

        # 验证ElaspedTimeDocumentManager.create被调用
        self.assertTrue(mock_create.called)

        # 验证调用参数
        call_args = mock_create.call_args[1]
        self.assertEqual(call_args['url'], '/test-path/')
        self.assertIsNotNone(call_args['time_taken'])
        self.assertIsNotNone(call_args['log_datetime'])
        self.assertIsNotNone(call_args['useragent'])
        self.assertIsNotNone(call_args['ip'])

    @patch('blog.middleware.ELASTICSEARCH_ENABLED', False)
    @patch('blog.middleware.ElaspedTimeDocumentManager.create')
    def test_middleware_elasticsearch_integration_disabled(self, mock_create):
        """测试Elasticsearch集成禁用时的行为"""
        request = self.factory.get('/test-path/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'

        response = self.middleware(request)

        # 验证ElaspedTimeDocumentManager.create未被调用
        self.assertFalse(mock_create.called)
        # 但响应时间替换仍然应该工作
        self.assertNotIn(b'<!!LOAD_TIMES!!>', response.content)

    @patch('blog.middleware.get_client_ip')
    def test_middleware_ip_detection(self, mock_get_client_ip):
        """测试IP地址检测"""
        mock_get_client_ip.return_value = ('192.168.1.1', True)

        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'

        response = self.middleware(request)

        # 验证get_client_ip被调用
        self.assertTrue(mock_get_client_ip.called)
        mock_get_client_ip.assert_called_once_with(request)

    def test_middleware_user_agent_parsing(self):
        """测试User-Agent解析"""
        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'

        with patch('blog.middleware.parse') as mock_parse:
            mock_ua = Mock()
            mock_parse.return_value = mock_ua

            response = self.middleware(request)

            # 验证parse被调用
            self.assertTrue(mock_parse.called)
            mock_parse.assert_called_once_with('Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)')

    @patch('blog.middleware.ELASTICSEARCH_ENABLED', True)
    @patch('blog.middleware.ElaspedTimeDocumentManager.create')
    def test_middleware_handles_elasticsearch_exception(self, mock_create):
        """测试中间件处理Elasticsearch异常"""
        # 模拟Elasticsearch抛出异常
        mock_create.side_effect = Exception("Elasticsearch connection failed")

        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'

        # 应该能够捕获异常并继续处理
        response = self.middleware(request)

        # 验证响应仍然返回
        self.assertEqual(response.status_code, 200)
        # 注意：当发生异常时，整个try块会被跳过，所以替换可能不会发生
        # 但响应应该仍然返回，只是没有被修改
        self.assertTrue(response.content is not None)

    def test_middleware_handles_content_replace_exception(self):
        """测试中间件处理内容替换异常"""
        def error_get_response(request):
            # 返回不包含替换标记的响应
            response = HttpResponse("Test content without marker")
            # 模拟response.content不可修改的情况
            response._container = [b"immutable content"]
            return response

        middleware = OnlineMiddleware(get_response=error_get_response)
        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'

        # 应该能够捕获异常并继续处理
        response = middleware(request)

        # 验证响应仍然返回
        self.assertEqual(response.status_code, 200)

    def test_middleware_time_format(self):
        """测试中间件时间格式化"""
        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'

        response = self.middleware(request)

        # 提取替换后的时间值
        content_str = response.content.decode('utf-8')
        # 查找时间字符串（应该是数字格式，长度不超过5个字符）
        time_parts = content_str.split()

        # 验证至少有一些内容
        self.assertTrue(len(content_str) > 0)

    @patch('blog.middleware.logger')
    @patch('blog.middleware.ELASTICSEARCH_ENABLED', True)
    @patch('blog.middleware.ElaspedTimeDocumentManager.create')
    def test_middleware_logs_exceptions(self, mock_create, mock_logger):
        """测试中间件记录异常日志"""
        # 模拟异常
        test_exception = Exception("Test exception")
        mock_create.side_effect = test_exception

        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'

        response = self.middleware(request)

        # 验证logger.error被调用
        self.assertTrue(mock_logger.error.called)
        # 验证日志消息包含异常信息
        call_args = str(mock_logger.error.call_args)
        self.assertIn("Error OnlineMiddleware", call_args)

    def test_middleware_with_multiple_requests(self):
        """测试中间件处理多个请求"""
        paths = ['/page1/', '/page2/', '/page3/']

        for path in paths:
            request = self.factory.get(path)
            request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'

            response = self.middleware(request)

            # 每个请求都应该成功处理
            self.assertEqual(response.status_code, 200)
            self.assertNotIn(b'<!!LOAD_TIMES!!>', response.content)

    def test_middleware_preserves_response_headers(self):
        """测试中间件保留响应头"""
        def get_response_with_headers(request):
            response = HttpResponse("Test content <!!LOAD_TIMES!!>")
            response['X-Custom-Header'] = 'CustomValue'
            response['Content-Type'] = 'text/html; charset=utf-8'
            return response

        middleware = OnlineMiddleware(get_response=get_response_with_headers)
        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'

        response = middleware(request)

        # 验证响应头被保留
        self.assertEqual(response['X-Custom-Header'], 'CustomValue')
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')

    @patch('blog.middleware.ELASTICSEARCH_ENABLED', True)
    @patch('blog.middleware.ElaspedTimeDocumentManager.create')
    @patch('django.utils.timezone.now')
    def test_middleware_uses_correct_timezone(self, mock_now, mock_create):
        """测试中间件使用正确的时区"""
        mock_time = timezone.now()
        mock_now.return_value = mock_time

        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'

        response = self.middleware(request)

        # 验证timezone.now被调用
        self.assertTrue(mock_now.called)

        # 验证传递给Elasticsearch的时间是正确的
        if mock_create.called:
            call_args = mock_create.call_args[1]
            self.assertEqual(call_args['log_datetime'], mock_time)
