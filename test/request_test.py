from restfulie.dsl import Dsl
from restfulie.request import Request
from mockito import mock

class callable_mock():
    
    def __init__(self):
        self.called = 0
    
    def __call__(self, *args, **kwargs):
        self.called = self.called + 1

class http_method_test:
    
    def setup(self):
        self.dsl = mock(Dsl)
        self.method = Request(self.dsl)

    def test_call_synchronous(self):
        self.dsl.callback = None
        self.method._process_flow = callable_mock()
        self.method()
        assert self.method._process_flow.called == 1
    
    def test_call_asynchronous(self):
        self.dsl.callback = self.test_call_synchronous
        self.method._process_async_flow = callable_mock()
        self.method()
        assert self.method._process_async_flow.called == 1