import twisted.internet
import twisted.internet.endpoints
import twisted.web.http
import twisted.web.proxy
import urllib.parse

class ReverseProxyHTTPFactory(twisted.web.http.HTTPFactory):
    def __init__(self, remote_url, *a, **kw):
        super().__init__(*a, **kw)

        self.remote_url = remote_url

    def protocol(self):
        return twisted.web.http._GenericHTTPChannelProtocol(ReverseProxy(self.remote_url))

class ReverseProxyRequest(twisted.web.proxy.ReverseProxyRequest):
    def process(self):
        self.requestHeaders.setRawHeaders(
            b"host",
            [self.channel.host.encode('ascii')],
        )

        clientFactory = self.proxyClientFactoryClass(
            self.method, self.uri, self.clientproto, self.getAllHeaders(),
            self.content.read(), self,
        )

        client_endpoint = twisted.internet.endpoints.clientFromString(
            twisted.internet.reactor,
            self.channel.client_conn_string,
        )

        client_endpoint.connect(clientFactory)

class ReverseProxy(twisted.web.proxy.ReverseProxy):
    requestFactory = ReverseProxyRequest

    def __init__(self, remote_url):
        super().__init__()

        url = urllib.parse.urlparse(remote_url)
        assert url.scheme in ('https', 'http')

        if ':' in url.netloc:
            self.host, self.proto = url.netloc.split(':')
        else:
            self.host = url.netloc
            self.port = {
                'http': 80,
                'https': 443,
            }[url.scheme]

        self.proto = {
            'http': 'tcp',
            'https': 'tls',
        }[url.scheme]

        self.client_conn_string = '{0.proto}:{0.host}:{0.port}'.format(self)
